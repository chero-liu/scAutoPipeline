# dnbc4tools 输出文件解读文档

## 目录概述

本目录包含单细胞RNA测序（scRNA-seq）数据分析流程 `dnbc4tools` 的输出结果。这些文件涵盖了从原始数据到分析结果的各个阶段，包括质量控制、细胞过滤、基因表达矩阵、测序指标统计、可视化报告等。

## 主要文件说明

### 1. 核心分析文件

#### 1.1 `metrics_summary.xls` - 测序指标汇总表
- **格式**: TSV/Excel格式（制表符分隔）
- **内容**: 包含样本的总体测序统计信息
- **用途**: 
  - 评估测序数据质量
  - 查看细胞数量估计、平均reads数、UMI计数、基因检测数等关键指标
  - 检查测序饱和度、Q30比例、线粒体基因比例等质量控制参数

#### 1.2 `singlecell.csv` - 单细胞水平统计表
- **格式**: CSV格式（逗号分隔）
- **内容**: 每个细胞的详细统计信息
- **用途**:
  - 查看每个细胞的原始reads数、检测到的基因数、UMI数
  - 识别有效细胞条形码（is_cell_barcode=1）
  - 追踪细胞对应的原始条形码序列

#### 1.3 `*_scRNA_report.html` - 分析报告
- **格式**: HTML网页报告
- **内容**: 包含数据可视化、质量控制图表、分析结果摘要
- **用途**: 
  - 交互式查看分析结果
  - 包含UMI分布、基因表达分布、细胞聚类、标记基因等可视化
  - 用于结果展示和分享

#### 1.4 `filter_feature.h5ad` - 过滤后的单细胞数据
- **格式**: HDF5格式的AnnData对象（Hierarchical Data Format version 5）
- **内容**: 包含过滤后的细胞和基因的表达矩阵、细胞注释、基因注释等
- **用途**:
  - 用于下游分析的标准化数据格式
  - 可在Python的scanpy、anndata等工具中直接加载
  - 包含细胞聚类、降维等中间结果

### 2. 比对文件

#### 2.1 `anno_decon_sorted.bam` - 注释和去卷积后的比对文件
- **格式**: BAM格式（二进制比对文件）
- **内容**: 经过注释和去卷积处理的测序reads比对结果
- **用途**:
  - 存储reads到参考基因组的比对信息
  - 已按坐标排序，便于快速检索
  - 包含基因注释信息

#### 2.2 `anno_decon_sorted.bam.bai` - BAM索引文件
- **格式**: BAI格式（BAM索引）
- **用途**: 用于快速随机访问BAM文件中的特定区域

### 3. 表达矩阵目录

#### 3.1 `filter_matrix/` - 过滤后的表达矩阵
包含经过质量控制的细胞和基因的表达数据：
- `barcodes.tsv.gz`: 细胞条形码列表（示例: CELL1_N2, CELL2_N3, ...）
- `features.tsv.gz`: 基因/特征列表（示例: LOC127515515, LOC127499227, ...）
- `matrix.mtx.gz`: 稀疏表达矩阵（Matrix Market格式）

**用途**: 标准10X Genomics格式，用于下游聚类和差异表达分析。

#### 3.2 `raw_matrix/` - 原始表达矩阵
结构与`filter_matrix/`相同，但包含所有原始检测到的细胞（未经过滤）。

**用途**: 保留原始数据，用于质量控制比较。

### 4. 附加分析目录

#### 4.1 `attachment/RNAvelocity_matrix/` - RNA速率分析矩阵
用于RNA速率分析的特殊矩阵：
- `barcodes.tsv.gz`: 细胞条形码
- `features.tsv.gz`: 基因列表
- `spliced.mtx.gz`: 剪接转录本表达矩阵
- `unspliced.mtx.gz`: 未剪接转录本表达矩阵
- `spanning.mtx.gz`: 跨越内含子的reads矩阵

**用途**: 用于RNA速率分析，预测细胞分化方向。

#### 4.2 `attachment/splice_matrix/` - 剪接矩阵
剪接特异性表达矩阵，结构与`filter_matrix/`相同。

**用途**: 专注于剪接转录本的分析。

## 文件关系和使用建议

### 数据分析流程
1. **质量控制**: 查看`metrics_summary.xls`和`singlecell.csv`评估数据质量
2. **表达矩阵**: 使用`filter_matrix/`中的矩阵进行下游分析
3. **深入分析**: 
   - 使用`filter_feature.h5ad`进行聚类、降维、差异表达分析
   - 使用`attachment/RNAvelocity_matrix/`进行RNA速率分析
4. **结果查看**: 打开`*_scRNA_report.html`查看可视化报告
5. **原始数据**: `raw_matrix/`和`anno_decon_sorted.bam`保留原始比对信息

### 注意事项
1. 压缩文件（.gz）需要使用相应工具解压或直接通过编程接口读取
2. H5AD文件需要使用Python的anndata或scanpy库处理
3. BAM文件需要使用samtools、IGV等工具查看
4. 矩阵文件为稀疏格式，适合处理单细胞数据的高维稀疏特性

### 推荐工具
- **Python**: scanpy, anndata, scvelo (用于RNA速率)
- **R**: Seurat, SingleCellExperiment
- **命令行**: samtools (BAM文件), zcat/gunzip (压缩文件)
- **可视化**: IGV (基因组浏览器), 浏览器打开HTML报告

## 总结
本输出目录提供了从原始测序数据到高级分析结果的完整数据链。研究人员可以根据需要选择不同层次的文件进行进一步分析或结果验证。`filter_feature.h5ad`和`filter_matrix/`是进行大多数下游分析的核心文件，而`metrics_summary.xls`和HTML报告则提供了快速的质量评估和结果概览。
