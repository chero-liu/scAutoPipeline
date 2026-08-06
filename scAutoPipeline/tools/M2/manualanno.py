import os
import sys
from scAutoPipeline.tools.utils import ModuleFun
from scAutoPipeline.config.config import DATABASE
from typing import Union


class Manualanno(ModuleFun):
    def __init__(
        self,
        data: dict,
        analysis: str,
        input: str,
        type: str,
        annofile: str = None,
        upstream: str = None,
    ):
        super().__init__(data, input, analysis, upstream)
        self.type = type
        self.annofile = annofile

    def init_param(self):
        self.outdir = os.path.join(
            self.outdir,
            self.type,
            self.analysis,
        )

    def shell_script(self):
        shell_script_content = f"""#!/bin/bash
set -euo pipefail
{self.environment} \\
{self.script} integration manualanno \\
    --input {self.input} \\
    --outdir {self.outdir} \\
    --groupby celltype \\
    --refgenome  {self.refgenome} \\
    --annofile {self.annofile}


{self.environment} chmod 777 -R {self.outdir}


"""
        self.save_script(shell_script_content)

    def run(self):
        self.init_param()
        self.prefix = f"{self.prefix}_{self.type}"
        self.shell_script()
