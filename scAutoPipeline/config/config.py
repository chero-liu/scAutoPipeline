import os
from scAutoPipeline.__init__ import ROOT_PATH, SOFTWARE_NAME

TEMPLATE_CONFIG_PATH = (
    os.path.dirname(ROOT_PATH) + "/" + SOFTWARE_NAME + "/templates/config"
)

DATABASE = {
    "pipelines": {
        "M1": {
            "config_yaml": f"{TEMPLATE_CONFIG_PATH}/cfgM1.yaml",
            "tools": {
                "dnbc4tools": {
                    "environment": "",
                    "script": "/opt/dnbc4tools2.1.3/dnbc4tools",
                    "thread": 20,
                    "description": "DNBC4tools分析环境及线程配置",
                },
                "cellranger": {
                    "environment": "",
                    "script": "/opt/cellranger-10.0.0/bin/cellranger",
                    "thread": 20,
                    "description": "Cellranger分析环境配置",
                },
                "fastp": {
                    "environment": "",
                    "script": "/opt/conda_envs/lclEnv/bin/fastp",
                    "thread": 10,
                    "description": "Fastp质量控制环境及线程配置",
                },
                "qc": {
                    "environment": "source /opt/miniconda3/etc/profile.d/conda.sh && conda activate clscanpy",
                    "script": "clscanpy",
                    "thread": 5,
                    "description": "质量控制分析环境及线程配置",
                },
            },
        },
        "M2": {
            "config_yaml": f"{TEMPLATE_CONFIG_PATH}/cfgM2.yaml",
            "tools": {
                "clustering": {
                    "environment": "source /opt/miniconda3/etc/profile.d/conda.sh && conda activate clscanpy",
                    "script": "clscanpy",
                    "thread": 5,
                    "description": "clustering分析环境及线程配置",
                },
            },
        },
    },
    "refgenome": {
        "human": {
            "dnbc4tools": {
                "index_path": "/nas/database/scrna/c4-refdata/GRCh38-2024-A",
                "genome_version": "GRCh38-2024-A",
                "description": "人类GRCh38参考基因组DNBC4tools索引路径",
            },
            "cellranger": {
                "index_path": "/nas/database/scrna/10x-refdata/GRCh38-2024-A",
                "genome_version": "GRCh38",
                "description": "人类GRCh38参考基因组Cellranger索引路径",
            },
        },
        "mouse": {
            "dnbc4tools": {
                "index_path": "/nas/database/scrna/c4-refdata/GRCm39-2024-A",
                "genome_version": "GRCm39-2024-A",
                "description": "小鼠GRCm39参考基因组DNBC4tools索引路径",
            },
            "cellranger": {
                "index_path": "/nas/database/scrna/10x-refdata/GRCm39-2024-A",
                "genome_version": "GRCm39",
                "description": "小鼠GRCm39参考基因组Cellranger索引路径",
            },
        },
    },
}
