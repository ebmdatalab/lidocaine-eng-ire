# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# **Work in progress**

# I'm interested in prescribing of Lidocaine patches since 2015. Details of lidocaine plasters prescribing can be seen on [OpenPrescribing here](https://openprescribing.net/measure/lplidocaine/national/england/). Previous DataLab work on evaluation on the impact of NHS England guidance can be viewed [here in JRSM](https://journals.sagepub.com/doi/10.1177/0141076818808429)

# The following example notebooks for reference for re-using code snippets
# - https://github.com/ebmdatalab/lidocaine-change-detection-notebook/blob/master/notebooks/ccg-lidocaine-change.ipynb
# - https://github.com/ebmdatalab/jupyter-notebooks/blob/master/Dementia%20Prescribing/Dementia%20Prescribing.ipynb
# - https://github.com/ebmdatalab/jupyter-notebooks/blob/master/new_measures/Gabapentinoids/New%20Measure%20-%20Gabapentin%20and%20Pregabalin%20DDD.ipynb
# - https://github.com/ebmdatalab/cd-legislation-notebook/blob/master/notebooks/legislative.change.ipynb
#     

# ## Data Extraction
#
# - Lidocaine here
# - See below for list size (add navigation later)

#import libraries required for analysis
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from ebmdatalab import bq, charts, maps
import os

## ensuring the format is consistent for pounds and pence
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# +
## here we will extract all prescribing of Lidocaine patches by ccg (prev named pct)
sql= '''
SELECT
DATE(month) AS month,
  pct,
  SUM(quantity) AS quantity_of_plasters,
  SUM(items) AS rx_items,
  SUM(actual_cost) AS actual_cost,
  SUM(net_cost) AS net_cost
FROM
  ebmdatalab.hscic.normalised_prescribing AS rx
  INNER JOIN hscic.ccgs AS ccg ON rx.pct = ccg.code 
WHERE
  bnf_code LIKE "1502010J0%EL" # brand and Lidocaine patches
  AND month >= "2015-01-01"
  AND ccg.org_type = 'CCG' #restrict to only ccg orgs i.e. exclude OOH etc
GROUP BY
   month,
   pct
 '''

df_lidocaine = bq.cached_read(sql, csv_path=os.path.join('..', 'data','lidocaine.csv'), use_cache=True)
df_lidocaine['month'] = df_lidocaine['month'].astype('datetime64[ns]')
df_lidocaine.head(10)

# +
## add list size
# -

# get data for patient list size (all patients)
sql2 = """
SELECT 
DATE(month) AS month, 
pct_id AS pct, 
sum(total_list_size) as list_size
FROM ebmdatalab.hscic.practice_statistics
group by 
month, pct
order by
month, pct
"""
listsize_df = bq.cached_read(sql2, csv_path=os.path.join('..', 'data','list_size.csv'), use_cache=True)
listsize_df['month'] = listsize_df['month'].astype('datetime64[ns]')
listsize_df.head()

lidocaine_and_listsize = pd.merge(df_lidocaine, listsize_df, on=['month', 'pct'])
lidocaine_and_listsize['plasters_per_1000'] = 1000* (lidocaine_and_listsize['quantity_of_plasters']/lidocaine_and_listsize['list_size'])
lidocaine_and_listsize['items_per_1000'] = 1000* (lidocaine_and_listsize['rx_items']/lidocaine_and_listsize['list_size'])
lidocaine_and_listsize['actual_cost_per_1000'] = 1000* (lidocaine_and_listsize['actual_cost']/lidocaine_and_listsize['list_size'])
lidocaine_and_listsize['net_cost_per_1000'] = 1000* (lidocaine_and_listsize['net_cost']/lidocaine_and_listsize['list_size'])
lidocaine_and_listsize.head()

# +
#plot deciles 
charts.deciles_chart(
        lidocaine_and_listsize,
        period_column='month',
        column= 'plasters_per_1000',
        title="CCGs - Plasters per 1000 people",
        show_outer_percentiles=True)
plt.show()


# +
#plot deciles 
charts.deciles_chart(
        lidocaine_and_listsize,
        period_column='month',
        column= 'actual_cost_per_1000',
        title="CCGs - Actual cost of Plasters per 1000 people",
        show_outer_percentiles=True)

#add in example CCG (Newcastle Gateshead)
df_subject = lidocaine_and_listsize.loc[lidocaine_and_listsize['pct'] == '13T']
plt.plot(df_subject['month'], df_subject['items_per_1000'], 'r--')


plt.show()
# -



# ## Charts
# Here we will draw some charts to ilustrate national patterns

# total number of patches
ax = df_lidocaine.groupby(["month"])['quantity_of_plasters'].sum().plot(kind='line', title="Total Lidocaine Patches")
ax.axvline(pd.to_datetime('2017-07-01'), color='black', linestyle='--', lw=2) ##policy announced
ax.axvline(pd.to_datetime('2017-11-01'), color='black', linestyle='--', lw=2) ##consultation implemented
plt.ylim(0, 800000)

# total actual cost
ax = df_lidocaine.groupby(["month"])['actual_cost'].sum().plot(kind='line', title="Total Lidocaine Actual Cost")
ax.axvline(pd.to_datetime('2017-07-01'), color='black', linestyle='--', lw=2) ##policy announced
ax.axvline(pd.to_datetime('2017-11-01'), color='black', linestyle='--', lw=2) ##consultation implemented
plt.ylim(0, )

# +
# total net cost
# -

ax = df_lidocaine.groupby(["month"])['net_cost'].sum().plot(kind='line', title="Total Lidocaine Net Cost")
ax.axvline(pd.to_datetime('2017-07-01'), color='black', linestyle='--', lw=2) ##policy announced
ax.axvline(pd.to_datetime('2017-11-01'), color='black', linestyle='--', lw=2) ##consultation implemented
plt.ylim(0, )


