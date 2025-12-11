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
                    "environment": "conda activate lclEnv",
                    "script": "/opt/dnbc4tools2.1.3/dnbc4tools",
                    "thread": 10,
                    "description": "DNBC4tools分析环境及线程配置",
                },
                "cellranger": {
                    "extra_config": "aksd",
                    "description": "Cellranger额外配置项",
                },
            },
        }
    },
    "refgenome": {
        "human": {
            "dnbc4tools": {
                "index_path": "/nas/database/scrna/c4-refdata/GRCh38-2024-A_C4/c4",
                "genome_version": "GRCh38-2024-A",
                "description": "人类GRCh38参考基因组DNBC4tools索引路径",
            },
            "cellranger": {
                "index_path": "test",
                "genome_version": "GRCh38",
                "description": "人类GRCh38参考基因组Cellranger索引路径",
            },
        },
        "mouse": {
            "dnbc4tools": {
                "index_path": "/nas/database/scrna/c4-refdata/GRCm39-2024-A_C4/c4",
                "genome_version": "GRCm39-2024-A",
                "description": "小鼠GRCm39参考基因组DNBC4tools索引路径",
            },
            "cellranger": {
                "index_path": "test",
                "genome_version": "GRCm39",
                "description": "小鼠GRCm39参考基因组Cellranger索引路径",
            },
        },
    },
}
