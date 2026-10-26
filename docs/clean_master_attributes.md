# Clean V3 总表完整字段说明

一行一个规范映射零售地点。58,513行，51列。下表说明全部字段；默认X只有13列，角色以feature spec为准。所有人口统计是所在tract的上下文，不能作为门店自身顾客特征。

| 字段 | 类型 | 单位 | 角色 | 具体解释 |
|---|---|---|---|---|
| `id` | VARCHAR | 标识符 | 审查／上下文／标识，非默认X | 主表地点唯一编号；跨来源实体匹配后的 ID |
| `name` | VARCHAR | 文本 | 审查／上下文／标识，非默认X | 规范门店／地点名称；用于查看及审核，不作为分类输入 |
| `category` | VARCHAR | 类别文本 | 审查／上下文／标识，非默认X | 规范主要类别；来源类别可能有误，亦参与标签形成，不作为 X |
| `basic_category` | VARCHAR | 类别文本 | 审查／上下文／标识，非默认X | 来源宽泛基础类别；不能单独判定是否真实零售 |
| `address` | VARCHAR | 文本 | 审查／上下文／标识，非默认X | 选定的来源街道地址；地址标准化和核验后保留 |
| `locality` | VARCHAR | 文本 | 审查／上下文／标识，非默认X | 来源城市／地方名称，不等于 tract 名称 |
| `postcode` | VARCHAR | 文本 | 审查／上下文／标识，非默认X | 邮编；保留字符串和前导零 |
| `website` | VARCHAR | URL | 审查／上下文／标识，非默认X | 选定公开官网，用于证据和匹配 |
| `phone` | VARCHAR | 文本 | 审查／上下文／标识，非默认X | 选定公开电话，用于实体匹配和核验 |
| `lon` | DOUBLE | 度 | 审查／上下文／标识，非默认X | WGS84 经度；默认只作空间定位和审查 |
| `lat` | DOUBLE | 度 | 审查／上下文／标识，非默认X | WGS84 纬度；默认只作空间定位和审查 |
| `x_m` | DOUBLE | 米 | 审查／上下文／标识，非默认X | EPSG:3310 California Albers 投影横坐标 |
| `y_m` | DOUBLE | 米 | 审查／上下文／标识，非默认X | EPSG:3310 California Albers 投影纵坐标 |
| `tract_geoid` | VARCHAR | 标识符文本 | 审查／上下文／标识，非默认X | 所属 Census Tract 的 11 位 GEOID；连接社区层 |
| `county_geoid` | VARCHAR | 标识符文本 | 审查／上下文／标识，非默认X | 5 位州加县 FIPS；用于地理分组 |
| `county_block_id` | VARCHAR | 标识符文本 | 审查／上下文／标识，非默认X | 当前值等于县 GEOID，是县级分组标识，并非另建精细网格 |
| `is_bay_area_9county` | BOOLEAN | 布尔 | 审查／上下文／标识，非默认X | 是否属于项目定义的湾区九县；用于分组与地图 |
| `population` | BIGINT | 人 | 审查／上下文／标识，非默认X | 所在 tract 的 ACS 常住总人口，不是门店客流 |
| `households` | BIGINT | 户 | 审查／上下文／标识，非默认X | 所在 tract 的全部住户数，非人数 |
| `land_area_km2` | DOUBLE | 平方公里 | 审查／上下文／标识，非默认X | 所在 tract 的 TIGER 陆地面积，不含水域 |
| `acs_period` | VARCHAR | 期间文本 | 审查／上下文／标识，非默认X | ACS 统计期标记；不是2026实时观测 |
| `population_density_per_km2` | DOUBLE | 人／平方公里 | X 预测输入 | tract 常住人口除以陆地面积 |
| `under18_share` | DOUBLE | 比例0–1 | X 预测输入 | 男性及女性 0–17 岁人口数除以全部人口 |
| `young_adult_18_34_share` | DOUBLE | 比例0–1 | X 预测输入 | 男性及女性 18–34 岁人口数除以全部人口 |
| `median_household_income_2024_usd` | BIGINT | 2024年美元 | X 预测输入 | tract 家庭收入中位数；250001表示$250,000+开放顶端区间，非精确值 |
| `median_household_income_moe` | BIGINT | 2024年美元 | 审查／上下文／标识，非默认X | B19013 家庭收入中位数的90%误差边界；特殊代码置NULL |
| `income_relative_moe` | DOUBLE | 比率 | 审查／上下文／标识，非默认X | 收入MOE／收入估计，用于不确定性提示；缺失保留NULL |
| `college_enrolled_share_3plus` | DOUBLE | 比例0–1 | X 预测输入 | 本科及研究生／专业课程在读人口除以3岁及以上人口；不是学历比例 |
| `family_household_share` | DOUBLE | 比例0–1 | X 预测输入 | 家庭户除以全部住户；不等同有小孩家庭比例 |
| `living_alone_household_share` | DOUBLE | 比例0–1 | X 预测输入 | 独居住户除以全部住户；不是独居人口占全部人口 |
| `confidence` | DOUBLE | 分值 | 审查／上下文／标识，非默认X | 地图来源置信分值，不是玩具标签的真实性概率 |
| `operating_status` | VARCHAR | 类别文本 | 审查／上下文／标识，非默认X | 来源报告的营业状态，存在时间滞后 |
| `source_provider` | VARCHAR | 来源文本 | 审查／上下文／标识，非默认X | Overture／OSM／跨来源匹配标识；细粒度上游见provenance |
| `is_mapped_specialist` | BIGINT | 二元0或1 | y 代理目标 | 目标代理标签，1=来源与规则支持的专营目标店，0=比较零售；不是盈利标签 |
| `specialist_label_verified` | BIGINT | 可空二元 | 审查／上下文／标识，非默认X | 额外官方证据支持的目标身份：1正类、0负类、NULL未知；不得把NULL填0 |
| `specialist_label_basis` | VARCHAR | 文本 | 审查／上下文／标识，非默认X | 该行目标代理／核验裁决所依据的规则或证据说明 |
| `retail_evidence_level` | VARCHAR | 类别文本 | 审查／上下文／标识，非默认X | source_qualified_map_record / overture_and_osm_goods / official_address，表示零售范围证据 |
| `target_subtype` | VARCHAR | 可空文本 | 审查／上下文／标识，非默认X | 目标零售的细分标签／审核分类，依现存规则；不作为X |
| `audit_evidence_url` | VARCHAR | 可空URL | 审查／上下文／标识，非默认X | 支持审核裁决的公开来源页面；空值不表示已核验 |
| `snapshot_date` | VARCHAR | 日期文本 | 审查／上下文／标识，非默认X | 当前地点来源／发布快照日期，不是开店日期 |
| `coordinate_crs` | VARCHAR | CRS文本 | 审查／上下文／标识，非默认X | lon/lat 所用坐标参考系标记 |
| `metric_crs` | VARCHAR | CRS文本 | 审查／上下文／标识，非默认X | x_m/y_m与距离所用投影参考系标记 |
| `other_retail_count_500m_clean` | BIGINT | 个 | X 预测输入 | 500米内通过规则的非目标比较零售背景数量，留一排除自身 |
| `other_retail_count_1000m_clean` | BIGINT | 个 | X 预测输入 | 1000米内通过规则的非目标比较零售背景数量，留一排除自身 |
| `food_count_500m_clean` | BIGINT | 个 | X 预测输入 | 500米内通过背景规则的餐饮映射对象数 |
| `food_count_1000m_clean` | BIGINT | 个 | X 预测输入 | 1000米内通过背景规则的餐饮映射对象数 |
| `other_target_count_500m_clean` | BIGINT | 个 | 审查／上下文／标识，非默认X | 500米内其他目标代理店数量；仅竞争筛选使用，不作X |
| `other_target_count_1000m_clean` | BIGINT | 个 | 审查／上下文／标识，非默认X | 1000米内其他目标代理店数量；仅竞争筛选使用，不作X |
| `distance_to_other_target_m_clean` | DOUBLE | 米 | 审查／上下文／标识，非默认X | 到另一目标代理记录的最近投影距离，排除自身；仅筛选使用 |
| `distance_to_mall_m_clean` | DOUBLE | 米 | X 预测输入 | 已下载背景范围内最近映射商场的投影距离；受范围和覆盖约束 |
| `distance_to_university_m_clean` | DOUBLE | 米 | X 预测输入 | 已下载背景范围内最近映射大学的投影距离；受范围和覆盖约束 |

更多约束见 [`model_feature_spec_v3.json`](../data/clean_v3/model_feature_spec_v3.json)。

NULL表示未知或不可计算，不是0。当前13个X均无缺失是主表筛选结果，不表示全部9,129个tract均有完整人口估计。
实体店营业真实性、地图覆盖和标签正确性仍有限制。面积、距离单位和比例分母必须按这里的定义使用。
