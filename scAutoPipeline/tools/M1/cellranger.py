import os
import sys
from scAutoPipeline.tools.utils import ModuleFun
from scAutoPipeline.config.config import DATABASE


class CellRanger(ModuleFun):
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
        if self.refgenome == None:
            self.refgenome = DATABASE["refgenome"][self.species][self.analysis][
                "index_path"
            ]
        if self.data["param"]["forcecell"] != None:
            self.forcecell = f"--forcecell {self.data['param']['forcecell']}"
        else:
            self.forcecell = ""

    def shell_script(self):
        shell_script_content = f"""#!/bin/bash

set -euo pipefail
mkdir -p {self.outdir}
{self.environment} \\
{self.script} count \\
    --id={self.type} \\
    --transcriptome={self.refgenome} \\
    --fastqs={self.input}/{self.type} \\
    --sample={self.type} \\
    --localcores={self.thread} \\
    --localmem=100 \\
    --create-bam=true \\
    --output-dir {self.outdir} {self.forcecell}

# Generate info.csv
FEATURE_MATRIX_PATH={self.outdir}/outs/filtered_feature_bc_matrix
OUTPUT_FILE="{self.outdir}/info.csv"

echo "sample,path,group,sample_order,datatype" > "$OUTPUT_FILE"
echo "{self.type},$FEATURE_MATRIX_PATH,{self.type},1,mtx-10x" >> "$OUTPUT_FILE"

cp /home/chenglong.liu/RaD/scAutoPipeline/scAutoPipeline/docs/cellranger/README.md {self.outdir}/output
"""
        self.save_script(shell_script_content)

    def run(self):
        self.init_param()
        self.prefix = f"{self.prefix}_{self.type}"
        self.shell_script()
