# Cell Ranger 输出结果解读文档

## 目录结构概述

Cell Ranger 是 10x Genomics 单细胞 RNA 测序数据分析的标准流程。包含了一个样本的完整分析结果。

## 主要文件说明

### 1. 核心输出文件

#### 1.1 `web_summary.html`
- **文件类型**: HTML 报告
- **作用**: 交互式网页总结报告，包含质控指标、细胞数估计、测序质量等可视化结果
- **查看方式**: 在浏览器中打开即可查看完整的分析总结
- **注意**: 该文件较大，包含丰富的交互式图表，是快速了解实验质量的主要文件

#### 1.2 `metrics_summary.csv`
- **文件类型**: CSV 表格
- **作用**: 关键质控指标的汇总表格
- **内容示例**:
  ```
  Estimated Number of Cells,Mean Reads per Cell,Median Genes per Cell,Number of Reads,Valid Barcodes
  ```
- **重要指标**:
  - `Estimated Number of Cells`: 估计的细胞数
  - `Mean Reads per Cell`: 每个细胞平均reads数
  - `Median Genes per Cell`: 每个细胞中位数基因数
  - `Number of Reads`: 总reads数
  - `Valid Barcodes`: 有效barcode比例

#### 1.3 `cloupe.cloupe`
- **文件类型**: Loupe 浏览器文件
- **作用**: 10x Genomics Loupe 浏览器专用文件，用于交互式数据探索
- **使用方式**: 需要安装 Loupe 浏览器软件打开
- **功能**: 包含所有分析结果的可视化，支持细胞聚类、基因表达查看、差异分析等

#### 1.4 `molecule_info.h5`
- **文件类型**: HDF5 格式文件
- **作用**: 存储分子级别的原始数据
- **内容**: 包含每个分子的 barcode、UMI、基因信息等
- **用途**: 用于下游自定义分析或重新分析

### 2. 基因表达矩阵文件

#### 2.1 `filtered_feature_bc_matrix/` 目录
- **作用**: 过滤后的基因表达矩阵，只包含被识别为细胞的 barcodes

##### `barcodes.tsv.gz`
- **格式**: 压缩的 TSV 文件
- **内容**: 被识别为细胞的 barcode 列表
- **示例**:
  ```
  AAACCCAAGAAGTCAT-1
  AAACCCAAGAGCCTGA-1
  AAACCCAAGAGTCTTC-1
  ```
- **说明**: 每行代表一个被识别为细胞的 barcode，格式为 `序列-数字`

##### `features.tsv.gz`
- **格式**: 压缩的 TSV 文件
- **内容**: 基因/特征信息
- **示例**:
  ```
  ENSMUSG00000051951	Xkr4	Gene Expression
  ENSMUSG00000089699	Gm1992	Gene Expression
  ENSMUSG00000102331	Gm19938	Gene Expression
  ```
- **列说明**:
  - 第1列: 基因ID (如 ENSMUSG00000051951)
  - 第2列: 基因名称 (如 Xkr4)
  - 第3列: 特征类型 (通常是 "Gene Expression")

##### `matrix.mtx.gz`
- **格式**: 压缩的 Matrix Market 格式
- **内容**: 稀疏矩阵格式的基因表达计数
- **头部信息**:
  ```
  MatrixMarket matrix coordinate integer general
  metadata_json: {"software_version": "10.0.0", "format_version": 2}
  ```
- **说明**:
  - 第1行: 文件格式说明
  - 第2行: 元数据
  - 第3行: 矩阵维度

#### 2.2 `raw_feature_bc_matrix/` 目录
- **作用**: 原始的基因表达矩阵，包含所有检测到的 barcodes
- **文件结构**: 与 `filtered_feature_bc_matrix/` 相同，但包含更多 barcodes
- **用途**: 用于质量控制或重新定义细胞阈值

### 3. 分析结果目录 (`analysis/`)

#### 3.1 主成分分析 (`pca/`)
- **目录**: `gene_expression_10_components/`
- **作用**: 基因表达数据的降维分析

##### `components.csv`
- **内容**: PCA 的主成分载荷矩阵
- **示例**:
  ```
  PC,ENSMUSG00000051951,ENSMUSG00000089699,ENSMUSG00000025900,ENSMUSG00000025902
  1,-0.0012658475685515353,-0.0005329480163130478,0,0
  2,-0.00010357694577479134,0.003148707322563077,0,0
  ```
- **说明**: 每行代表一个主成分 (PC1-PC10)，每列代表一个基因在该主成分上的载荷

##### `dispersion.csv`
- **内容**: 基因的离散度信息
- **示例**:
  ```
  Feature,Normalized.Dispersion
  ENSMUSG00000051951,-0.9760940384496872
  ENSMUSG00000089699,1.8339311147011599
  ```
- **说明**: 用于选择高变异基因进行PCA分析

