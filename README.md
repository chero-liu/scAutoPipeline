# scAutoPipeline - 单细胞RNA测序自动化分析流水线

## 项目概述

scAutoPipeline是一个用于单细胞RNA测序数据分析的自动化流水线工具。它提供了模块化的分析流程，支持多种单细胞测序平台（如10x Genomics、DNBelab C4等）和多种分析工具（如Cell Ranger、DNBC4tools、fastp等）。该工具旨在简化和标准化单细胞数据分析流程，提高分析效率和可重复性。

### 主要特性

- **模块化设计**：支持多个分析模块（M1、M2等），每个模块专注于特定的分析任务
- **多平台支持**：支持10x Genomics、DNBelab C4等单细胞测序平台
- **多物种支持**：支持人类、小鼠、草鱼等多种物种的参考基因组
- **容器化部署**：使用Docker容器确保分析环境的一致性
- **自动化脚本生成**：自动生成SLURM作业提交脚本，便于在HPC集群上运行
- **配置驱动**：使用YAML配置文件管理分析参数，提高可重复性

## 目录结构

```
scAutoPipeline/
├── scAutoPipeline/          # 主包目录
│   ├── __init__.py         # 包初始化文件，定义版本和可用分析类型
│   ├── scAutoPipeline.py   # 主命令行入口
│   ├── config/             # 配置模块
│   │   └── config.py       # 数据库配置（工具、参考基因组等）
│   ├── init/               # 初始化模块
│   │   ├── __init__.py     # 初始化模块定义
│   │   ├── M1.py           # M1模块实现
│   │   ├── M2.py           # M2模块实现
│   │   └── report.py       # 报告生成模块
│   ├── run/                # 运行模块
│   │   ├── __init__.py     # 运行模块定义
│   │   ├── M1.py           # M1运行实现
│   │   └── M2.py           # M2运行实现
│   ├── tools/              # 工具模块
│   │   ├── utils.py        # 通用工具函数
│   │   ├── M1/             # M1相关工具
│   │   └── M2/             # M2相关工具
│   ├── templates/          # 模板文件
│   │   ├── config/         # 配置文件模板
│   │   │   ├── cfgM1.yaml  # M1配置模板
│   │   │   ├── cfgM2.yaml  # M2配置模板
│   │   │   └── cfgM4.yaml  # M4配置模板
│   │   └── scripts/        # 脚本模板
│   ├── docs/               # 文档
│   │   ├── cellranger/     # Cell Ranger文档
│   │   └── dnbc4tools/     # DNBC4tools文档
│   └── script/             # 分析脚本
│       ├── data_transformation/
│       ├── ma/
│       ├── netplot/
│       ├── report/
│       ├── scenic_vis/
│       └── volcanoplot/
├── setup.py                # 安装脚本
├── MANIFEST.in             # 包清单文件
└── README.md               # 本文档
```

## 安装方法

### 通过pip安装

```bash
# 从源代码安装
git clone <repository-url>
cd scAutoPipeline
pip install -e .
```

### 依赖要求

- Python 3.7+
- 主要Python包依赖：
  - pyyaml
  - numpy
  - pandas
  - matplotlib
  - ruamel.yaml

安装后，系统将添加`scAutoPipeline`命令行工具。

## 快速开始

### 1. 初始化分析项目

```bash
# 初始化M1模块（定量分析）
scAutoPipeline init M1 -i /path/to/input/data -o ./output -s human

# 初始化M2模块（聚类分析）
scAutoPipeline init M2 -o ./output -s human
```

### 2. 配置分析参数

编辑生成的配置文件：
```bash
vim ./output/config/cfgM1.yaml
```

### 3. 运行分析

```bash
# 运行M1模块
scAutoPipeline run M1 -c ./output/config/cfgM1.yaml

# 运行M2模块
scAutoPipeline run M2 -c ./output/config/cfgM2.yaml
```

## 详细使用说明

