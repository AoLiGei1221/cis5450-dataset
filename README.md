# cis5450-dataset

本仓库供 CIS 5450 项目组共享数据：研究**加州哪些社区值得优先考察开设玩具／潮玩店，以及人口和商业环境中哪些因素值得关注**。全州用于分析，Bay Area 用于重点展示和地理泛化验证。

这里有四个原始数据源、当前 V3 clean 总表、字段字典和完整清洗 Notebook。**一行主表代表一个清洗后的地图零售地点记录，不是一家已经逐店实地核实的玩具店。**

## 先看哪里

| 你要做什么 | 文件或入口 |
|---|---|
| 开始 EDA／后续分类建模 | [`data/clean_v3/california_retail_clean_master_v3.parquet`](data/clean_v3/california_retail_clean_master_v3.parquet) |
| 用 Excel 查看总表 | [同名 CSV](data/clean_v3/california_retail_clean_master_v3.csv)，导入时把 GEOID／邮编设成文本 |
| 先看 30 行 | [`clean_preview_30.csv`](data/clean_v3/clean_preview_30.csv)，只是预览，不能拿它训练模型 |
| 查看全部 51 个字段的含义、单位和用途 | [总表完整字段字典](docs/clean_master_attributes.md) |
| 查看所有 ACS 原始变量的官方解释 | [138 个估计／误差字段映射](docs/acs_variable_dictionary.csv) |
| 下载四个原始数据源 | [固定版本 Data Release](https://github.com/AoLiGei1221/cis5450-dataset/releases/tag/data-v3-2026-10-26) 或下面的下载脚本 |
| 从原始数据重跑清洗 | [`notebooks/California_Retail_Full_Data_Cleaning_V3.ipynb`](notebooks/California_Retail_Full_Data_Cleaning_V3.ipynb) |

**当前主表：58,513 行 × 51 列；548 个目标代理标签、57,965 个比较标签；13 个默认数值预测特征。**社区汇总另有 9,129 行。50,000 行的分析规模来自主表，不是社区表，也不是 50,000 家玩具店。

## 获取数据

```bash
git clone https://github.com/AoLiGei1221/cis5450-dataset.git
cd cis5450-dataset

# 只想先看 clean 数据：clone 后就有，不需要下载大文件。
# 需要完整原始输入：Python 3.12+，脚本只使用标准库。
python scripts/download_raw_data.py

# 可按需下载某一个来源
python scripts/download_raw_data.py --dataset acs
python scripts/download_raw_data.py --verify-only
```

原始文件超过普通 Git 单文件大小限制，实际文件上传在**这个仓库的 Releases**，不是只给第三方网站链接。下载脚本把它们恢复到 `data/raw/` 原目录，并逐个检查 SHA-256。固定清单见 [`manifests/release_assets.json`](manifests/release_assets.json) 和 [`manifests/raw_files.json`](manifests/raw_files.json)。完整下载约 2 GB；保留压缩包、原始文件和重跑输出时应预留约 6 GB 以上空间。

## 四个原始数据源和 attributes

### 1 Overture Maps Places

**用途：商业地点名录。**提供大量真实映射地点，既用来发现玩具／潮玩候选，也用来形成其他零售比较样本以及餐饮、商场、大学等周边环境信息。

- 固定 release：`2026-10-21.0`；官方文档：https://docs.overturemaps.org/guides/places/。
- 文件：`data/raw/overture_ca/raw_shards/part_*.parquet`，16 个本地区域提取文件，合计 **2,375,195 个地点**；另有方便读取的 `points.parquet`。
- 提取范围是加州外接矩形加约 2 km 缓冲，**还未按加州精确边界裁剪，也不全是商店**。本地文件不是全球原始分片的完整镜像。只有两个分片有记录，另外 14 个为空是正常结果。
- [提取与投影 SQL](data/raw/overture_ca/queries.sql)、[来源清单](data/raw/overture_ca/manifest.json)、[实际字段说明](docs/overture_attributes.md)。

| attribute | 含义 | 项目中怎么用 |
|---|---|---|
| `id` | Overture GERS 地点编号 | 去重、来源追溯，不作模型 X |
| `geometry` | 地点几何，当前本地提取为 WKB 二进制 | 空间关联；不能直接当字符串经纬度读 |
| `names.primary` | 主要名称 | 名称标准化、实体匹配、人工核验 |
| `taxonomy.primary` | 主要类别，例如 `toy_store` | 产生候选及代理标签；自身类别不作 X |
| `taxonomy.hierarchy` / `alternates` | 类别层级／备选类别 | 零售范围筛选与模糊类别复查 |
| `basic_category` | 宽泛基础类别 | 初步分类，不能单独证明实体零售性质 |
| `addresses[]` | `freeform/locality/postcode/region/country` 地址数组 | 地址核验、跨来源匹配 |
| `confidence` | 来源记录置信分值 | 来源质量筛选，**不是目标标签正确率** |
| `operating_status` | 来源报告的营业状态 | 排除明确关闭等记录；不是实时营业保证 |
| `websites[]` / `phones[]` | 官网与电话 | 店铺核验、同店匹配 |
| `emails[]` / `socials[]` | 公开来源中的联系／社交信息，可能缺失 | 来源保留；不作模型 X |
| `brand` | 品牌名称／Wikidata 等嵌套信息 | 品牌和门店格式核验 |
| `sources[]` | provider、dataset、record_id、license 等来源信息 | 保留出处、许可和证据；不能丢掉 |
| `version` / `bbox` | 记录版本／几何包络 | 版本与空间审核 |
| `audit_lon` / `audit_lat` | 项目提取的经纬度，单位度 | 便于空间处理 |
| `audit_source_file/release/scope` | 项目添加的分片、release、范围记录 | 复现与追溯 |

`points.parquet` 是 22 列便读投影，包含 `lon/lat/name/category` 和初筛旗标；它不是完整原始 schema。原始提取的几何缺少 GeoParquet 元数据，建议先用 `audit_lon/audit_lat`，或通过 DuckDB spatial 读取 WKB。

### 2 OpenStreetMap California

**用途：另一份地图来源，用来发现可能漏掉的目标店、补充零售证据，并与 Overture 做实体匹配。**OSM 不是营业登记数据库；同一门店可能对应 node 和 way，不能直接把对象数量当门店数量。

- 固定文件：`data/raw/osm/california-261024.osm.pbf`，1,333,570,033 bytes。
- [原始下载地址](https://download.geofabrik.de/north-america/us/california-261024.osm.pbf)，[下载与校验记录](data/raw/osm/california-261024.osm.pbf.download.json)。
- `.osm.pbf` 是二进制地图，不是 CSV。用 PyOsmium／本仓库 Notebook 解析。

| attribute 或 tag | 含义 | 项目中怎么用 |
|---|---|---|
| object type + `id` | `node/way/relation` 及各类型内部编号 | 合起来作为来源对象主键，随后还需跨对象去重 |
| node `lon/lat` | 节点经纬度 | 精确裁剪和空间匹配 |
| way node refs / relation members | 线、面或组合对象的构成 | 组装几何并取内部代表点；不等同店铺入口 |
| `tags` | 不固定字段的 key/value 映射 | 保存原始标注，不能假设每个对象都有同样字段 |
| `shop` | 商店或服务类别，如 `toys/model/games/collector` | 产生候选，`shop=*` 也可能是服务业 |
| `name` / `brand` | 名称、品牌 | 标准化、核验与实体匹配 |
| `addr:*` | 门牌、街道、城市、邮编等 | 地址一致性检查 |
| `website/contact:website`、`phone/contact:phone` | 公开联系方式 | 辅助核验 |
| `opening_hours` | 来源填写的营业时间 | 审核线索，不是实时开门状态 |
| `disused:shop/abandoned:shop/was:shop/closed:shop` | 历史、停用或关闭标记 | 避免把历史对象直接算当前门店 |
| version/timestamp 等元数据 | 若提取文件保留则可用 | 地图编辑信息，不是开店日期；不是每个对象均保留 |

原查询产生的 682 个目标候选是 **OSM 对象候选数**，不是已经核实的 682 家独立玩具店。Overpass 可以用于补充查询；本项目的固定输入是可重复下载的 PBF 快照。

### 3 ACS 2024 Five Year

**用途：给每个 Census Tract 提供人口和社会经济画像，再 JOIN 给位于该 tract 的零售地点。**这是加州专用子集的来源，不需要另找不同口径的“加州人口数据库”。

固定版本是 **2024 ACS 五年估计，统计期 2020–2024**。原始四份 DAT 是全国多个地理层级的汇总表；处理时用 `GEO_ID` 以 `1400000US06` 开头筛出加州 tract，每表得到 9,129 行。它们不是 2026 实时人口。

| 数据表 | 每个统计单元提供什么 | 估计列数量 | 本项目特征 |
|---|---|---:|---|
| `B01001` Sex by Age | 总人口、按性别和年龄组的人口数 | 49 | 人口密度、儿童占比、18–34 岁占比 |
| `B19013` Median Household Income | 家庭收入中位数，2024 年价格美元 | 1 | 收入水平及其 MOE |
| `B14001` School Enrollment | 3 岁及以上人口的入学情况 | 10 | 大学／研究生在读人数占 3 岁以上人口比例 |
| `B11001` Household Type | 家庭户、非家庭户、独居等 | 9 | 家庭户占比、独居户占比 |

| attribute | 含义 |
|---|---|
| `GEO_ID` | 包含地理层级前缀的 Census 标识；筛选加州 tract 后取末 11 位作为 GEOID |
| `B01001_E001/B01001_E002/...` | 原始表内估计列，须按表号和序号解释 |
| `B01001_M001/B01001_M002/...` | 同序号估计的 90% margin of error；不是另一种人口数量 |
| `B01001_003E` 等 | 把 DAT 的 `B01001_E003` 转换为 API／清洗表变量名后的形式 |
| 特殊负值 | Census 缺失／特殊编码，不能直接当负收入或人口 |

表号与含义来自 Census 官方元数据，不靠猜测：[四份原始变量字典](data/raw/census/metadata/)。完整 69 个估计值＋69 个 MOE 的逐字段映射见 [ACS 字段字典](docs/acs_variable_dictionary.csv)，派生公式与读取示例见 [ACS 说明](docs/acs_attributes.md)。

收入字段中的 `250001` 表示 `$250,000+` 的开放顶端区间；当前表保留该数值编码，不能解释为精确收入。MOE 的特殊负值置为空；人口比例的误差区间尚未由组件 MOE 推导。

```python
import pandas as pd
acs = pd.read_csv('data/raw/census/acs2024/acsdt5y2024-b19013.dat', sep='|', dtype={'GEO_ID': 'string'})
ca = acs.loc[acs['GEO_ID'].str.startswith('1400000US06', na=False)].copy()
ca['tract_geoid'] = ca['GEO_ID'].str[-11:]
```

### 4 TIGER Line California Census Tract Boundaries

**用途：社区边界和空间 JOIN。**Tract 是 Census 统计区域，作为本项目的 neighborhood proxy，不等于具有当地名称的真实社区或城市行政区。

- 固定文件：`data/raw/census/tiger2024/tl_2024_06_tract.zip`，2024 年 California Tract，9,129 个多边形。
- [官方下载地址](https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_06_tract.zip)。ZIP 内 `.shp/.shx/.dbf/.prj/.cpg` 要成套保留。

| attribute | 含义及用途 |
|---|---|
| `STATEFP` / `COUNTYFP` / `TRACTCE` | 州、县、tract 编码；加州州码 `06` |
| `GEOID` | 11 位 tract 主键，连接 ACS；必须保留前导零 |
| `GEOIDFQ` | 带地理层级前缀的完整标识 |
| `NAME` / `NAMELSAD` | Census 的 tract 编号名称，不是商业社区名 |
| `MTFCC` / `FUNCSTAT` | 地理实体类别／功能状态 |
| `ALAND` / `AWATER` | 陆地／水域面积，平方米；密度用 `ALAND/1e6` 作平方公里分母 |
| `INTPTLAT` / `INTPTLON` | 官方内部参考点，不应当作每家门店坐标 |
| geometry（由 `.shp` 读取） | tract 面，用于点落在哪个区域的空间关联 |

原始 `.prj` 指定 NAD83 经纬度；处理后门店坐标统一到 EPSG:4326，距离和邻域计算用米制 EPSG:3310。不能用经纬度的“度”直接作为米。

## 四个来源怎样 JOIN

1. Overture 与 OSM 通过名称、坐标、地址、电话等证据做实体匹配，不能直接堆叠两份门店记录。
2. 去重并执行零售范围、地址、来源状态及冲突筛选，保留明确的来源记录和审核裁决。
3. 门店点与 TIGER tract 面做空间 JOIN，得到 `tract_geoid`；精确裁出加州。
4. 用 `tract_geoid = GEOID` 对 ACS 做多对一属性 JOIN，加入人口、年龄、收入等。同 tract 的店铺共享这些统计值，不会因此产生新地点。
5. 计算周围 500 m／1 km 商业环境和最近商场、大学距离。计数排除自身，边界附近使用已下载的周边背景记录。

## Clean 数据集各自是什么

| 文件 | 一行代表什么 | 用途 |
|---|---|---|
| `california_retail_clean_master_v3.parquet/.csv` | 一个 source-qualified 映射零售地点，58,513 行／51 列 | EDA 与代理分类的主表 |
| `california_tract_clean_summary_v3.parquet` | 一个 tract，9,129 行，含零观测门店的区域 | 人口画像、门店数量、社区比较；还没有训练后的选址排名 |
| `source_provenance_v3.parquet` | 主表一个地点的跨源记录，按 `id` JOIN | 原始 Overture／OSM 编号、来源和匹配证据 |
| `context_clean_v3.parquet` | 一个周边环境映射对象，211,627 行，类别可重叠 | 重算邻域计数和最近距离，不是额外独立主表样本 |
| `data/interim/census/ca_acs2024_tract_features.parquet` | 一个 tract，含全部 69 个估计及 MOE 和派生值 | 不重读全国 DAT 即可查看人口层 |

各辅助表的全部实际字段和含义见 [辅助表字段说明](docs/auxiliary_attributes.md)；字段类型与行数快照见 [Parquet schemas](manifests/parquet_schemas.json)。

### 默认用于分类的 13 个 X

| 字段 | 解释／单位 |
|---|---|
| `population_density_per_km2` | tract 总人口／陆地平方公里 |
| `under18_share` | 18 岁以下人口／总人口，0–1 |
| `young_adult_18_34_share` | 18–34 岁人口／总人口，0–1 |
| `median_household_income_2024_usd` | tract 家庭收入中位数，2024 美元 |
| `college_enrolled_share_3plus` | 大学及研究生在读人口／3 岁以上人口，0–1 |
| `family_household_share` | 家庭户／所有住户，0–1 |
| `living_alone_household_share` | 独居住户／所有住户，0–1 |
| `other_retail_count_500m_clean` / `1000m_clean` | 500 m／1 km 内非目标比较零售数量，各一列 |
| `food_count_500m_clean` / `1000m_clean` | 500 m／1 km 内餐饮数量，各一列 |
| `distance_to_mall_m_clean` | 到已下载背景范围内最近映射商场的距离，米 |
| `distance_to_university_m_clean` | 到已下载背景范围内最近映射大学的距离，米 |

以 [`model_feature_spec_v3.json`](data/clean_v3/model_feature_spec_v3.json) 中的白名单为准。名称、品牌、自身类别、来源和审核字段不作 X。`other_target_count_*` 与 `distance_to_other_target_*` 只用于后续竞争／机会筛选，不输入分类器。

### y 与证据等级

- `is_mapped_specialist = 1`：来源及规则支持的玩具／潮玩／TCG／模型专营代理标签，共 548 条；**不是全部人工核实的真标签**。
- `is_mapped_specialist = 0`：当前范围内的比较零售代理标签，共 57,965 条；不意味着现实中绝对不卖玩具。
- `specialist_label_verified`：额外核验子集，41 个正类、1 个负类，其余 NULL 表示未知，**不能填成 0**。
- `retail_evidence_level`：48,706 条为 `source_qualified_map_record`，9,702 条为 `overture_and_osm_goods`，105 条为 `official_address`。官方地址证据与目标店标签核验是不同问题。

清洗和计算通过复现／QA，并不等于全部门店都被证实当前营业。旧审查样本用于修正过记录，不能再把它当作修正后独立总体准确率。地图里没观察到店不代表现实没有店或存在盈利机会。本数据没有利润、租金、空置铺位或真实人流。

## 读取与复现

```python
import pandas as pd
import json

df = pd.read_parquet('data/clean_v3/california_retail_clean_master_v3.parquet')
spec = json.load(open('data/clean_v3/model_feature_spec_v3.json'))
X = df[spec['predictor_allowlist']]
y = df[spec['target']]
print(df.shape, y.value_counts())
```

完整清洗：先下载四来源，再安装固定依赖并从 `notebooks/` 启动 Jupyter：

```bash
python -m pip install -r requirements.txt
python -m pip install notebook
cd notebooks
jupyter notebook California_Retail_Full_Data_Cleaning_V3.ipynb
```

Notebook 的 92 个代码单元包含提取、去重、关联、JOIN、规则清洗和特征计算的实际代码。`cleaning_notebook_inputs/` 是必要的人工审核裁决、冻结研究输入和参照表，不是可随意删除的缓存。它复用已保存审核结论，不会自动重新完成现实门店核验。

此前完整 Run All 已得到与发布版相同的 58,513×51 表和 Parquet SHA-256，见 [`validation/`](validation/)。每次重跑在仓库根目录的 `notebook_runs/` 创建新结果，保留发布表。后续模型应按 tract／地理区域分组验证；不要把同 tract 门店随机拆到训练和测试后宣称空间泛化。

## 来源与许可

© OpenStreetMap contributors, Overture Maps Foundation；OSM California 由 Geofabrik 分发；ACS 与 TIGER/Line 来自 U.S. Census Bureau。保留原始和衍生数据的来源归属。原始来源适用的许可不同，详见 [LICENSE.md](LICENSE.md)、[NOTICE.md](NOTICE.md) 和 [`LICENSES/`](LICENSES/)。本仓库没有把第三方数据统一改成 MIT 许可。
