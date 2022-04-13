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
DATE(month) AS month
  pct,
  SUM(quantity) AS quantity_of_plasters,
  SUM(items) AS prescription_items,
  SUM(actual_cost) AS actual_cost,
  SUM(net_cost) AS net_cost
FROM
  ebmdatalab.hscic.normalised_prescribing_standard AS rx
  INNER JOIN hscic.ccgs AS ccg ON rx.pct = ccg.code 
WHERE
  bnf_code LIKE "1502010J0%EL" # brand and Lidocaine patches
  AND month >= "2015-01-01"
  AND ccg.org_type = 'CCG' #restrict to only ccg orgs i.e. exclude OOH etc
GROUP BY
   month,
   pct
 '''

df_lidocaine = bq.cached_read(sql, csv_path=os.path.join('..', 'data','lidocaine.csv'))
df_lidocaine.head(10)
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

# +
## add list size
# -

# get data for patient list size (all patients)
sql2 = """
SELECT month, pct_id AS pct, sum(total_list_size) as list_size
FROM ebmdatalab.hscic.practice_statistics
group by 
month, pct
order by
month, pct
"""
listsize_df = bq.cached_read(sql2, csv_path='list_size.csv')
listsize_df['month'] = listsize_df['month'].astype('datetime64[ns]')

#Merge data into single dataframe
df_qty=df_lidocaine.groupby(["month", "pct"])['quantity_of_plasters'].sum().to_frame(name = 'qty_plasters').reset_index()
df_qty.head()
#plot data on graph
#gaba_df.groupby(["month"])['pregab_mg'].sum().plot(kind='line', title="Total pregabalin mg eq prescribing of gabape

#merge dataframes
per_1000_df = pd.merge(df_qty, listsize_df, on=['month', 'pct'])
per_1000_df['plasters_per_1000'] = 1000* (per_1000_df['quantity_of_plasters']/per_1000_df['list_size'])
per_1000_df.head()

# +
#plot deciles 
charts.deciles_chart(
        df_ccg,
        period_column='month',
        column= 'perc_doacs',
        title="CCGs - Percentage of DOACs and warfarin \nprescribed as DOACS",
        show_outer_percentiles=True)
plt.show()

