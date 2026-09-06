# TensionMap 论文复现调研与三阶段规划

> 论文：Hallou et al., **A computational pipeline for spatial mechano-transcriptomics**  
> 期刊：*Nature Methods* 22, 737–750 (2025)  
> DOI：<https://doi.org/10.1038/s41592-025-02618-1>  
> 代码仓库：<https://github.com/Computational-Morphogenomics-Group/TensionMap>  
> 调研日期：2026-09-06

## 一、结论概览

TensionMap 可以理解为三个相互衔接的层次：

1. **细胞几何层**：把二维细胞实例分割掩膜转换成细胞、细胞间连接、顶点和邻接关系。
2. **力学推断层**：用 VMSI 推断相对的细胞间连接张力、细胞内压力和细胞应力张量。
3. **转录组整合层**：将力学量与 seqFISH/插补基因表达数据匹配，进行组织边界、配体–受体和基因–力学关联分析。

最稳妥的复现路线不是直接从原始显微图像开始，而是：

```text
官方合成掩膜教程
    ↓
作者提供的胚胎分割掩膜和处理后数据
    ↓
复现 dataset 3 的 VMSI 推断
    ↓
复现 Figure 3c 的边界张力差异
    ↓
复现 Figure 5 的压力–基因表达空间回归
```

这样可以依次隔离环境、分割几何、非线性优化和转录组统计四类问题。

## 二、仓库结构

```text
TensionMap/
├── README.md
├── tensionmap-minimal.yml
├── tensionmap-full.yml
├── example_data/
│   └── synthetic/
│       └── test.tiff
├── src/
│   ├── VMSI.py
│   ├── segment.py
│   ├── bwmorph.py
│   ├── cellpose_models/
│   ├── initial_optimization.m
│   ├── theta_optimization.m
│   ├── main_minimization.m
│   └── tensionmap_old/
├── notebooks/
│   ├── tensionmap_example.ipynb
│   ├── 00_run_tensionmap.ipynb
│   ├── 01_biophysical_analysis.ipynb
│   ├── 02_sc_analysis.ipynb
│   ├── 03_lr_analysis.ipynb
│   ├── 04_nonlinear_schot.ipynb
│   ├── 05_spatial_regression.ipynb
│   ├── helper_functions.py
│   └── helper_functions.R
└── reproduce_data/
    ├── dataset1/
    │   └── data_access.txt
    ├── dataset2/
    │   └── data_access.txt
    ├── dataset3/
    │   └── data_access.txt
    └── omnipath_cellchatdb.txt
```

### 2.1 核心文件说明

- `README.md`：安装方法、快速上手、教程顺序以及分割掩膜清理建议。
- `src/VMSI.py`：核心实现，包括 `run_VMSI()`、VMSI 优化、张力与压力计算、应力张量、可视化、图像分块和结果导出。
- `src/segment.py`：把已分割的掩膜转换为 VMSI 所需的细胞、边、顶点和邻接图；也包含实验性的 Cellpose 调用入口。
- `src/bwmorph.py`：二值形态学辅助函数，功能接近部分 MATLAB `bwmorph` 操作。
- `src/cellpose_models/`：与作者分割流程有关的 Cellpose 模型材料。
- `src/*.m`：通过 MATLAB `fmincon` 优化时使用，可选。
- `src/tensionmap_old/`：旧版本代码，初次复现不建议使用。
- `example_data/synthetic/test.tiff`：官方合成示例的已分割掩膜。
- `notebooks/00–05`：从力学推断到论文统计分析的主要 notebook。
- `reproduce_data/`：论文数据预期存放位置；GitHub 中主要是下载地址，实际大文件需要另行下载。

项目目前没有常规的 `pyproject.toml` 或 `setup.py`。Notebook 通过修改 `sys.path` 直接导入 `src.VMSI`，因此启动 Jupyter 时的工作目录非常重要。

## 三、运行环境与依赖

### 3.1 最小力学环境

`tensionmap-minimal.yml` 主要包含：

| 依赖 | 版本 |
|---|---:|
| Python | 3.9.12 |
| NumPy | 1.23.5 |
| SciPy | 1.11.2 |
| pandas | 1.4.1 |
| matplotlib | 3.5.1 |
| scikit-image | 0.19.2 |
| scikit-learn | 1.3.1 |
| NLopt | 2.7.1 |
| cyipopt | 1.3.0 |

这个环境适用于：

- 合成数据教程；
- 从分割掩膜运行 VMSI；
- 输出和绘制张力、压力与应力张量。

