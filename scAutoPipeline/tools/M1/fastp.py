import os
import sys
from scAutoPipeline.tools.utils import ModuleFun


class Fastp(ModuleFun):
    def __init__(
        self,
        data: dict,
        analysis: str,
        input: str,
        type: str,
    ):
        super().__init__(data, input, analysis)
        self.type = type

    def init_param(self):
        self.outdir = os.path.join(
            self.outdir,
            self.type,
            self.analysis,
        )

    def shell_script(self):
        shell_script_content = f"""#!/bin/bash

set -euo pipefail

# Fastp quality control script for samples with multiple lanes
# This script merges all R1 files and all R2 files before running fastp

# Parse arguments
SAMPLE_NAME="{self.type}"
INPUT_DIR="{self.input}/${{SAMPLE_NAME}}"
OUTPUT_DIR="{self.outdir}"
THREADS="{self.thread}"

echo "=== Fastp Quality Control for Sample: ${{SAMPLE_NAME}} ==="
echo "Input directory: ${{INPUT_DIR}}"
echo "Output directory: ${{OUTPUT_DIR}}"
echo "Threads: ${{THREADS}}"
echo "Sample name: ${{SAMPLE_NAME}}"
echo ""

# Define report file names
REPORT_HTML="${{OUTPUT_DIR}}/report.html"
REPORT_JSON="${{OUTPUT_DIR}}/summary.json"

# Temporary files (will be deleted)
MERGED_R1="${{OUTPUT_DIR}}/.${{SAMPLE_NAME}}_merged_R1.fastq.gz"
MERGED_R2="${{OUTPUT_DIR}}/.${{SAMPLE_NAME}}_merged_R2.fastq.gz"
TMP_OUT1="${{OUTPUT_DIR}}/.${{SAMPLE_NAME}}_tmp_r1.fq.gz"
TMP_OUT2="${{OUTPUT_DIR}}/.${{SAMPLE_NAME}}_tmp_r2.fq.gz"

# Ensure output directory exists
mkdir -p "${{OUTPUT_DIR}}"

# Find all R1 and R2 files in the input directory
# Pattern: sample_L*_R1_*.fastq.gz and sample_L*_R2_*.fastq.gz
R1_FILES=($(ls "${{INPUT_DIR}}/${{SAMPLE_NAME}}"_*_R1_*.fastq.gz 2>/dev/null | sort))
R2_FILES=($(ls "${{INPUT_DIR}}/${{SAMPLE_NAME}}"_*_R2_*.fastq.gz 2>/dev/null | sort))

# Check if files were found
R1_COUNT=$(ls "${{INPUT_DIR}}/${{SAMPLE_NAME}}"_*_R1_*.fastq.gz 2>/dev/null | wc -l)
R2_COUNT=$(ls "${{INPUT_DIR}}/${{SAMPLE_NAME}}"_*_R2_*.fastq.gz 2>/dev/null | wc -l)

if [ $R1_COUNT -eq 0 ]; then
    echo "❌ Error: No R1 files found in ${{INPUT_DIR}}"
    echo "Expected pattern: ${{SAMPLE_NAME}}_*_R1_*.fastq.gz"
    exit 1
fi

if [ $R2_COUNT -eq 0 ]; then
    echo "❌ Error: No R2 files found in ${{INPUT_DIR}}"
    echo "Expected pattern: ${{SAMPLE_NAME}}_*_R2_*.fastq.gz"
    exit 1
fi

if [ $R1_COUNT -ne $R2_COUNT ]; then
    echo "⚠️ Warning: Number of R1 files ($R1_COUNT) does not match number of R2 files ($R2_COUNT)"
fi

# Display files to process
echo "Found $R1_COUNT R1 files:"
for file in "${{R1_FILES[@]}}"; do
    if [ -f "$file" ]; then
        echo "  - $(basename "$file") ($(ls -lh "$file" | awk '{{print $5}}'))"
    else
        echo "  ❌ ERROR: File not found: $file"
        exit 1
    fi
done

echo ""
echo "Found $R2_COUNT R2 files:"
for file in "${{R2_FILES[@]}}"; do
    if [ -f "$file" ]; then
        echo "  - $(basename "$file") ($(ls -lh "$file" | awk '{{print $5}}'))"
    else
        echo "  ❌ ERROR: File not found: $file"
        exit 1
    fi
done

# Extract lane information for report
LANES=()
for file in "${{R1_FILES[@]}}"; do
    # Extract lane number from filename (e.g., L001 from sample_L001_R1_001.fastq.gz)
    lane=$(basename "$file" | grep -o 'L[0-9][0-9][0-9]' | head -1)
    if [ -n "$lane" ]; then
        LANES+=("$lane")
    fi
done

LANE_INFO=""
# Get lane count using a different method
LANE_COUNT=0
for file in "${{R1_FILES[@]}}"; do
    LANE_COUNT=$((LANE_COUNT + 1))
done

if [ $LANE_COUNT -gt 0 ]; then
    # Extract lane numbers
    LANE_NUMBERS=()
    for file in "${{R1_FILES[@]}}"; do
        lane=$(basename "$file" | grep -o 'L[0-9][0-9][0-9]' | head -1)
        if [ -n "$lane" ]; then
            LANE_NUMBERS+=("$lane")
        fi
    done
    LANE_NUMBERS_COUNT=0
    for file in "${{R1_FILES[@]}}"; do
        lane=$(basename "$file" | grep -o 'L[0-9][0-9][0-9]' | head -1)
        if [ -n "$lane" ]; then
            LANE_NUMBERS_COUNT=$((LANE_NUMBERS_COUNT + 1))
        fi
    done
    
    if [ $LANE_NUMBERS_COUNT -gt 0 ]; then
        # Create lane info string
        LANE_STR=""
        for file in "${{R1_FILES[@]}}"; do
            lane=$(basename "$file" | grep -o 'L[0-9][0-9][0-9]' | head -1)
            if [ -n "$lane" ]; then
                if [ -z "$LANE_STR" ]; then
                    LANE_STR="$lane"
                else
                    LANE_STR="$LANE_STR+$lane"
                fi
            fi
        done
        LANE_INFO="$LANE_STR"
    else
        LANE_INFO="$LANE_COUNT lanes"
    fi
else
    LANE_INFO="all lanes"
fi

echo ""
echo "=== Processing Steps ==="

# Merge R1 files
echo "1. Merging R1 files..."
cat "${{R1_FILES[@]}}" > "${{MERGED_R1}}"
if [ $? -eq 0 ]; then
    echo "   ✅ R1 files merged: $(basename "${{MERGED_R1}}") ($(ls -lh "${{MERGED_R1}}" | awk '{{print $5}}'))"
else
    echo "   ❌ Failed to merge R1 files"
    exit 1
fi

# Merge R2 files
echo "2. Merging R2 files..."
cat "${{R2_FILES[@]}}" > "${{MERGED_R2}}"
if [ $? -eq 0 ]; then
    echo "   ✅ R2 files merged: $(basename "${{MERGED_R2}}") ($(ls -lh "${{MERGED_R2}}" | awk '{{print $5}}'))"
else
    echo "   ❌ Failed to merge R2 files"
    exit 1
fi

# Run fastp on merged files
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
START_TIMESTAMP=$(date +%s)
echo "3. Running fastp quality control..."
echo "   Command: fastp --in1 ${{MERGED_R1}} --in2 ${{MERGED_R2}} --thread ${{THREADS}}"
echo "   Report title: ${{SAMPLE_NAME}} Sample (Lanes: ${{LANE_INFO}}) PE Fastp QC Report"

{self.script} \\
  --in1 "${{MERGED_R1}}" \\
  --in2 "${{MERGED_R2}}" \\
  --out1 "${{TMP_OUT1}}" \\
  --out2 "${{TMP_OUT2}}" \\
  --html "${{REPORT_HTML}}" \\
  --json "${{REPORT_JSON}}" \\
  --disable_quality_filtering \\
  --disable_length_filtering \\
  --disable_adapter_trimming \\
  --disable_trim_poly_g \\
  --dont_eval_duplication \\
  --report_title "${{SAMPLE_NAME}} Sample (Lanes: ${{LANE_INFO}}) PE Fastp QC Report" \\
  --thread "${{THREADS}}"

FASTP_EXIT_CODE=$?

# Clean up temporary files
echo "4. Cleaning up temporary files..."
rm -f "${{MERGED_R1}}" "${{MERGED_R2}}" "${{TMP_OUT1}}" "${{TMP_OUT2}}"

# Verify results
echo ""
echo "=== Results ==="
if [ ${{FASTP_EXIT_CODE}} -eq 0 ] && [ -f "${{REPORT_HTML}}" ] && [ -f "${{REPORT_JSON}}" ]; then
    echo "✅✅✅ SUCCESS: Fastp quality control completed! ✅✅✅"
    echo ""
    echo "Generated reports:"
    echo "  HTML: ${{REPORT_HTML}}"
    echo "  JSON: ${{REPORT_JSON}}"
    echo ""
    echo "Processing summary:"
    echo "  Sample: ${{SAMPLE_NAME}}"
    echo "  Lanes processed: ${{LANE_INFO}}"
    echo "  Total R1 files: $R1_COUNT"
    echo "  Total R2 files: $R2_COUNT"
    echo "  Threads used: ${{THREADS}}"
    echo ""
    echo "To view the report, open:"
    echo "  ${{REPORT_HTML}}"
else
    echo "❌❌❌ FAILURE: Fastp quality control failed! ❌❌❌"
    echo ""
    echo "Exit code: ${{FASTP_EXIT_CODE}}"
    echo "Report files:"
    echo "  HTML: ${{REPORT_HTML}} ($([ -f "${{REPORT_HTML}}" ] && echo "Exists" || echo "Missing"))"
    echo "  JSON: ${{REPORT_JSON}} ($([ -f "${{REPORT_JSON}}" ] && echo "Exists" || echo "Missing"))"
    echo ""
    echo "Possible issues:"
    echo "  1. Input files may be corrupted"
    echo "  2. Insufficient disk space"
    echo "  3. Permission issues"
    echo "  4. fastp software problem"
    exit 1
fi
"""
        self.save_script(shell_script_content)

    def run(self):
        self.init_param()
        self.prefix = f"{self.prefix}_{self.type}"
        self.shell_script()