### 命令行结构

scAutoPipeline采用层级命令结构：

```
scAutoPipeline <assay> <step> [options]
```

其中：
- `<assay>`：分析类型，支持`init`（初始化）和`run`（运行）
- `<step>`：分析步骤，支持`M1`、`M2`等

### 可用命令

#### 初始化模块 (init)

**M1模块** - 定量分析初始化：
```bash
scAutoPipeline init M1 -i <input_path> -o <output_dir> -s <species> [options]
```

参数说明：
- `-i, --input`：输入数据路径（包含FASTQ文件的目录）
- `-o, --outdir`：输出目录（默认：当前目录）
- `-s, --species`：物种（human, mouse, 或 Ctenopharyngodon_idella_GCA_019924925_1）
- `-p, --prefix`：输出文件前缀（可选）
- `--thread`：线程数（可选）

**M2模块** - 聚类分析初始化：
```bash
scAutoPipeline init M2 -o <output_dir> -s <species> [options]
```

#### 运行模块 (run)

**运行M1模块**：
```bash
scAutoPipeline run M1 -c <config_file> [options]
```

**运行M2模块**：
```bash
scAutoPipeline run M2 -c <config_file> [options]
```

参数说明：
- `-c, --config`：配置文件路径（YAML格式）

### 配置文件说明

#### M1配置文件 (cfgM1.yaml)

```yaml
module: M1           # 模块名称（定量分析）
programID:           # 项目ID（必填）
species:             # 物种（必填）：human/mouse/Ctenopharyngodon_idella_GCA_019924925_1

analysis:            # 分析步骤配置（必填）
  fastp: 0           # [0,1] 质量控制
  dnbc4tools: 0      # [0,1] DNBC4tools分析
  cellranger: 0      # [0,1] Cell Ranger分析
  qc: 0              # [0,1] 质量控制分析

param:
  input:             # 输入路径（必填）
  types:             # 分析对象（可选，不填写则分析input下所有样本）
  prefix:            # 前缀（可选）
  refgenome:         # 参考基因组（可选，默认根据物种选择）
  forcecell:         # 强制指定细胞数量（可选，整数）

  # 各分析步骤的详细参数
  fastp:
  dnbc4tools:
  cellranger:
  qc:
```

#### M2配置文件 (cfgM2.yaml)

```yaml
module: M2           # 模块名称（聚类分析）
programID:           # 项目ID（必填）
species:             # 物种（必填）

analysis:            # 分析步骤配置（必填）
  clustering: 0      # [0,1] 聚类分析
  merge: 0           # [0,1] 合并分析
  manualanno: 0      # [0,1] 手动注释

param:
  input:             # 输入路径（必填）
  prefix:            # 前缀（可选）
  # 各分析步骤的详细参数
  clustering:
  merge:
  manualanno:
```

## 分析模块详解

### M1模块：定量分析

M1模块负责单细胞数据的定量分析，包括：

1. **fastp**：FASTQ文件质量控制
2. **dnbc4tools**：DNBelab C4平台数据分析
3. **cellranger**：10x Genomics平台数据分析
4. **qc**：数据质量控制和过滤

### M2模块：聚类分析

M2模块负责单细胞数据的下游分析，包括：

1. **clustering**：细胞聚类分析
2. **merge**：多个样本合并分析
3. **manualanno**：细胞类型手动注释

## 支持的物种和参考基因组

scAutoPipeline预配置了以下物种的参考基因组：

### 人类 (human)
- **DNBC4tools**：GRCh38-2024-A (`/nas/database/scrna/c4-refdata/GRCh38-2024-A`)
- **Cell Ranger**：GRCh38 (`/nas/database/scrna/10x-refdata/GRCh38-2024-A`)

### 小鼠 (mouse)
- **DNBC4tools**：GRCm39-2024-A (`/nas/database/scrna/c4-refdata/GRCm39-2024-A`)
- **Cell Ranger**：GRCm39 (`/nas/database/scrna/10x-refdata/GRCm39-2024-A`)

