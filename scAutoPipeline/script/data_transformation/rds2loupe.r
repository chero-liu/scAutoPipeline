library(Seurat)
library(loupeR)

rds=readRDS("/nas/projects/scrna/10x/TSE20251028-025-00005/result/M2/Main/merge/PRO_diff.h5ad")

rds <- RenameCells(rds,new.names=rds$rawbc)

# 获取 metadata 数据框
meta <- nrds[[]]  # 或 nrds@meta.data

# 计算每列的唯一值数量（将因子转换为字符，避免未使用水平的影响）
n_unique <- sapply(meta, function(col) length(unique(as.character(col))))

# 找出超过阈值的列名
cols_to_remove <- names(n_unique[n_unique > 32768])

# 如果存在，则删除这些列
if (length(cols_to_remove) > 0) {
  message("发现以下列的唯一值数量超过 32768，即将删除：", 
          paste(cols_to_remove, collapse = "、"))
  nrds[[cols_to_remove]] <- NULL  # Seurat v3+ 支持用 NULL 移除列
} else {
  message("所有列的唯一值数量均未超过 32768，无需删除。")
}

# 现在可以安全运行 create_loupe_from_seurat
create_loupe_from_seurat(nrds)