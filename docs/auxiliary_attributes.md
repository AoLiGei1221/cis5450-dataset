# 辅助数据表字段说明

原始ACS各估计及MOE的138个字段已逐一列在[ACS字典](acs_variable_dictionary.csv)。下表列出辅助表中所有其余字段。`B...E/M`为原始统计值，不代表额外地点或年份。

## california_tract_clean_summary_v3.parquet

9,129行，166列。

| 字段 | 类型 | 含义 |
|---|---|---|
| `GEOID` | string | 11位tract连接键，字符串；主表中叫tract_geoid |
| `NAME` | string | Census tract显示名，不是当地商业社区名称 |
| `acs_period` | string | ACS 统计期标记；不是2026实时观测 |
| `population` | int64 | 所在 tract 的 ACS 常住总人口，不是门店客流 |
| `under18_count` | int64 | 男性及女性0–17岁总人数 |
| `under18_share` | double | 男性及女性 0–17 岁人口数除以全部人口 |
| `young_adult_18_34_count` | int64 | 男性及女性18–34岁总人数 |
| `young_adult_18_34_share` | double | 男性及女性 18–34 岁人口数除以全部人口 |
| `median_household_income_2024_usd` | int64 | tract 家庭收入中位数；250001表示$250,000+开放顶端区间，非精确值 |
| `median_household_income_moe` | int64 | B19013 家庭收入中位数的90%误差边界；特殊代码置NULL |
| `population_age3plus` | int64 | 3岁及以上常住人口，college比例分母 |
| `college_enrolled_count` | int64 | 本科及研究生／专业课程在读人数 |
| `college_enrolled_share_3plus` | double | 本科及研究生／专业课程在读人口除以3岁及以上人口；不是学历比例 |
| `households` | int64 | 所在 tract 的全部住户数，非人数 |
| `family_household_share` | double | 家庭户除以全部住户；不等同有小孩家庭比例 |
| `living_alone_household_share` | double | 独居住户除以全部住户；不是独居人口占全部人口 |
| `STATEFP` | string | 2位州FIPS，加州06 |
| `COUNTYFP` | string | 州内3位县FIPS |
| `county_geoid` | string | 5 位州加县 FIPS；用于地理分组 |
| `county_block_id` | string | 当前值等于县 GEOID，是县级分组标识，并非另建精细网格 |
| `is_bay_area_9county` | bool | 是否属于项目定义的湾区九县；用于分组与地图 |
| `ALAND` | int64 | 陆地平方米 |
| `AWATER` | int64 | 水域平方米 |
| `land_area_km2` | double | 所在 tract 的 TIGER 陆地面积，不含水域 |
| `water_area_km2` | double | 水域平方公里 |
| `population_density_per_km2` | double | tract 常住人口除以陆地面积 |
| `clean_retail_rows` | int64 | 该tract主表记录数；0表示未观察到合格记录 |
| `mapped_specialist_rows` | int64 | 该tract主表目标代理记录数；不是核实的真实市场供给 |

## source_provenance_v3.parquet

58,513行，6列。

| 字段 | 类型 | 含义 |
|---|---|---|
| `id` | string | 主表地点唯一编号；跨来源实体匹配后的 ID |
| `overture_ids_json` | string | JSON数组：匹配保留的Overture/GERS编号 |
| `osm_ids_json` | string | JSON数组：匹配保留的OSM type+ID编号 |
| `overture_sources_json` | string | JSON数组：Overture原始sources的provider/dataset/license等 |
| `source_osm_json` | string | JSON保存的OSM来源对象与标注记录 |
| `osm_scope_evidence_json` | string | JSON保存的OSM零售范围证据 |

## context_clean_v3.parquet

211,627行，9列。

| 字段 | 类型 | 含义 |
|---|---|---|
| `id` | string | 主表地点唯一编号；跨来源实体匹配后的 ID |
| `name` | string | 规范门店／地点名称；用于查看及审核，不作为分类输入 |
| `x_m` | double | EPSG:3310 California Albers 投影横坐标 |
| `y_m` | double | EPSG:3310 California Albers 投影纵坐标 |
| `other_retail` | bool | 是否属于通过范围规则的非目标比较零售背景；布尔 |
| `target` | bool | 是否属于目标代理店背景；布尔 |
| `food` | bool | 是否属于餐饮背景；布尔 |
| `mall` | bool | 是否属于商场背景；布尔 |
| `university` | bool | 是否属于大学背景；布尔 |

## ca_acs2024_tract_features.parquet

9,129行，164列。

| 字段 | 类型 | 含义 |
|---|---|---|
| `GEOID` | string | 11位tract连接键，字符串；主表中叫tract_geoid |
| `NAME` | string | Census tract显示名，不是当地商业社区名称 |
| `acs_period` | string | ACS 统计期标记；不是2026实时观测 |
| `population` | int64 | 所在 tract 的 ACS 常住总人口，不是门店客流 |
| `under18_count` | int64 | 男性及女性0–17岁总人数 |
| `under18_share` | double | 男性及女性 0–17 岁人口数除以全部人口 |
| `young_adult_18_34_count` | int64 | 男性及女性18–34岁总人数 |
| `young_adult_18_34_share` | double | 男性及女性 18–34 岁人口数除以全部人口 |
| `median_household_income_2024_usd` | int64 | tract 家庭收入中位数；250001表示$250,000+开放顶端区间，非精确值 |
| `median_household_income_moe` | int64 | B19013 家庭收入中位数的90%误差边界；特殊代码置NULL |
| `population_age3plus` | int64 | 3岁及以上常住人口，college比例分母 |
| `college_enrolled_count` | int64 | 本科及研究生／专业课程在读人数 |
| `college_enrolled_share_3plus` | double | 本科及研究生／专业课程在读人口除以3岁及以上人口；不是学历比例 |
| `households` | int64 | 所在 tract 的全部住户数，非人数 |
| `family_household_share` | double | 家庭户除以全部住户；不等同有小孩家庭比例 |
| `living_alone_household_share` | double | 独居住户除以全部住户；不是独居人口占全部人口 |
| `STATEFP` | string | 2位州FIPS，加州06 |
| `COUNTYFP` | string | 州内3位县FIPS |
| `county_geoid` | string | 5 位州加县 FIPS；用于地理分组 |
| `county_block_id` | string | 当前值等于县 GEOID，是县级分组标识，并非另建精细网格 |
| `is_bay_area_9county` | bool | 是否属于项目定义的湾区九县；用于分组与地图 |
| `ALAND` | int64 | 陆地平方米 |
| `AWATER` | int64 | 水域平方米 |
| `land_area_km2` | double | 所在 tract 的 TIGER 陆地面积，不含水域 |
| `water_area_km2` | double | 水域平方公里 |
| `population_density_per_km2` | double | tract 常住人口除以陆地面积 |

Context的五个类别可以重叠，不能相加当主表样本量。Context坐标EPSG:3310，单位米；范围受原始下载矩形及现有覆盖限制。
