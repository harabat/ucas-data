# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # UCAS data analysis

# %% [markdown]
# ---

# %% [markdown]
# ## Context

# %% [markdown]
# [Map POLAR4](https://tableau.hefce.ac.uk/t/Public/views/InteractivemapMarch2021/POLAR4)
#
# [Map Index of Multiple
# Deprivation 2019](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/833959/IoD2019_Infographic.pdf)
#
# Information about POLAR4
#
# <details>
#     
# - Sources: 
#     - https://www.officeforstudents.org.uk/data-and-analysis/young-participation-by-area/about-polar-and-adult-he/
#     - https://www.officeforstudents.org.uk/media/cd78246d-0072-4e2f-a25a-42ba54deea11/polar-and-tundra-faqs-september2020.pdf
#     
# - The young participation rate is calculated by dividing the number of young people from each area who enter higher education aged 18 or 19 by the young population of that area. POLAR4 was calculated using data on students who begun their studies between 2009-10 and 2013-14. The areas are then ranked by participation rate and split into five quintiles, each of which represents about a fifth of the young population. POLAR4 does not limit the student population by school type and does not track individual students. 
#     
# - Area-based measures can be used:
#     - to compare areas across the UK
#     - to identify areas with the lowest young participation in higher education
#     - to evaluate whether gaps in participation have changed year on year
#     - to compare relative levels of participation in higher education across the UK
#     - as part of an assessment of the background of an individual. When making background assessments these measures should never be used alone and only with other information.
#     
# - [...] most people are more likely to enter higher education when they are young. The biggest single year of age in higher education are those who enter aged 18, and more than half of undergraduate entrants and over two-thirds of full-time undergraduate entrants are under 21. [...] Mature participation is important, but needs a different approach, considering the proportion of the population that already have a higher education qualification.
#
# - The original research for POLAR showed that, in many parts of the UK, low participation areas were also the areas with the highest measures of socio-economic disadvantage, but this was not the only factor in determining participation in higher education. Other factors that influence the level of young participation in an area include:
#     - the ethnicity profile of the area
#     - the adult education level amongst the population
#     - the relative school outcomes of the area
#     - the availability of local, accessible higher education places
#     - the availability of alternative post-school pathways.
#     
# - London is the region of the UK with the highest number of small areas that are simultaneously classified as deprived using the Index of Multiple Deprivation (IMD), and [not classified as low participation](https://www.ucas.com/file/65656/download?token=VgsvkzN7) using POLAR4 or TUNDRA.
#
# - [...] area-based measures are not a measure of socio-economic disadvantage, of either the individual or of areas.
#
# - For an area based measure such as POLAR, this may mean that participation rates for state school may be masked by higher participation rates of independent schools in the area. For outreach and access and participation programmes, this masking may mean that certain areas could be excluded from potential funding and opportunities. TUNDRA’s purpose is to reveal such areas.
#     
# </details>

# %% [markdown]
# Observations:
# - Apart from London, areas with least participation (POLAR4 and TUNDRA) are correlated with most deprived areas (IMD) 
# - Reference points: universities that appear close (±5) to UoB on [at least 2 rankings](https://en.wikipedia.org/wiki/Rankings_of_universities_in_the_United_Kingdom) (the ones marked with \* are within ±3 places):
#     - University of Manchester *
#     - University of Sheffield *
#     - University of East Anglia *
#     - Queen's University Belfast
#     - University of Exeter
#     - University of Nottingham 
#     - Heriot-Watt University
# - Models: universities that are 5-10 places higher on at least 2 rankings: 
#     - King's College London
#     - University of York

# %% [markdown]
# Information on UoB's WP efforts:
# - some criticism of UoB for slashing budgets on WP efforts in recent years: https://nitter.pussthecat.org/PrecariousBrum/status/1268135554815844353

# %% [markdown]
# ---

# %% [markdown]
# ## Exploratory

# %%
import pandas as pd
from pandas_profiling import ProfileReport
import seaborn
sns.set_theme()
import altair as alt

# %%
# %matplotlib inline

# %%
data = pd.read_csv('./UCAS_data_file.csv')

# %%
data.info()

# %%
# profile = ProfileReport(data, title="Pandas Profiling Report")
# profile

