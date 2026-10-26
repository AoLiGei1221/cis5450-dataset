# Overture 本地实际schema

`raw_shards`是固定release按加州包络框加约2km过滤的本地导出，21列：16个原始物理字段＋5个audit字段。它不是全球原始分片完整镜像。14个空文件是正常空间过滤结果。

物理`geometry`是WKB binary且没有GeoParquet元数据；坐标为经度／纬度。源查询逻辑schema的`theme/type`来自Hive路径，不在本地物理列中。

## raw_shards 字段类型

| 字段 | 实际Arrow类型 |
|---|---|
| `id` | `string` |
| `geometry` | `binary` |
| `confidence` | `double` |
| `websites` | `list<element: string>` |
| `emails` | `list<element: string>` |
| `socials` | `list<element: string>` |
| `phones` | `list<element: string>` |
| `brand` | `struct<wikidata: string, names: struct<primary: string, common: map<string, string ('common')>, rules: list<element: struct<variant: string, language: string, perspectives: struct<mode: string, countries: list<element: string>>, value: string, between: list<element: double>, side: string>>>>` |
| `addresses` | `list<element: struct<freeform: string, locality: string, postcode: string, region: string, country: string>>` |
| `names` | `struct<primary: string, common: map<string, string ('common')>, rules: list<element: struct<variant: string, language: string, perspectives: struct<mode: string, countries: list<element: string>>, value: string, between: list<element: double>, side: string>>>` |
| `sources` | `list<element: struct<property: string, dataset: string, license: string, record_id: string, update_time: string, confidence: double, between: list<element: double>, provider: string, resource: string, version: string>>` |
| `operating_status` | `string` |
| `basic_category` | `string` |
| `taxonomy` | `struct<primary: string, hierarchy: list<element: string>, alternates: list<element: string>>` |
| `version` | `int32` |
| `bbox` | `struct<xmin: double, xmax: double, ymin: double, ymax: double>` |
| `audit_source_file` | `string` |
| `audit_release` | `string` |
| `audit_scope` | `string` |
| `audit_lon` | `double` |
| `audit_lat` | `double` |

## points 投影字段

22列便读投影，未新增地点；所有原始emails、socials、geometry、完整names/taxonomy仍以raw_shards为准。

| 字段 | 类型 |
|---|---|
| `id` | `string` |
| `name` | `string` |
| `basic_category` | `string` |
| `category` | `string` |
| `hierarchy` | `list<element: string>` |
| `alternate_categories` | `list<element: string>` |
| `confidence` | `double` |
| `operating_status` | `string` |
| `lon` | `double` |
| `lat` | `double` |
| `addresses` | `list<element: struct<freeform: string, locality: string, postcode: string, region: string, country: string>>` |
| `sources` | `list<element: struct<property: string, dataset: string, license: string, record_id: string, update_time: string, confidence: double, between: list<element: double>, provider: string, resource: string, version: string>>` |
| `brand` | `struct<wikidata: string, names: struct<primary: string, common: map<string, string ('common')>, rules: list<element: struct<variant: string, language: string, perspectives: struct<mode: string, countries: list<element: string>>, value: string, between: list<element: double>, side: string>>>>` |
| `websites` | `list<element: string>` |
| `phones` | `list<element: string>` |
| `audit_source_file` | `string` |
| `audit_release` | `string` |
| `audit_scope` | `string` |
| `passes_initial_quality_screen` | `bool` |
| `in_candidate_category_frame` | `bool` |
| `target_review_reason` | `string` |
| `is_strict_target_proxy` | `bool` |

`name/category/hierarchy/alternate_categories`来自names.primary与taxonomy各子字段，`lon/lat`来自audit坐标。`passes_initial_quality_screen/in_candidate_category_frame/target_review_reason/is_strict_target_proxy`是项目最初候选规则，不是当前V3最终筛选或真标签。

## sources中的每个子字段

| 子字段 | 含义 |
|---|---|
| `property` | 对应的属性路径，可能为空或指confidence/status等特定字段 |
| `dataset` | 来源数据集名称；不一定与provider同名 |
| `license` | 来源条目的许可标识，须保留 |
| `record_id` | 来源系统记录编号，非GERS |
| `update_time` | 来源更新时间，非开店日期 |
| `confidence` | 该条来源分值，不一定等于顶层Place confidence |
| `between` | 若适用的几何分段范围；点位常为空 |
| `provider` | 提供方标识；一行可能有多个 |
| `resource` | 来源处理或资源名称，如confidence_calculation |
| `version` | 来源条目的版本，非年度观测 |

实际本地抽样看到meta、overture、foursquare、microsoft、dac、brightquery、alltheplaces、uberall、pinmeto、birdeye、renderseo。来源字段中有CDLA-Permissive-2.0、Apache-2.0和CC0-1.0；Foursquare等是Overture上游来源，不是本项目额外下载的第五套数据。一个Place可以有多个来源条目。完整NOTICE和license随数据保留。

`names/brand.names`的primary是主要名称，common是语言名称映射，rules是名称变体及适用语言／条件。brand.wikidata是品牌Wikidata编号。addresses数组的freeform是街道自由文本，locality是地方名称，postcode邮编，region州／区域，country国家码。网站和电话均为数组，不能默认只有一个值。
