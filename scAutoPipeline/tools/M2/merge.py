import os
import sys
from scAutoPipeline.tools.utils import ModuleFun
from scAutoPipeline.config.config import DATABASE
from typing import Union


class Merge(ModuleFun):
    def __init__(
        self,
        data: dict,
        analysis: str,
        input: str,
        type: str,
        model: str = None,
        upstream: str = None,
    ):
        super().__init__(data, input, analysis, upstream)
        self.type = type
        self.model = model

    def init_param(self):
        self.outdir = os.path.join(
            self.outdir,
            self.type,
            self.analysis,
        )
        if self.model is None:
            self.model = ""
        else:
            self.model = f"--model {self.model}"

    def shell_script(self):
        shell_script_content = f"""#!/bin/bash
set -euo pipefail
{self.environment} \\
{self.script} integration merge \\
    --info {self.input} \\
    --refgenome  {self.refgenome} \\
    --outdir {self.outdir} \\
    --rmdoublet_method doubletdetection {self.model}

{self.environment} chmod 777 -R {self.outdir}

"""
        self.save_script(shell_script_content)

    def run(self):
        self.init_param()
        self.prefix = f"{self.prefix}_{self.type}"
        self.shell_script()