# %% [markdown]
# The profile generated by `pandas-profiling` tells us the following:
#
# - `inst_all` and `INSTITUTION_CODE` have a high cardinality: 132 distinct values 
# - `Cycle` is a time period (year)
# - high correlation between `statistic` and `agegroup`
# - `value` has 7133 (1.8%) missing values 
# - `value` has 4606 (1.2%) zeros 

# %% [markdown]
# ---

# %% [markdown]
# ## Data cleaning

# %% [markdown]
# Let's have a closer look at the columns we're working with.

# %%
for i in data.columns[2:-1]:
    print(
        f'Unique values for {i}:\n'
        f'\t{data[i].unique()}\n'
    )

# %% [markdown]
# ### `inst_all` and `INSTITUTION_CODE`

# %% [markdown]
# We know that `inst_all` might be codified by `INSTITUTION_CODE`: after checking that, we drop `INSTITUTION_CODE`. 

# %%
data[['inst_all', 'INSTITUTION_CODE']]

# %%
all(data['inst_all'].apply(lambda x: x[:3]) == data['INSTITUTION_CODE'])

# %%
data = data.drop(columns='INSTITUTION_CODE')

# %% [markdown]
# ---

# %% [markdown]
# ### `value`

# %% [markdown]
# #### Negative values

# %% [markdown]
# Let's look at `value`. 

# %%
data['value'].describe()

# %% [markdown]
# We can see that the minimum is negative, which means that there are some negative values in this column. It looks like an input error (we're counting people after all), let's check. 

# %%
data.loc[data['value'] < 0]['statistic'].unique()

# %% [markdown]
# The only negative values refer to a negative percentage point difference between offer rate and average offer rate: this is not an error. 

# %% [markdown]
# ---

# %% [markdown]
# #### Null values

# %% [markdown]
# We know that there's a small amount of null values: it's probable that most of these values aren't missing but simply null (no applicants of `Asian ethnic group` in a given year, for example), but we want to check whether missing values are limited to a single university or specific columns. 

# %%
data_null = data.loc[data["value"] == 0]

for i in data_null.columns[:-1]:
    print(
        f'Unique values for {i}:\n'
        f'\t{data_null[i].unique()}\n'
    )

# %% [markdown]
# Doesn't seem like the problem is with a single university. 

# %% [markdown]
# Let's check whether any university has all null values:

# %%
data.groupby('inst_all').max()['value'].apply(int).sort_values().reset_index()

# %%
data.groupby(['Cycle', 'inst_all']).max()\
.reset_index().reindex(columns=['inst_all', 'Cycle', 'value'])\
.sort_values(['value', 'inst_all', 'Cycle'])\
.loc[lambda x: x['value'] == 0]

# %% [markdown]
# We can see that A66, W01, and W05 seemingly are missing some values for the first few years of the dataset: we could drop only the missing years, but, given that these 3 universities represent a very small part of the data, we can afford to drop them entirely without it affecting our analysis. 

# %%
data = data.loc[
    ~data['inst_all'].str.startswith('A66')
    & ~data['inst_all'].str.startswith('W01')
    & ~data['inst_all'].str.startswith('W05')
]

# %% [markdown]
# ---

# %% [markdown]
# #### Missing values

# %% [markdown]
# We also know that there are some missing values. 

# %%
data_na = data.loc[data['value'].isna()]

for i in data_na.columns[:-1]:
    print(
        f'Unique values for {i}:\n'
        f'\t{data_na[i].unique()}\n'
    )

# %% [markdown]
# The missing values can be found in all universities, but are limited to the `statistic` values `Average offer rate`, `Percentage point difference between offer rate and average offer rate`, `Contribution of group to the average offer rate`, and `Offer rate`. 

# %% [markdown]
# In theory, these missing values can be determined from the data. For example, after reading the UCAS dataset guidelines and playing with the values, we determine the following:
#
# - $\text{Offer rate} = \frac{\text{Offers}}{\text{June deadline applicants}}$
#
# - $\text{Percentage point difference between offer rate and average offer rate} = \text{(Offer rate - Average offer rate)} * 100$

# %% [markdown]
# However, we'll leave the missing values for now, as we're unlikely to be looking into them in our analysis. 

# %% [markdown]
# ---

# %% [markdown]
# ### `agegroup`

# %% [markdown]
# Let's check whether we can afford looking at 18 year olds only. 
#
# If `18 years old` represents the majority of values, we can drop the `All ages` rows. 