### 3.2 完整分析环境

`tensionmap-full.yml` 在上述基础上加入：

- R 4.2.1 和 R Jupyter kernel；
- Jupyter/JupyterLab；
- Scanpy、Seaborn、Numba、Decoupler；
- Phenograph、igraph、Leidenalg；
- Bioconductor `scHOT`；
- `clusterProfiler`、`org.Mm.eg.db`、`EnhancedVolcano`；
- R 并行计算、空间模型和绘图包；
- 若干 Conda 与 pip 混合依赖。

完整环境只应在最小力学教程成功后再处理。

### 3.3 优化器选择

- **NLopt**：默认选项，建议作为首次复现的唯一选择。
- **CyIpopt**：环境文件中声明，但在 macOS 上可能需要匹配的系统 Ipopt 库。
- **MATLAB `fmincon`**：需要 MATLAB 许可证和与 Python 版本匹配的 MATLAB Engine。

MATLAB 只是优化器替代方案，并非获得论文结果所必需。仓库已有用户报告 MATLAB 许可证导致运行失败，因此第一阶段应避免使用。

## 四、公开数据及预期目录

论文指定的归档数据位于：

- Zenodo：<https://doi.org/10.5281/zenodo.13975707>
- 当前索引版本：<https://zenodo.org/records/13975708>

归档包约为 **278 MB**，公开页面给出的 MD5 为：

```text
14da2772d0bdcfd28e2e91379e6010aa
```

GitHub 中三个 `data_access.txt` 都指向同一个 Dropbox 文件夹。正式复现应优先使用有版本记录和校验值的 Zenodo 归档。

Notebook 预期目录大致为：

```text
reproduce_data/
├── dataset1/
├── dataset2/
└── dataset3/
```

在官方 notebook 中出现的关键文件包括：

```text
reproduce_data/datasetN/
├── segmentation_final.tif
├── tensionmap_res.csv
├── adj_mat.csv
└── gex_res.csv
```

### 4.1 文件含义

- `segmentation_final.tif`：修正后的细胞实例分割掩膜。
- `tensionmap_res.csv`：逐细胞的几何与力学特征。
- `adj_mat.csv`：细胞邻接矩阵；非零元素为相邻细胞之间的推断张力。
- `gex_res.csv`：与分割细胞对应的插补全转录组表达矩阵。

### 4.2 三个论文数据集

- **dataset 1**：FMH（前脑/中脑/后脑）与 NC（神经嵴）的边界。
- **dataset 2**：CM（颅侧中胚层）与 FMH 的边界。
- **dataset 3**：中脑与后脑边界，即 MHB。

原始生物学数据来自 E8.5 小鼠胚胎 seqFISH，共设计 387 个基因，并利用小鼠原肠胚形成单细胞 RNA-seq 图谱进行细胞类型注释和更广泛的表达插补。首次复现宜直接采用作者发布的处理后数据，不要先独立重建原论文的 seqFISH 预处理。

## 五、官方教程的推荐顺序

### 5.1 `tensionmap_example.ipynb`

最容易运行。输入为 `example_data/synthetic/test.tiff`，主要执行：

```python
vmsi_model = run_VMSI(img)
```

然后绘制张力、压力和应力，导出结果，并演示简单 PCA。

### 5.2 `00_run_tensionmap.ipynb`

在论文胚胎掩膜上运行力学推断，是 Figure 2 的主要代码入口。Notebook 约 12.6 MB，包含大量保存的输出。

### 5.3 `01_biophysical_analysis.ipynb`

从力学输出识别组织边界，比较异型与同型连接张力。它是首次生物学复现最合适的目标。

### 5.4 `02_sc_analysis.ipynb`

用 Scanpy 读取和过滤插补表达数据，进行单细胞表达探索。

### 5.5 `03_lr_analysis.ipynb`

分析组织边界附近具有方向性的配体–受体相互作用。

### 5.6 `05_spatial_regression.ipynb`

在控制平滑空间变化后，检验基因表达与细胞压力/应力之间的关系。

### 5.7 `04_nonlinear_schot.ipynb`

用 scHOT 进行非线性基因–力学关联分析。计算量和解释难度较高，尽管编号在 `05` 前，仍建议最后运行。

## 六、从输入到力学结果的最小工作流

### 6.1 细胞分割与几何构建

这里需要区分两种“分割”：

1. **显微图像分割**：把膜染色图像转成带细胞编号的实例掩膜。
2. **几何处理**：从实例掩膜提取细胞、连接、顶点和邻接图。

