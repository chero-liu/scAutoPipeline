import os
import sys
from scAutoPipeline.tools.utils import ModuleFun
from scAutoPipeline.config.config import DATABASE
from typing import Union


class Clustering(ModuleFun):
    def __init__(
        self,
        data: dict,
        analysis: str,
        input: str,
        type: str,
        upstream: str = None,
    ):
        super().__init__(data, input, analysis, upstream)
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
{self.environment}
{self.script} integration clustering \\
    --input {self.input} \\
    --outdir {self.outdir} \\
    --refgenome {self.refgenome}

"""
        self.save_script(shell_script_content)

    def run(self):
        self.init_param()
        self.prefix = f"{self.prefix}_{self.type}"
        self.shell_script()
