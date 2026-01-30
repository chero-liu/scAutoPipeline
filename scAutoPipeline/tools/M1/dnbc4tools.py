import os
import sys
from scAutoPipeline.tools.utils import ModuleFun
from scAutoPipeline.config.config import DATABASE
from scAutoPipeline.tools.M1.utils import classify_fastq_files


class DNBC4tools(ModuleFun):
    def __init__(
        self,
        data: dict,
        analysis: str,
        input: str,
        type: str,
        cDNAfastq1: str = None,
        cDNAfastq2: str = None,
        oligofastq1: str = None,
        oligofastq2: str = None,
    ):
        super().__init__(data, input, analysis)
        self.type = type
        self.cDNAfastq1 = cDNAfastq1
        self.cDNAfastq2 = cDNAfastq2
        self.oligofastq1 = oligofastq1
        self.oligofastq2 = oligofastq2

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
        
        if self.cDNAfastq1 == None:
            fq_dict = classify_fastq_files(f"{self.input}/{self.type}")
            self.cDNAfastq1 = fq_dict['cDNAfastq1']
            self.cDNAfastq2 = fq_dict['cDNAfastq2']
            self.oligofastq1 = fq_dict['oligofastq1']
            self.oligofastq2 = fq_dict['oligofastq2']

    def shell_script(self):
        shell_script_content = f"""#!/bin/bash

set -euo pipefail

{self.environment} \\
{self.script} rna run \\
    --name {self.type} \\
    --cDNAfastq1 {self.cDNAfastq1} \\
    --cDNAfastq2 {self.cDNAfastq2} \\
    --oligofastq1 {self.oligofastq1} \\
    --oligofastq2 {self.oligofastq2} \\
    --genomeDir {self.refgenome}/star \\
    --outdir {self.outdir} \\
    --threads {self.thread} \\
    --calling_method emptydrops \\
    --expectcells 3000 \\
    --chemistry auto {self.forcecell}

{self.environment} chmod 777 -R {self.outdir}

# Generate info.csv
FEATURE_MATRIX_PATH={self.outdir}/output/filter_matrix
OUTPUT_FILE="{self.outdir}/info.csv"

echo "sample,path,group,sample_order,datatype" > "$OUTPUT_FILE"
echo "{self.type},$FEATURE_MATRIX_PATH,{self.type},1,mtx-c4" >> "$OUTPUT_FILE"

cp /home/chenglong.liu/RaD/scAutoPipeline/scAutoPipeline/docs/dnbc4tools/README.md  {self.outdir}/output

"""
        self.save_script(shell_script_content)

    def run(self):
        self.init_param()
        self.prefix = f"{self.prefix}_{self.type}"
        self.shell_script()
