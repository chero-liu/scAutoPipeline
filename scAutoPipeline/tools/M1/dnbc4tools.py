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




















END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
END_TIMESTAMP=$(date +%s)
ELAPSED_TIME=$((END_TIMESTAMP - START_TIMESTAMP))
ELAPSED_HOURS=$((ELAPSED_TIME / 3600))
ELAPSED_MINUTES=$(((ELAPSED_TIME % 3600) / 60))
ELAPSED_SECONDS=$((ELAPSED_TIME % 60))

if [ -d "${{OUTPUT_DIR}}/${{SAMPLE_NAME}}" ]; then
    echo "[CHECK] Output directory exists: ${{OUTPUT_DIR}}/${{SAMPLE_NAME}}"
else
    echo "[WARNING] Output directory NOT found! Analysis may have failed. Check log: " >&2
    exit 1
fi

# Parameters explanation:
#   --name:          样本唯一标识（自定义），示例：KSXY-TJQK-DO25112701-1
#   --cDNAfastq1/2:  cDNA文库R1/R2原始FASTQ文件路径（支持多个文件逗号分隔）
#   --oligofastq1/2: Oligo文库（条码文库）R1/R2原始FASTQ文件路径
#   --genomeDir:     参考基因组索引目录（需包含完整scStar索引）
#   --outdir:        结果输出根目录（最终结果在 {self.outdir}/DNBC4tools/${{SAMPLE_NAME}}）
#   --threads:       分析线程数（当前设置：{self.thread}）
#   --calling_method:细胞筛选方法（固定为emptydrops，适合低/常规细胞数样本）
#   --expectcells:   预期回收细胞数（默认3000，可通过--forcecell覆盖）
#   --forcecell:     强制指定细胞数（优先级高于expectcells，示例：--forcecells 5000）
#   --chemistry:     试剂版本（自动检测，支持：scRNAv1HT/scRNAv2HT/scRNAv3HT/scRNA5Pv1）
#   --end5:          5'端测序分析开关（当前未启用，启用需添加--end5参数）

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
