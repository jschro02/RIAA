import pandas as pd

"""
Files downloaded from Tableau public do not match in terms of row count, etc...

Explore the files to find out why.
"""

# Open Files
salesVolume_raw = pd.read_csv("Sales Volume Chart_Full Data_data.csv")
revenue_raw = pd.read_csv("Revenue Chart_Full Data_data_raw.csv")
revenueAdj_raw = pd.read_csv("Revenue Chart_Full Data_data_InflationAdjusted.csv")



def extract_unique_column_names( *args ) -> list:
    """
    creates a unique list of all columns in
    provided Pandas dataframes
    """
    column_sets = [ set(df.columns) for df in args ]
    all_columns = set().union(*column_sets)
    return( list(all_columns) )


def extract_common_column_names( *args ) -> list:
    """
    creates a unique list of all common columns in
    provided Pandas dataframes
    """
    column_sets = [ set(df.columns) for df in args ]
    all_columns = set.intersection(*column_sets)
    return( list(all_columns) )


def delta_columns( df1, df2, field) -> pd.DataFrame:
    """
    pass in two dataframes and a field name
    returns any missing values or values with different counts
    """
    a = df1[field].value_counts()
    b = df2[field].value_counts()

    results = (
        pd.merge(a.to_frame(),
                 b.to_frame(),
                 left_index=True,
                 right_index=True,
                 how="outer")
                )
          
    results['delta'] = results.count_x - results.count_y
    results['field'] = field
    return( results[ results.delta!=0 ] )



###############################################################################
# Review Undjusted vs. Inflation Adjusted Revenue File

# Get a list of unique field names in 2 or more pd.DataFrame
fields = extract_unique_column_names( revenue_raw, revenueAdj_raw )

# for each field, identify differences in counts or missing categories
a = [delta_columns( revenue_raw, revenueAdj_raw, f) for f in fields]
out = pd.concat(a)

#write to excel, easier to view
out.to_excel( "revenue_comparison.xlsx")

#After review, these fields need further examination:
out = out[ out['field'].isin(['Format', 'Metric', 'Year'])]


"""
Paid Subscription:
    There are two fields in the raw file: 'Paid Subscription' & 'Paid Subscriptions'
    Review showed Paid Subscriptions < 1% of Paid subscription.
    Paid Subscription field matches across; opted to ignore 'Paid Subscriptions',
    Not materially impactful, but worth follow-up as to why catergorized.
    ( See Below )

Other Digital:
    category had extra entires in 2023 & 2024 in the un-adjusted file.
    Both values were < $800K, ignoring for roll-up

Year:
    2023 & 2024 explained above (duplicated entries in un-adjusted file)
    2005 - 2024 have one extra entry in Raw Data, this is from 'Paid Subscription'
"""

# 'Paid Subscritpions is < 1% of the value of Paid Subscription.  We can ignore it
revenue_raw.groupby('Format')['Value (For Charting)'].agg(['mean', 'sum', 'min', 'max']).round(0)

"""
DECISION POINT:
Based on small differences, have opted to use the Inflation Adjusted file
"""





###############################################################################
# Review Units Sold file vs. Inflation Adjusted File

# Get a list of unique field names in 2 or more pd.DataFrame
all_fields = extract_unique_column_names( revenueAdj_raw, salesVolume_raw )
common_fields = extract_common_column_names( revenueAdj_raw, salesVolume_raw ) # 6 fields are not common

# Non-Common Fields
list( set(all_fields) - set(common_fields) ) # non-Common fields are not important

# I do want to know if we have disimilar formats, take a look at them
out = delta_columns( revenueAdj_raw, salesVolume_raw, 'Format')

"""
CD Single, Cassette Single, and DVD Audio have different number of entries:
    * Cassette Single shows negative values in volume data for 2001 and 2002, RevenueAdj is missing these entries
    * CD Single is Missing 1989 Entry in Inflation Adjusted Revenue Chart
    * DVD Audio: 2013 data is missing from the Inflation Adjusted revenue Chart

Multiple Streaming / Digital Subscriptions
    These 7 formats are missing from the Sales Volume numbers, which is not surprising 
    because they aren't necessarily for a fixed unit of songs, albums, etc...
    - Limited Tier Paid Subscription
    - On-Demand Streamding (Ad-Supported)
    ...
    ...
    - Syncronization
"""