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
salesVolume_raw = pd.read_csv("./inputs/Sales Volume Chart_Full Data_data.csv")
revenueAdj_raw = pd.read_csv("./inputs/Revenue Chart_Full Data_data_InflationAdjusted.csv")

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


###################################################################################
# Exploratory plots

# Overall revenue over time



df_sum = df.groupby(['Year'])['Revenue(M)'].sum().reset_index()

(ggplot(df_sum, aes(x="Year", y='Revenue(M)') ) +
 geom_line() +
 #facet_wrap('Format', scales='free_y') +
 #geom_smooth(method='lm', se=False, colour='blue') +
 theme(
     axis_text_x=element_text(angle=90, ha='center'),
     figure_size=(10, 5)
     ) + 
     
     ggtitle('Inflation Adusted revenue vs Time')
)

"""
Since it's peak in the late 90's, revenue has declined 30% to 2024 levels
"""


# revenue Time Series
(ggplot(df[ df.Year>=2019], aes(x="Year", y='Revenue(M)') ) +
 geom_line() +
 facet_wrap('Format', scales='free_y') +
 geom_smooth(method='lm', se=False, colour='blue') +
 theme(
     axis_text_x=element_text(angle=90, ha='center'),
     figure_size=(10, 5)
     ) + 
     ggtitle('Inflation Adusted revenue vs Time')
)


# Revenue Comparison
df['Revenue'] = df['Revenue(M)']
(ggplot( 
    data=df[  df.Year.isin( [2019, 2022, 2024] )  ],
    mapping=aes(x="reorder( Format, Revenue )" , y='Revenue(M)', fill= "factor(Year)" )) +
 geom_bar(stat='identity', position='dodge') +
 theme(
     axis_text_x=element_text(angle=90, ha='center'),
     figure_size=(10, 5)
     ) + 
 ggtitle('Inflation Adusted revenue Comparison')
 )


# Units Time Series
(ggplot(df[ df.Year>=2019], aes(x="Year", y='Units(M)') ) +
 geom_line() +
 facet_wrap('Format', scales='free_y') +
 geom_smooth(method='lm', se=False, colour='blue') +
 theme(
     axis_text_x=element_text(angle=90, ha='center'),
     figure_size=(10, 5)
     ) + 
     ggtitle('Units(M) vs Time')
)


# Units Comparison
df['Units'] = df['Units(M)']
(ggplot( 
    data=df[  df.Year.isin( [2019, 2022, 2024] )  ],
    mapping=aes(x="reorder( Format, Units )" , y='Units', fill= "factor(Year)" )) +
 geom_bar(stat='identity', position='dodge') +
 theme(
     axis_text_x=element_text(angle=90, ha='center'),
     figure_size=(10, 5)
     ) + 
 ggtitle('Units(M) Comparison')
 )



# Revenue Per Unit
colors=['darkblue']
(ggplot( 
    data=df[  (df.Year.isin( range(2024,2025) ) & (df.Revenue_per_unit >0 )  )  ],
    mapping=aes(x="reorder( Format, Revenue_per_unit )" , y='Revenue_per_unit', fill= "factor(Year)" )) +
 geom_bar(stat='identity', position='dodge') +
 theme_minimal()+
 theme(
     axis_text_x=element_text(angle=45, ha='right'),
     figure_size=(10, 5),
     legend_position="none"
     ) + 
 scale_fill_manual( values=colors) +
 ggtitle('Revenue Per Unit ($)')+
 labs(x='', y='Revenue per Unit ($)')
 )



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


(ggplot( df[ (df.media == 'Streaming') & (df.Year >= 2019) ], 
        aes(x='Year', y='Revenue(M)', fill='Format')) +
    geom_area() +
    scale_y_continuous(breaks=np.arange(0, 15000, 1000)) +
    ggtitle( "Streaming Revenue Adjusted for Inflation")
)

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
    ggtitle( "Streaming Revenue Adjusted for Inflation")
)





#############################################################
# Calcualte 5-year and 2-year CAGRs for Revenue (2019, 2022 vs 2024)

cagr = df[ df.Year.isin([2019, 2022, 2025]) ]

#culate_cagr(beginning_value, ending_value, num_periods):
store=[]

for format in cagr.Format.unique():
   
    try:
        yr24 = df.loc[ (df.Format == format) & (df.Year == 2024), 'Revenue(M)'].item()
    except:
        yr24=0 


    two = calculate_cagr(
        df.loc[ (df.Format == format) & (df.Year == 2022), 'Revenue(M)'].item(),
        yr24,
        2)
    
    five = calculate_cagr(
        df.loc[ (df.Format == format) & (df.Year == 2019), 'Revenue(M)'].item(),
        yr24,
        5)  
    
    store.append([format, two, five])

cagr = pd.DataFrame(store)
cagr.columns = ['Format', "2022-2024 Revenue CAGR", "2019-2024 Revenue CAGR"]

cagr_melt = pd.melt(cagr, id_vars=['Format'], value_vars=['2022-2024 Revenue CAGR', '2019-2024 Revenue CAGR'],
                    var_name='field',
                    value_name='value')

cagr_melt = cagr_melt.sort_values( by='value', ascending=False)

(
    ggplot( cagr_melt[ cagr_melt.value > -1], aes('field', "reorder(Format, value)", fill="value"))
    + geom_tile(aes(width=0.95, height=0.95))
    + geom_text(aes(label="value"), size=9)
    + theme( axis_text_x=element_text(angle=45, ha='right') ) +
    ggtitle( "Revenue 2-year and 5-year CAGR")
)




#############################################################
# Calcualte 5-year and 2-year CAGRs for Revenue (2019, 2022 vs 2024)
digital = df[ (df.media == 'Streaming' )].Format.unique()

cagr_melt_stream = cagr_melt[ cagr_melt.Format.isin(digital)]


(
    ggplot( cagr_melt_stream[ cagr_melt_stream.value > -1], aes('field', "Format", fill="value"))
    + geom_tile(aes(width=0.95, height=0.95))
    + geom_text(aes(label="value"), size=9)
    + theme( axis_text_x=element_text(angle=45, ha='right') ) +
    ggtitle( "Streaming Revenue 2-year and 5-year CAGR")
)


 



"""
# I have a belief that there may be interesting growth in physical media,
#  and also in Ownership of Media vs Streaming.
#  Let's create some categories to investigate.
"""