官方合成教程从第 2 步开始。

论文中的显微图像分割大致包含：

- 在 Fiji 中用 CLAHE 增强局部对比度；
- 去除异常像素/噪声；
- 使用定制的 Cellpose 流程；
- 手动修正过分割和欠分割；
- 修复四重顶点及其他不适合力学推断的拓扑结构。

最终掩膜交给 `Segmenter.process_segmented_image()`，它会：

- 必要时重新标记细胞；
- 将接触图像边缘的细胞作为外部区域处理；
- 提取细胞质心和形态指标；
- 检测细胞连接与顶点；
- 建立细胞邻接关系；
- 生成 `V_df`、`C_df` 和 `E_df`。

掩膜边界最好为单像素宽、四连通。细小的断裂标签或孤立区域可能使拓扑提取失败。

### 6.2 VMSI 力学推断

最小调用为：

```python
vmsi_model = run_VMSI(img_mask)
```

内部流程可概括为：

```text
带标签的分割掩膜
    ↓
Segmenter.process_segmented_image()
    ↓
细胞、顶点、边和邻接关系
    ↓
消除或协调无效四重顶点
    ↓
保证顶点附近连接的凸性
    ↓
用圆弧或直线拟合细胞连接
    ↓
VMSI 非线性优化
    ↓
相对压力和相对连接张力
    ↓
逐细胞应力张量与形态特征
```

VMSI 假设组织近似处于力学平衡，并利用连接几何、曲率及 Young–Laplace 关系推断力学量。

### 6.3 连接张力

```python
tensions = vmsi_model.return_tensions()
```

若输出邻接矩阵：

```python
cell_results, adj_mat = vmsi_model.output_results(neighbours=True)
```

`adj_mat[i, j]` 为零表示两个细胞不相邻，非零值表示它们共享连接的推断张力。

张力是**任意单位下的相对量**，只能确定到一个乘法尺度。因此最适合比较同一图像内部不同连接类别，而不是直接比较不同图像的原始数值。

### 6.4 细胞内压力

```python
pressures = vmsi_model.return_pressures()
```

压力同样是相对量，只能确定压力差；其绝对零点具有任意的加法偏移。

### 6.5 可视化与结果导出

```python
vmsi_model.plot(
    ["tension", "pressure", "stress"],
    img_mask
)

results, adj_mat = vmsi_model.output_results(neighbours=True)
```

`plot()` 支持：

- `tension`：连接张力；
- `pressure`：细胞压力；
- `stress`：细胞应力张量；
- `CAP`：拟合后的圆弧多边形几何。

逐细胞输出包括：

- 质心；
- 压力；
- 应力张量特征值；
- 应力方向和各向异性；
- 面积与周长；
- 多边形周长；
- Feret 直径；
- 惯性张量特征；
- Hu moments；
- 标签和包围盒信息。

## 七、Notebook 与论文图表的对应关系

| 论文结果 | 主要代码 | 含义 |
|---|---|---|
| Figure 1 | 论文流程示意 | 概念性总览，不是单一可执行输出 |
| Figure 2a–c | `00_run_tensionmap.ipynb`、`VMSI.py` | 分割掩膜、空间张力图和压力图 |
| Figure 2d | `02_sc_analysis.ipynb`、表达数据 | 细胞类型空间图和表达组织结构 |
| Figure 3a–c | `01_biophysical_analysis.ipynb` | 边界概率与异型连接高张力 |
| Figure 3d | 细胞组织模拟代码/数据 | 边界维持的 Cellular Potts 模拟，不适合初次复现 |
| Figure 4 | `03_lr_analysis.ipynb` | 边界配体–受体分析，包括 Eph/ephrin 信号 |
| Figure 5 | `05_spatial_regression.ipynb`、`helper_functions.R` | 控制空间混杂后的基因–压力/应力关联 |
| Figure 6 | `04_nonlinear_schot.ipynb` | scHOT 非线性基因–力学关联 |
| Supplementary Fig. 1 | VMSI 基准和噪声/优化器测试 | 算法验证，工作量较大 |
| Supplementary Figs. 4–5 | MHB 相邻 z 切片 | 跨邻近平行切片的生物学稳健性 |
| Supplementary Figs. 7–10 | Notebook `03–05` | LR、回归、非线性和跨数据集补充分析 |

最合适的核心力学复现目标是 **Figure 3c**：组织边界上的异型连接张力高于组织内部的同型连接张力。论文报告的差异约为 12%–35%，具体取决于数据集。