##### `features_selected.csv`
- **作用**: 被选择用于PCA分析的高变异基因列表
- **格式**: 与 `features.tsv.gz` 类似

##### `projection.csv`
- **作用**: 细胞在PCA空间中的坐标
- **格式**: 每行一个细胞，每列一个主成分

##### `variance.csv`
- **作用**: 每个主成分解释的方差比例

#### 3.2 聚类分析 (`clustering/`)
- **作用**: 基于基因表达模式的细胞聚类

##### 聚类方法:
- `gene_expression_graphclust/`: 图聚类算法 (默认)
- `gene_expression_kmeans_2_clusters/` 到 `gene_expression_kmeans_10_clusters/`: K-means 聚类 (2-10个簇)

##### `clusters.csv`
- **内容**: 每个细胞的聚类标签
- **示例**:
  ```
  Barcode,Cluster
  AAACCCAAGAAGTCAT-1,3
  AAACCCAAGAGCCTGA-1,2
  ```
- **说明**: 将每个细胞分配到特定的聚类中

#### 3.3 差异表达分析 (`diffexp/`)
- **作用**: 找出不同聚类间差异表达的基因

##### `differential_expression.csv`
- **内容**: 差异表达分析结果
- **示例**:
  ```
  Feature ID,Feature Name,Cluster 1 Mean Counts,Cluster 1 Log2 fold change,Cluster 1 Adjusted p value
  ENSMUSG00000051951,Xkr4,0.005593166657170627,-0.035501271720924876,1
  ENSMUSG00000089699,Gm1992,0,-0.8131088503844772,0.8583223785851696
  ```
- **重要列**:
  - `Log2 fold change`: 对数2倍变化值 (正值表示上调，负值表示下调)
  - `Adjusted p value`: 校正后的p值 (越小越显著)

#### 3.4 t-SNE 可视化 (`tsne/`)
- **目录**: `gene_expression_2_components/`

##### `projection.csv`
- **内容**: 细胞在t-SNE二维空间中的坐标
- **示例**:
  ```
  Barcode,TSNE-1,TSNE-2
  AAACCCAAGAAGTCAT-1,-18.015674622954126,11.174526102871694
  AAACCCAAGAGCCTGA-1,22.48505913023667,-31.528657872104326
  ```
- **用途**: 用于二维可视化细胞群体结构

#### 3.5 UMAP 可视化 (`umap/`)
- **目录**: `gene_expression_2_components/`

##### `projection.csv`
- **内容**: 细胞在UMAP二维空间中的坐标
- **示例**:
  ```
  Barcode,UMAP-1,UMAP-2
  AAACCCAAGAAGTCAT-1,6.170348521818011,-3.3746068757894827
  AAACCCAAGAGCCTGA-1,-6.928145173169278,7.041816673991951
  ```
- **用途**: 另一种流行的降维可视化方法

### 4. HDF5 格式文件

#### `filtered_feature_bc_matrix.h5`
- **作用**: 过滤后基因表达矩阵的HDF5格式
- **优点**: 比文本格式更紧凑，读取更快
- **兼容性**: 兼容多种分析工具 (如 Seurat、Scanpy)

#### `raw_feature_bc_matrix.h5`
- **作用**: 原始基因表达矩阵的HDF5格式

## 数据解读要点

### 1. 数据分析流程
1. **原始数据处理**: `raw_feature_bc_matrix/` 包含所有检测信号
2. **细胞识别**: 基于barcode的UMI计数区分细胞与背景
3. **质量控制**: 生成过滤后的矩阵 `filtered_feature_bc_matrix/`
4. **降维分析**: PCA识别主要变异来源
5. **细胞聚类**: 基于基因表达模式分组细胞
6. **差异表达**: 识别聚类特异的标记基因
7. **可视化**: t-SNE和UMAP展示细胞关系

### 2. 下游分析建议
1. **使用 Loupe 浏览器（https://www.10xgenomics.com/support/software/loupe-browser/latest）**: 打开 `cloupe.cloupe` 进行交互式探索
2. **R/Python 分析**: 使用 `filtered_feature_bc_matrix.h5` 导入到 Seurat 或 Scanpy
3. **标记基因识别**: 查看 `diffexp/` 目录中的差异表达结果
4. **质量控制**: 比较 `raw_` 和 `filtered_` 矩阵评估过滤效果

## 注意事项

1. **文件关联性**: 三个矩阵文件 (`barcodes.tsv.gz`, `features.tsv.gz`, `matrix.mtx.gz`) 需要一起使用
2. **版本兼容性**: 不同版本的Cell Ranger可能产生略有不同的输出结构
3. **存储空间**: 原始数据文件较大，注意磁盘空间管理
4. **分析完整性**: 所有分析步骤的结果都保存在 `analysis/` 目录中，可按需使用

*分析软件: Cell Ranger 9.0.1
