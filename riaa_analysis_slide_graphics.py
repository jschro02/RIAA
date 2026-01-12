import pandas as pd
import numpy as np
from plotnine import * #


def calculate_cagr(beginning_value, ending_value, num_periods):
    """
    Calculates the Compound Annual Growth Rate (CAGR).

    Args:
    beginning_value: The starting value of the investment or metric.
    ending_value: The final value after the investment period.
    num_periods: The number of periods (typically years) between the start and end dates.

    Returns:
    The CAGR as a decimal. Multiply by 100 to get the percentage.
    """
    if beginning_value <= 0 or ending_value < 0 or num_periods <= 0:
        return None # Handles invalid inputs where CAGR isn't applicable or calculable

    # The core CAGR formula
    cagr = (ending_value / beginning_value) ** (1 / num_periods) - 1
    cagr = round( cagr, 4)
    return cagr




# Open Files
salesVolume_raw = pd.read_csv("./inputsSales Volume Chart_Full Data_data.csv")
revenueAdj_raw = pd.read_csv("./inputsRevenue Chart_Full Data_data_InflationAdjusted.csv")

# Simplify Sales Volume
sales_cols = ['Year', 'Format', 'Value (Actual)']
sales_vol = salesVolume_raw.loc[ :, sales_cols]
sales_vol.columns = ['Year', 'Format', 'Units(M)']

# Simplify Sales Revenue
revenue_cols = ['Year', 'Format', 'Value (For Charting)']
revenue = revenueAdj_raw.loc[:, revenue_cols]
revenue.columns =['Year', 'Format', 'Revenue(M)']
revenue['Revenue(B)'] = revenue['Revenue(M)'] * .001

# Merge revenu and volume with full outer-join
df = pd.merge( sales_vol,
              revenue,
              left_on=['Year', 'Format'],
              right_on=['Year', 'Format'],
              how='outer'
              ).reset_index()


# Calculate Revenue per Unit - Dollars
df["Revenue_per_unit"] = df['Revenue(M)'] / df['Units(M)']









########################
# Streaming growth
physical_media = ['8 - Track', 'Cassette', 'LP/EP', 'Other Tapes', 'Vinyl Single',
       'CD', 'Cassette Single', 'CD Single', 'Music Video (Physical)',
       'DVD Audio', 'SACD',  'Other Physical']

streaming_media = ['Paid Subscription', 'On-Demand Streaming (Ad-Supported)',
       'Limited Tier Paid Subscription', 'Other Ad-Supported Streaming']

owned_media = ['Download Album', 'Download Single', 'Download Music Video']

other_media = ['SoundExchange Distributions', 'Synchronization', 'Ringtones & Ringbacks', 'Kiosk','Download Album', 'Download Single', 'Download Music Video', 'Other Digital']

owned_media.extend( physical_media)

# Create the media category - digital vs. physical
df['media'] = "Streaming"
df['media'][ df.Format.isin( physical_media ) ] = "Physical"
df['media'][ df.Format.isin( other_media ) ] = "Other"


colors = ['black','lightblue','darkblue', 'black'] 
(ggplot( df[ (df.media == 'Streaming') & (df.Year >= 2019) ], 
        aes(x='Year', y='Revenue(M)', fill='Format')) +
    geom_area() +
    scale_y_continuous(breaks=np.arange(0, 15000, 1000)) +
    facet_wrap('Format') +
     theme(
     axis_text_x=element_text(angle=90, ha='center'),
     figure_size=(8, 5),
     legend_position="none"
     ) + 
     scale_fill_manual( values=colors) + 
    ggtitle( "2021-2024, Limited-Tier and Ad-Supported revenue have declined")
)



# Overall revenue over time
df_sum = df.groupby(['Year', 'media'])['Revenue(M)'].sum().reset_index()

#USED FOR SLIDES
colors = ['lightblue', 'darkblue', 'black'] 
(ggplot(df_sum[ df_sum.Year >= 2014 ], aes(x="Year", y='Revenue(M)', fill='media') ) +
 geom_area() +
 scale_x_continuous(breaks=np.arange(2010, 2026, 1)) +
 theme_minimal( ) +
 theme(
     #axis_text_x=element_text(angle=90, ha='center'),
     figure_size=(10, 5),
     legend_title=element_blank()
     ) + 
 #ggtitle('Revenue by General Category') +
 scale_fill_manual( values=colors)
)

# USED FOR SLIDES
df_sum = df.groupby(['Year', 'Format'])['Revenue(M)'].sum().reset_index()
colors = ['lightblue', 'darkblue', 'black']
tmp = df_sum[ df_sum.Format.isin(['CD', 'LP/EP']) ] 
(
    ggplot( 
    (tmp[ (tmp.Year >= 2019)  ]),
    aes(x="Year", y='Revenue(M)', fill='Format') ) +
    geom_area() +
    facet_wrap('Format', nrow=1) +
    scale_x_continuous(breaks=np.arange(2010, 2026, 1)) +
    #theme_minimal( ) +
    theme(
        #axis_text_x=element_text(angle=90, ha='center'),
        figure_size=(6, 2.5),
        legend_title=element_blank(),
        legend_position="none"
        ) +
    ggtitle('Change in Revenue - 2019-2024') +
    scale_fill_manual( values=colors)
)




