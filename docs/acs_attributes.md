# ACS 原始字段和派生公式

2024 ACS five-year统计期为2020–2024。原始全国DAT为UTF-8、`|`分隔且有一行header；每张表首个数据行为全国，不是加州。筛选`GEO_ID.startswith("1400000US06")`后各有9,129个唯一tract；去掉`1400000US`获得11位GEOID，保留为字符串。

## 两种变量命名

原始Summary File：`B01001_E001` / `B01001_M001`。API与当前处理表：`B01001_001E` / `B01001_001M`。两种写法是同一变量，不能再把它们当独立特征。完整138列映射、官方concept与label见[acs_variable_dictionary.csv](acs_variable_dictionary.csv)，原始JSON保存在`data/raw/census/metadata/`。

| 表 | 人口总体或统计量 | 原始列数（含GEO_ID） |
|---|---|---:|
| B01001 | Sex by Age；总人口及按性别细分年龄 | 99 |
| B19013 | Median Household Income in 2024 inflation-adjusted dollars | 3 |
| B14001 | Enrollment by level for population aged 3 and over | 21 |
| B11001 | Household Type Including Living Alone | 19 |

## 当前七个人口和面积特征

以下使用API／处理表命名，`sum(a…b)`表示包括两端的序号范围。比例都在0–1，不是0–100。

| 派生字段 | 计算方法 | 分母含义 |
|---|---|---|
| population_density_per_km2 | B01001_001E / (ALAND / 1e6) | 陆地平方公里 |
| under18_share | [sum(B01001_003E…006E) + sum(B01001_027E…030E)] / B01001_001E | 全部常住人口 |
| young_adult_18_34_share | [sum(B01001_007E…012E) + sum(B01001_031E…036E)] / B01001_001E | 全部常住人口 |
| median_household_income_2024_usd | B19013_001E | 无比率分母，是家庭收入中位数 |
| college_enrolled_share_3plus | (B14001_008E + B14001_009E) / B14001_001E | 3岁及以上人口；不是仅年轻人口 |
| family_household_share | B11001_002E / B11001_001E | 全部住户 |
| living_alone_household_share | B11001_008E / B11001_001E | 全部住户；008是独居，007是全部非家庭户 |

## 误差和特殊编码

`M`是90% margin of error，单位与其估计值一致，不是另一条观测。原始DAT保留所有编码；当前处理层把这些表里的特殊负数和非数字记号保守置为NULL。不要把负数当负人口，也不要把NULL填0。

加州B19013共有122个缺失收入估计；164个tract的估计为`250001`、原始MOE为`-333333333`，表示`$250,000+`开放顶端区间。当前数值列保留250001编码，模型解释及敏感性分析必须考虑此限制。收入MOE合计286个NULL。`income_relative_moe = median_household_income_moe / median_household_income_2024_usd`。

总人口、住户、面积为0时派生比例保留NULL。全部69个原始MOE保存在处理表中，但没有为年龄合计、密度或比例计算派生置信区间；不能直接相加MOE。

四表没有族裔变量、消费支出、租金、客流或盈利数据。所需新字段须另加真实来源，不应从现有字段编造。

官方参考：[Census特殊编码](https://www.census.gov/data/developers/data-sets/acs-1year/notes-on-acs-estimate-and-annotation-values.html)、[ACS误差与质量定义](https://www.census.gov/programs-surveys/acs/methodology/sample-size-and-data-quality/sample-size-definitions.html)。