## 八、主要复现风险

### 8.1 分割是最大的科学风险

很小的边界缺陷就可能改变：

- 哪些细胞相邻；
- 顶点数量和类型；
- 连接曲率；
- 最终推断出的压力和张力。

因此，分割质量不仅影响图像是否“好看”，还会直接改变力学结论。

### 8.2 原始图像分割并非完整的一键式流程

`Segmenter.segment_image()` 在源代码中被标为实验性。仓库也有公开 issue 询问论文中使用的分割代码位置。初次复现应使用作者提供的最终掩膜，而不是立即尝试从原始膜图像完全重建分割。

### 8.3 完整环境可能难以求解

完整环境混合了：

- 较旧的 Python 和 R；
- Conda、pip 和 Bioconductor；
- Numba、Scanpy、scHOT 等版本约束；
- 可能需要系统库的优化器。

仓库已有创建完整环境失败的公开 issue。

### 8.4 工程化程度有限

- 没有常规 Python 打包配置；
- 未发现完善的自动测试套件；
- 导入依赖相对路径和当前工作目录；
- 大型 notebook 保存了大量历史输出。

### 8.5 数据获取路径存在歧义

三个 `data_access.txt` 指向同一 Dropbox 目录。应以 Zenodo 版本为准，并在下载后核验：

- 文件名；
- 目录层次；
- MD5；
- 数据发布日期/版本。

### 8.6 平台兼容性

- Python 3.9 和部分依赖已经较旧；
- Numba 0.56.4 强约束 Python/NumPy 版本；
- Apple Silicon 可能缺少某些旧版求解器的原生构建；
- CyIpopt 依赖系统 Ipopt；
- MATLAB Engine 必须同时匹配 MATLAB 和 Python 版本。

初次复现应忠实采用作者环境版本。依赖现代化应作为后续、独立的工程任务。

### 8.7 计算瓶颈

- VMSI 是约束非线性优化，细胞数增加时成本明显上升。
- 图像分块虽然可以加速，但需要跨块校准压力和张力尺度；对于组织尺度形态各向异性的图像可能带来偏差。
- `05_spatial_regression.ipynb` 明确使用 8 个 R worker。
- scHOT 对 3,000 个高变基因进行置换检验，可能是最慢的转录组步骤。
- Figure 3d 的模拟使用 540 个细胞、50,000 个 Monte Carlo steps，并至少做 6 次重复。

### 8.8 结果解释边界

- 张力和压力不是绝对物理单位。
- VMSI 假设二维上近似力学平衡。
- 胚胎切片只是三维组织的二维截面。
- 不同图像之间的原始张力/压力值不宜直接比较。
- 全转录组表达包含插补值，并非每个基因都被 seqFISH 直接测量。
- 空间自相关可能产生伪基因–力学关系，因此 Figure 5 的空间校正非常关键。

## 九、三阶段复现计划

## Stage 1：运行官方合成数据教程

### 目标

在不引入真实生物数据和原始图像分割复杂性的情况下，验证力学引擎能够运行。

### 输入与配置

- `tensionmap-minimal.yml`；
- `example_data/synthetic/test.tiff`；
- `notebooks/tensionmap_example.ipynb`；
- 优化器使用 NLopt；
- `tile=False`。

### 预期输出

- `run_VMSI(img)` 成功完成；
- 张力图；
- 压力图；
- 应力张量图；
- 逐细胞结果 DataFrame；
- 邻接/张力矩阵。

### 验证标准

- 纳入分析的细胞没有 NaN 或无穷值；
- 大多数内部连接具有正的有限张力；
- 输出图与 notebook 保存的示例在整体空间结构上相似；
- 记录操作系统、CPU 架构、代码 commit、运行时间和完整环境导出。

### 完成定义

成功从官方合成掩膜生成力学图和结果表。

## Stage 2：复现一个核心力学结果

### 推荐目标

复现 **Figure 3c 的 dataset 3（中脑–后脑边界）**。

### 选择 dataset 3 的原因

- 组织边界生物学定义清楚；
- 官方 notebook 默认使用 `dataset3`；
- 论文中它的边界–内部张力差异最大；
- 后续可用相邻 z 切片进行稳健性检验。

### 工作流

1. 检查 `segmentation_final.tif` 的标签和拓扑质量。
2. 运行或核验 `00_run_tensionmap.ipynb`。
3. 导出 `tensionmap_res.csv` 和 `adj_mat.csv`。
4. 运行 `01_biophysical_analysis.ipynb` 的相关部分。
5. 将连接分为：
   - 异型边界连接；
   - 同型中脑连接；
   - 同型后脑连接。
