import os
import sys
from scAutoPipeline.tools.utils import ModuleFun
from scAutoPipeline.config.config import DATABASE
from scAutoPipeline.tools.M1.utils import scan_fastq_directory


class DNBC4tools(ModuleFun):
    def __init__(
        self,
        data: dict,
        analysis: str,
        input: str,
    ):
        super().__init__(data, input, analysis)

    def init_param(self):
        if self.refgenome == None:
            self.refgenome = DATABASE["refgenome"][self.species][self.analysis][
                "index_path"
            ]
        if self.data["param"]["forcecell"] != None:
            self.forcecell = f"--forcecell {self.data['param']['forcecell']}"
        else:
            self.forcecell = ""

    def shell_script(self, name, cDNAfastq1, cDNAfastq2, oligofastq1, oligofastq2):
        shell_script_content = f"""#!/bin/bash

set -euo pipefail

SAMPLE_NAME="{name}"
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
START_TIMESTAMP=$(date +%s)
OUTPUT_DIR="{self.outdir}/DNBC4tools"

{self.script} rna run \\
    --name ${{SAMPLE_NAME}} \\
    --cDNAfastq1 {cDNAfastq1} \\
    --cDNAfastq2 {cDNAfastq2} \\
    --oligofastq1 {oligofastq1} \\
    --oligofastq2 {oligofastq2} \\
    --genomeDir {self.refgenome} \\
    --outdir ${{OUTPUT_DIR}} \\
    --threads {self.thread} \\
    --calling_method emptydrops \\
    --expectcells 3000 \\
    --chemistry auto {self.forcecell}

# Generate info.csv
INPUT_PATH="${{OUTPUT_DIR}}/${{SAMPLE_NAME}}"
FEATURE_MATRIX_PATH="${{INPUT_PATH}}/outs/filtered_feature_bc_matrix"
OUTPUT_FILE="${{INPUT_PATH}}/info.csv"

echo "sampleid,path,group,sampleid_order,datatype" > "$OUTPUT_FILE"
echo "${{SAMPLE_NAME}},$FEATURE_MATRIX_PATH,${{SAMPLE_NAME}},1,mtx-c4" >> "$OUTPUT_FILE"
















END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
END_TIMESTAMP=$(date +%s)
ELAPSED_TIME=$((END_TIMESTAMP - START_TIMESTAMP))

if [ -d "${{OUTPUT_DIR}}/${{SAMPLE_NAME}}" ]; then
    echo "[CHECK] Output directory exists: ${{OUTPUT_DIR}}/${{SAMPLE_NAME}}"
else
    echo "[WARNING] Output directory NOT found! Analysis may have failed. Check log: " >&2
    exit 1
fi

LOG_FILE="/nas/database/scAutoPipeline/task_logs.csv"
if [ ! -f "$LOG_FILE" ]; then
    echo "Project,Analysis,StartTime,EndTime,TotalElapsedTime(min),Threads,outdir" > "$LOG_FILE"
fi

echo "\"{self.data['programID']}\",\"{self.analysis}\",\"${{START_TIME}}\",\"${{END_TIME}}\",\"$(( (END_TIMESTAMP - START_TIMESTAMP) / 60 ))\",\"{self.thread}\",\"${{OUTPUT_DIR}}/${{SAMPLE_NAME}}\"" >> "$LOG_FILE"

"""
        self.save_script(shell_script_content)

    def run(self):
        self.init_param()
        dict = scan_fastq_directory(self.input)
        for sample, files in dict.items():
            self.prefix = sample
            self.shell_script(
                name=sample,
                cDNAfastq1=files["cDNAfastq1"],
                cDNAfastq2=files["cDNAfastq2"],
                oligofastq1=files["oligofastq1"],
                oligofastq2=files["oligofastq2"],
            )