### 草鱼 (Ctenopharyngodon_idella_GCA_019924925_1)
- **DNBC4tools**：GCA_019924925.1 (`/nas/database/scrna/c4-refdata/Ctenopharyngodon_idella_GCA_019924925_1`)

## 工具配置

scAutoPipeline集成了以下分析工具，每个工具都配置了Docker容器环境：

### M1模块工具
- **dnbc4tools**：DNBelab C4数据分析工具
- **cellranger**：10x Genomics Cell Ranger
- **fastp**：FASTQ文件质量控制工具
- **qc**：单细胞数据质量控制工具

### M2模块工具
- **clustering**：细胞聚类分析工具
- **merge**：样本合并分析工具
- **manualanno**：细胞类型注释工具

每个工具都配置了相应的Docker容器、脚本路径和默认线程数，确保分析环境的一致性。

## 输出结构

### M1模块输出目录
```
output/
├── config/           # 配置文件
├── result/M1/        # M1结果文件
├── script/M1/        # M1分析脚本
│   └── logs/        # 日志文件
├── result/M2/        # M2结果文件（预留）
├── script/M2/        # M2分析脚本（预留）
│   └── logs/
└── sbatch.sh        # SLURM作业提交脚本
```

### 自动生成的脚本

scAutoPipeline会自动生成以下文件：
1. **分析脚本**：每个分析步骤的Shell脚本
2. **SLURM提交脚本**：自动管理作业依赖关系的提交脚本
3. **配置文件**：基于模板生成的YAML配置文件

## 高级功能

### FASTQ文件自动分类

scAutoPipeline提供了`classify_fastq_files`函数，可自动分类FASTQ文件：

```python
from scAutoPipeline.tools.utils import classify_fastq_files

result = classify_fastq_files("/path/to/fastq/directory")
# 返回分类后的文件字典：cDNAfastq1, cDNAfastq2, oligofastq1, oligofastq2
```

### 自定义分析模块

用户可以通过以下步骤扩展scAutoPipeline：

1. 在`scAutoPipeline/init/`或`scAutoPipeline/run/`目录中添加新的模块文件
2. 在相应的`__init__.py`文件中注册模块
3. 在`config/config.py`中配置工具参数
4. 在`templates/config/`中添加配置文件模板

## 故障排除

### 常见问题

1. **模块找不到错误**
   - 确保已正确安装scAutoPipeline
   - 检查Python路径和包导入

2. **配置文件错误**
   - 检查YAML文件格式是否正确
   - 确保所有必填字段都已填写

3. **Docker容器错误**
   - 确保Docker服务正在运行
   - 检查容器镜像是否可用

4. **参考基因组路径错误**
   - 检查`config/config.py`中的参考基因组路径
   - 确保有相应的访问权限

### 获取帮助

- 查看命令行帮助：`scAutoPipeline -h`
- 查看特定模块帮助：`scAutoPipeline init M1 -h`
- 检查日志文件：`output/script/*/logs/`

## 开发指南

### 项目结构扩展

要添加新的分析模块：

1. 创建模块文件：`scAutoPipeline/init/NewModule.py`
2. 定义模块类，继承自`Step`基类
3. 实现`run()`方法
4. 在`__init__.py`中注册模块
5. 添加配置文件模板

### 代码规范

- 遵循PEP 8代码风格
- 使用类型提示（Type Hints）
- 添加适当的文档字符串
- 编写单元测试

## 版本历史

- **v1.0**：初始版本，支持M1和M2模块

## 许可证

[在此添加许可证信息]

## 作者

- 刘承龙 (liuchenglong) - njlcl@outlook.com

## 致谢

感谢所有贡献者和用户的支持与反馈。

---

*注意：本文档基于scAutoPipeline v1.0编写，具体功能可能随版本更新而变化。请参考实际代码和最新文档。*