6. 重画张力分布或汇总图。
7. 与 Figure 3c 比较中位数、均值、样本量和效应方向。

### 验证标准

- 把高张力连接叠加回分割掩膜进行人工检查；
- 确认掩膜、元数据和邻接矩阵中的细胞 ID 完全对应；
- 检查结论对边界标签阈值是否敏感；
- 同时比较作者提供的机械结果和本地重新推断结果；
- 比较归一化比例和排序，不要求任意单位下的绝对数值完全相同。

### 完成定义

异型边界连接的相对张力高于两类同型连接，效应方向及量级与论文基本一致。

## Stage 3：复现一个力学–转录组结果

### 推荐目标

先复现 **Figure 5 的细胞压力–基因表达空间回归**，而不是直接运行 scHOT。

### 选择 Figure 5 的原因

- 直接把逐细胞力学量与基因表达联系起来；
- 明确处理空间混杂；
- 比 scHOT 更容易解释且计算量较低；
- 不需要像配体–受体分析那样引入额外的方向和邻接假设。

### 工作流

1. 使用 `gex_res.csv` 和 Stage 2 验证后的 `tensionmap_res.csv`。
2. 确认两个表的细胞 ID、数量和顺序完全一致。
3. 重现 `05_spatial_regression.ipynb` 中的基因表达过滤。
4. 重现压力变换和平滑空间回归。
5. 使用 `helper_functions.R` 拟合 gSEM 残差模型。
6. 使用论文相同的 Benjamini–Hochberg 多重检验校正。
7. 重画：
   - 压力关联火山图；
   - 一个正相关和一个负相关基因的残差回归图；
   - 可选的空间基因表达图。

### 验证标准

- 比较论文突出基因的回归系数方向和近似数值；
- 比较显著基因数量，不要求逐位完全一致；
- 在涉及随机过程时固定随机种子；
- 比较普通线性回归与空间校正回归的差异；
- 确认表达矩阵是否与论文归档版本完全一致。

### 完成定义

在去除平滑空间变化后，仍能恢复一组与细胞压力显著关联的表达程序，并与论文的主要定性结论一致。

## 十、建议记录的复现元数据

每一阶段都应保存：

- Git commit hash；
- Zenodo 版本和文件校验值；
- 操作系统和硬件架构；
- Conda/Mamba 版本；
- 完整环境锁定文件；
- Python、R、NLopt 版本；
- 优化器及参数；
- 随机种子；
- 输入文件路径和哈希；
- 运行时间和峰值内存；
- 输出表的行列数和哈希；
- 与论文图表比较所使用的定量指标。

## 十一、主要参考链接

- [Nature Methods 正式论文](https://www.nature.com/articles/s41592-025-02618-1)
- [PMC 全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978512/)
- [TensionMap GitHub 仓库](https://github.com/Computational-Morphogenomics-Group/TensionMap)
- [官方 README](https://github.com/Computational-Morphogenomics-Group/TensionMap#readme)
- [Notebook 目录](https://github.com/Computational-Morphogenomics-Group/TensionMap/tree/main/notebooks)
- [合成数据教程](https://github.com/Computational-Morphogenomics-Group/TensionMap/blob/main/notebooks/tensionmap_example.ipynb)
- [VMSI 核心实现](https://github.com/Computational-Morphogenomics-Group/TensionMap/blob/main/src/VMSI.py)
- [分割与几何处理代码](https://github.com/Computational-Morphogenomics-Group/TensionMap/blob/main/src/segment.py)
- [最小环境文件](https://github.com/Computational-Morphogenomics-Group/TensionMap/blob/main/tensionmap-minimal.yml)
- [完整环境文件](https://github.com/Computational-Morphogenomics-Group/TensionMap/blob/main/tensionmap-full.yml)
- [Zenodo 数据集 DOI](https://doi.org/10.5281/zenodo.13975707)
- [Zenodo 代码归档 DOI](https://doi.org/10.5281/zenodo.13975227)
- [原始小鼠胚胎 seqFISH 研究](https://www.nature.com/articles/s41587-021-01006-2)
- [TensionMap 公开 issues](https://github.com/Computational-Morphogenomics-Group/TensionMap/issues)

---

本文件仅包含调研与复现规划。目前尚未安装依赖、下载正式数据或修改 TensionMap 源代码。