# %%
# create dataframe that contains totals for each statistic
# and only the absolute values (we drop rates, percentages, etc.)
agegroup_data = data.loc[
    (data['equality_dimension'] == 'Total')
    & (~data['statistic'].str.contains('|'.join(['per 10', 'rate', 'percent'])))
].drop(
    columns='equality_dimension'
)

# create separate dataframes for `18 years old` and `All ages`
agegroup_18_data = agegroup_data.loc[agegroup_data['agegroup'] == '18 year olds'].drop(columns='agegroup')
agegroup_all_data = agegroup_data.loc[agegroup_data['agegroup'] != '18 year olds'].drop(columns='agegroup')

# merge the above dataframes (left join on non-value columns)
agegroups_data = pd.merge(
    agegroup_18_data,
    agegroup_all_data,
    how='right',
    left_on=['inst_all', 'Cycle', 'statistic'],
    right_on=['inst_all', 'Cycle', 'statistic'],
    suffixes=('_18yo', '_all')
)

# create column with ratio of `18 years old` compared to `All ages`
agegroups_data['18yo_proportion'] = agegroups_data['value_18yo'] / agegroups_data['value_all']

agegroups_data.sort_values('18yo_proportion')

# %%
# histogram of proportion of 18yo for `statistic` measures
sns.histplot(data=agegroups_data.dropna()['18yo_proportion'], stat='percent')

# %% [markdown]
# It seems that, for most `statistic` measures, `18 years old` represents 40-70% of `All ages`. 
#
# We'll lose a large amount of information by only looking at 18yo applicants. However, the data task specifically requires to advise UoB on the effects of WP policies on the participation of Year 13 students, which are largely 18yo. Moreover, [OfS states](https://www.officeforstudents.org.uk/media/cd78246d-0072-4e2f-a25a-42ba54deea11/polar-and-tundra-faqs-september2020.pdf) that "The biggest single year of age in higher education are those who enter aged 18 [...] Mature participation is important, but needs a different approach, considering the proportion of the population that already have a higher education qualification."
#
# Consequently, we drop `All ages` and only focus on `18 year olds`. 

# %%
data = data.loc[data['agegroup'] != 'All ages'].reset_index(drop=True)

# %% [markdown]
# ---

# %% [markdown]
# ### `equality_dimension`

# %% [markdown]
# Let's have a closer look at the `equality_dimension` column. 

# %%
# abs_rows = [row for row in data['equality_dimension'].unique() if all(match not in row for match in ['per 10', 'rate', 'percent'])]

ethnicity_cols = [col for col in data['equality_dimension'].unique() if 'ethnic' in col]
gender_cols = [col for col in data['equality_dimension'].unique() if 'en' in col]
polar_cols = [col for col in data['equality_dimension'].unique() if 'POLAR' in col]

print(
    f'ethnicity_cols:\n\t{ethnicity_cols}\n\n'
    f'gender_cols:\n\t{gender_cols}\n\n'
    f'polar_cols:\n\t{polar_cols}\n\n'
)

# %% [markdown]
# The `equality_dimension` column splits the students along various axes, namely POLAR4, ethnicity, and sex. 
#
# The data task specifically requires to look at Widening Participation efforts with respect to POLAR4 and IMD criteria. Consequently, we will drop the information relating to ethnicity and sex. 

# %%
data = data.loc[data['equality_dimension'].isin(polar_cols)]

# %% [markdown]
# ### `statistic`

# %%
data['statistic'].unique()

# %% [markdown]
# We won't touch the `statistic` column for now, but wait until we know what we want to be looking at.

# %%
data.to_csv('./data_clean.csv')

# %% [markdown]
# ## Data analysis

# %% [markdown]
# ### UoB

# %% [markdown]
# We are working with `University of Birmingham`. 

# %%
# unique values in `inst_all` that contain 'University of Birmingham'
data[data['inst_all'].str.contains('University of Birmingham', case=False)]['inst_all'].unique()

# %% [markdown]
# ### Reference points and model universities

