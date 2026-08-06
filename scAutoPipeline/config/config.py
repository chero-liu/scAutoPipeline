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
                    "environment": "docker run --rm -v  /nas/:/nas crpi-nc6vrpgro1z8mu8m.cn-chengdu.personal.cr.aliyuncs.com/lclimage/dnbc4tools:v2.1.3",
                    "script": "dnbc4tools",
                    "thread": 8,
                    "description": "DNBC4tools分析环境及线程配置",
                },
                "cellranger": {
                    "environment": "docker run --rm -v  /nas/:/nas crpi-nc6vrpgro1z8mu8m.cn-chengdu.personal.cr.aliyuncs.com/lclimage/cellranger:v9.0.1",
                    "script": "cellranger",
                    "thread": 8,
                    "description": "Cellranger分析环境配置",
                },
                "fastp": {
                    "environment": "",
                    "script": "/opt/conda_envs/lclEnv/bin/fastp",
                    "thread": 4,
                    "description": "Fastp质量控制环境及线程配置",
                },
                "qc": {
                    "environment": "docker run --rm  -v /nas:/nas crpi-nc6vrpgro1z8mu8m.cn-chengdu.personal.cr.aliyuncs.com/lclimage/music:v1.0.0",
                    "script": "clscanpy",
                    "thread": 4,
                    "description": "质量控制分析环境及线程配置",
                },
            },
        },
        "M2": {
            "config_yaml": f"{TEMPLATE_CONFIG_PATH}/cfgM2.yaml",
            "tools": {
                "clustering": {
                    "environment": "docker run --rm  -v /nas:/nas crpi-nc6vrpgro1z8mu8m.cn-chengdu.personal.cr.aliyuncs.com/lclimage/clscanpy:v1.0.0",
                    "script": "clscanpy",
                    "thread": 8,
                    "description": "clustering分析环境及线程配置",
                },
                "merge": {
                    "environment": "docker run --rm  -v /nas:/nas crpi-nc6vrpgro1z8mu8m.cn-chengdu.personal.cr.aliyuncs.com/lclimage/clscanpy:v1.0.0",
                    "script": "clscanpy",
                    "thread": 8,
                    "description": "merge分析环境及线程配置",
                },
                "manualanno": {
                    "environment": "docker run --rm  -v /nas:/nas crpi-nc6vrpgro1z8mu8m.cn-chengdu.personal.cr.aliyuncs.com/lclimage/clscanpy:v1.0.0",
                    "script": "clscanpy",
                    "thread": 8,
                    "description": "manualanno分析环境及线程配置",
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
        "Ctenopharyngodon_idella_GCA_019924925_1": {
            "dnbc4tools": {
                "index_path": "/nas/database/scrna/c4-refdata/Ctenopharyngodon_idella_GCA_019924925_1",
                "genome_version": "GCA_019924925.1",
                "description": "草鱼(Ctenopharyngodon_idella) GCA_019924925.1版本",
            },
            "cellranger": {
                "index_path": "",
                "genome_version": "",
                "description": "",
            },
        },
    },
}