# %% [markdown]
# We identified several universities that are similar enough to University of Birmingham to serve as reference points. 
#
# Our methodology for achieving this was quite crude: we identified universities that appeared close to University of Birmingham in the [3 main rankings of UK universities for 2022](https://en.wikipedia.org/wiki/Rankings_of_universities_in_the_United_Kingdom). This is not perfect, as, for example, UoB has dropped many places in 2022 on [at least one of the rankings](https://www.thecompleteuniversityguide.co.uk/universities/university-of-birmingham#subSec_leaguetableperformance) and one of our model universities is in London, which is a [major outlier in the UK in terms of POLAR4 quintiles](https://www.ucas.com/file/65656/download?token=VgsvkzN7). However, [cross-checking with other sources](https://www.universityrankings.ch/compare?id[]=5256&id[]=5288&id[]=5267&id[]=5321&id[]=5300&global=all) does not uncover any major issues with our picks: we will consider this sufficient for the current exploratory analysis, given the time constraints. 

# %% [markdown]
# Our reference points are universities that appear close (±3) to UoB on [at least 2 out of 3 rankings](https://en.wikipedia.org/wiki/Rankings_of_universities_in_the_United_Kingdom):
# - University of Manchester
# - University of Sheffield
# - University of East Anglia

# %%
data[data['inst_all'].str.contains(
    '|'.join(['University of Manchester', 'University of Sheffield', 'University of East Anglia']), 
    case=False
)]['inst_all'].unique()

# %% [markdown]
# We have also identified models (universities that are 5-10 places higher on at least 2 out of 3 rankings): 
# - King's College London
# - University of York

# %%
data[data['inst_all'].str.contains(
    '|'.join(["King.?s College London", 'University of York']), 
    case=False
)]['inst_all'].unique()

# %% [markdown]
# ### `universities_data`

# %% [markdown]
# Let's create the dataframe that will hold the data we want to look at: the POLAR4 data for our 6 universities over 2010-2021. 

# %%
# create df with UoB, the reference universities, and the model ones
universities_data = data[data['inst_all'].str.contains(
    '|'.join(['B32', 'M20', 'E14', 'S18', 'K60', 'Y50']), 
    case=False
)]

# %% [markdown]
# Let's check that there's no missing data among our reference points and models. 

# %%
any(universities_data['value'].isna())

# %% [markdown]
# No missing data: we continue.

# %% [markdown]
# Now that we're working with a small number of universities, we can afford to pivot the dataframe to a more meaningful form, just to have a better understanding of what features of the data we want to be exploring. 

# %%
universities_data.pivot_table(
    index=['inst_all', 'statistic', 'equality_dimension'],
    columns='Cycle',
    values='value'
)

# %% [markdown]
# Let's make some visualisations. 

# %% [markdown]
# ### `POLAR4` depending on various `statistic` values

# %% [markdown]
# We want to look at aspects of the data that are not already covered by UCAS [in their (very basic) reports](https://www.ucas.com/file/144876/download?token=hr_HRBqo#page=7). 

# %% [markdown]
# First, we need to prepare our dataframe for our visualisation library (altair). 

# %%
# altair requires datetime column for plotting time series
universities_data.loc[:, 'Cycle'] = pd.to_datetime(universities_data['Cycle'], format='%Y')

# altair requires a list of labels to sort faceted charts
universities_order = [
    'B32 University of Birmingham',
    'M20 University of Manchester',
    'E14 University of East Anglia UEA',
    'S18 University of Sheffield',
    'K60 Kings College London University of London',
    'Y50 University of York'
]

# %% [markdown]
# #### Offer rate

# %% [markdown]
# First, we'll look into the `Offer rate` depending on the POLAR4 quintile in our different universities. 

# %%
# create df with `Offer rate` data
offer_rate = universities_data[universities_data['statistic'] == 'Offer rate']

# %%
# plot offer rates in 2010-2021 by university (faceted line plot)
chart = alt.Chart(offer_rate)\
.mark_line(point=True)\
.encode(
    x=alt.X('Cycle:T', title='Year'),
    y=alt.Y('value:Q', title='Offer rate'),
    color=alt.Color('equality_dimension:N', title='POLAR4'),
    tooltip=(
        alt.Tooltip('inst_all:N', title='University'),
        alt.Tooltip('equality_dimension:N', title='POLAR4'),
        alt.Tooltip('value:Q', title='Offer rate'),
    )
)\
.facet(
    facet=alt.Facet('inst_all:N', title=None, sort=universities_order),
    columns=2,
    title={
        'text': 'Offer rate in 2010-2021 by university',
        'anchor': 'middle',
        'fontSize': 15,
        'dy': -10
    }
)

chart

# %% [markdown]
# **Main point: UoB has a historically wide and stagnating amplitude between offer rates for Q1 and Q5, while most other universities in our benchmark either have a narrow amplitude or are strongly improving.**
#
# ---
#
# We notice that UoB has historically had a very wide amplitude between the offer rates for lower POLAR4 quintiles (Q1-Q3) and the higher ones (Q4-Q5). 
#
# Indeed, the offer rates for Q5 in the considered period have been above 80%, sometimes as high as 90%. In contrast, the offer rates for Q1 (and Q2) have been below 70%, and close to 60%. Historically, we observe Q5 offer rates at 15-20 percentage points above those for Q1-Q2. 
#
# Manchester has a similar amplitude and a similar track record to University of Birmingham. 
#
# East Anglia, Sheffield, and King's College London all have much narrower offer rate ranges (~10 percentage points). York, while its track record is similar to UoB's, has been drastically improving since 2016. 
#
# The trend of levelling offer rates across POLAR4 quintiles is much more noticeable, in general for our reference points and models (Q1 > Q5 for King's in 2021!), while UoB and Manchester are stagnating at very wide amplitudes. 

# %% [markdown]
# #### Placed June deadline applicants

# %% [markdown]
# Let's look at the absolute values for `Placed June deadline applicants`. 
#
# We could be looking at `All placed applicants`, but `Offer rates` is calculated based on the number of `June deadline applications`, so it directly affects primarily the June deadline applicants. This population represents a vast majority of `All placed applicants` anyway. 

# %%
# create df with `Placed June deadline applicants` data
placed_applicants = universities_data[universities_data['statistic'] == 'Placed June deadline applicants']

# %%
# plot placed June deadline applicants in 2010-2021 by university (faceted stacked area plot)
chart = alt.Chart(placed_applicants)\
.mark_area(opacity=.8, stroke='white', strokeWidth=2)\
.encode(
    x=alt.X('Cycle:T', title='Year'),
    y=alt.Y('value:Q', title='Placed June deadline applicants (percentage)', stack='normalize'),
    color=alt.Color('equality_dimension:N', title='POLAR4'),
    tooltip=(
        alt.Tooltip('inst_all:N', title='University'),
        alt.Tooltip('equality_dimension:N', title='POLAR4'),
        alt.Tooltip('value:Q', title='Placed June deadline applicants'),
    )
)\
.facet(
    facet=alt.Facet('inst_all:N', title=None, sort=universities_order),
    columns=2,
    title={
        'text': 'Placed June deadline applicants in 2010-2021 by university',
        'anchor': 'middle',
        'fontSize': 15,
        'dy': -10
    }
)

chart

# %% [markdown]
# **Main point: University of Birmingham is average when it comes to the proportion of placed June deadline applicants from lower POLAR4 quintiles**
#
#
# ---
#
# Here, we notice that the proportion of POLAR4 Q1 `Placed June deadline applicants` at University of Birmingham is relatively good compared to our benchmark universities, standing at ~10% of applicants across all POLAR4 quintiles. 
#
# University of East Anglia does a bit better than the others for this metric, with ~12%, while King's College London does worse, with <5% (which is probably explained by the specificities of London applicants, who probably represent the majority of applications). 
#
# The metric for quintiles Q1-Q3 is similarly good (relatively speaking) at UoB, at ~40% of all applicants. Yet again, East Anglia shines with ~50% of placed applicants in Q3 or lower, while King's lags behind for this metric at 30%. 

# %% [markdown]
# #### Conclusion
#
# We observe that University of Birmingham has historically lagged behind on Widening Participation efforts compared to its peer universities (as identified by us) when looking at offer rates, which is one aspect of the application process that the university has arguably full control over. More specifically, the university has a very wide amplitude between its offer rates for higher and lower POLAR4 quintiles, and little improvement is to be noticed over time. In contrast, its peers either have much narrower amplitudes or have been starkly improving over the last decade. 
#
# However, when looking at the outcomes of the process, UoB is average, with 10% and 40% of all June deadline applications being Q1 or ≤Q3, respectively. This metric is much more affected by external factors (ie where students choose to go). 
#
# One potentially effective measure that UoB could implement to improve this would be to attempt to bring closer the gap between its offer rates to lower POLAR4 quintiles and the higher ones. We can assume (based on our current data analysis), that this could translate to much better outcomes in terms of Widening Participation for the university. 
