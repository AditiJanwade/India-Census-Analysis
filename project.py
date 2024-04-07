import streamlit as st
import pandas as pd
import plotly.express as px
import json
import numpy as np


st.set_page_config(
    page_title='India Census',
    page_icon='🇮🇳',  # Indian flag emoji
    layout='wide',
    initial_sidebar_state='collapsed'
)
st.title('📊 Indian Census Analysis')
# Load geojson file
with open(r"D:\Desktop\states_india.geojson", 'r') as f:
    india_states = json.load(f)

# Create a map of state names to state codes
state_id_map = {}
for feature in india_states["features"]:
    feature["id"] = feature["properties"]["state_code"]
    state_id_map[feature["properties"]["st_nm"]] = feature["id"]

df_main=pd.read_csv('india_census.csv')
df_maha=pd.read_csv('States.csv')
df_main["Density"] = df_main["Density[a]"].apply(lambda x: int(x.split("/")[0].replace(",", "")))
df_main["id"] = df_main["State or union territory"].apply(lambda x: state_id_map[x])
df_main["DensityScale"] = np.log10(df_main["Density"])
df_main["SexRatioScale"] = df_main["Sex ratio"] - 1000

# Check for NaN or infinite values in 'DensityScale' column
missing_values = df_main["DensityScale"].isnull().sum()
infinite_values = np.isinf(df_main["DensityScale"]).sum()
if missing_values > 0 or infinite_values > 0:
    st.error("There are missing or infinite values in 'DensityScale' column.")

# Create sidebar for additional options
with st.sidebar:
    st.title('India Population Dashboard')
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo',
                        'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)
    selected_states = st.multiselect("Select States", list(df_main["State or union territory"].unique()))
    selected_state_analysis = st.selectbox("Select State for Analysis",
                                           list(df_maha["State or union territory"].unique()))

df_selected_states = df_main[df_main["State or union territory"].isin(selected_states)]
# Plot chloropleth map and heatmap for the selected state
fig = px.choropleth_mapbox(
    df_selected_states,
    locations="id",
    geojson=india_states,
    color="DensityScale",
    hover_name="State or union territory",
    hover_data=["Density", 'Population'],
    title=f" Population Density",
    mapbox_style="carto-positron",
    center={"lat": 24, "lon": 78},
    zoom=3,
    opacity=0.5,
    color_continuous_scale=selected_color_theme,  # Use selected color theme
)
fig.update_layout(
    template='plotly_dark',
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
    margin=dict(l=0, r=0, t=0, b=0),
    height=600
)
st.plotly_chart(fig, use_container_width=True)

merged_df = pd.merge(df_main, df_maha, on="State or union territory")
selected_data = merged_df[merged_df["State or union territory"]==(selected_state_analysis)]

st.header(f"selected {selected_state_analysis} for Visualizations")
st.markdown("---")
if selected_state_analysis:
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"Analysis for {selected_state_analysis}")

    st.sidebar.write(f"You selected {selected_state_analysis} for analysis.")
    # Filter data for selected state
    selected_data = df_maha[df_maha["State or union territory"] == selected_state_analysis]

col1, col2,= st.columns([2, 1])

# Plot pie chart and scatter plot in the first column
with col1:
    st.subheader("Pie Chart: Population Distribution by Literacy Rate")
    literacy_bins = pd.cut(selected_data['Literacy'], bins=3, labels=['Low', 'Medium', 'High'])
    literacy_distribution = literacy_bins.value_counts(normalize=True)
    pie_fig = px.pie(values=literacy_distribution, names=literacy_distribution.index,
                     title='Population Distribution by Literacy Rate',
                     color_discrete_sequence=px.colors.qualitative.Plotly)
    st.plotly_chart(pie_fig)

    st.subheader("Population Distribution by SEX Ratio")
    literacy_bins = pd.cut(selected_data['Sex Ratio'], bins=3, labels=['Low', 'Medium', 'High'])
    literacy_distribution = literacy_bins.value_counts(normalize=True)
    st.plotly_chart(px.pie(values=literacy_distribution, names=literacy_distribution.index,
                            title='Population Distribution by Literacy Rate'))

    st.subheader("Population vs. Sex Ratio")
    scatter_fig = px.scatter(
        selected_data,
        x="Population",
        y="Sex Ratio",
        size="Density",
        color="Density",
        hover_name="State or union territory",
        title="Population vs. Sex Ratio (Size: Density)",
        labels={"Population": "Population", "Sex Ratio": "Sex Ratio", "Density": "Density"},
        template="plotly_white",
        width=800,
        height=500
    )
    scatter_fig.update_layout(
        xaxis_title="Population",
        yaxis_title="Sex Ratio",
        coloraxis_colorbar=dict(title="Density"),
        margin=dict(l=40, r=40, t=80, b=40),
    )
    st.plotly_chart(scatter_fig)

    # Scatter plot
    st.subheader("Scatter Plot: Population vs District (Size: Sex Ratio)")
    scatter_fig = px.scatter(selected_data, x='District', y='Population', size='Sex Ratio',
                             color='Sex Ratio', hover_name='District',
                             title='Population vs District (Size: Sex Ratio)',
                             color_continuous_scale=selected_color_theme)
    st.plotly_chart(scatter_fig)
    # Histogram
    st.subheader("Histogram: Population Distribution")
    st.write(px.histogram(selected_data, x='Population', title='Population Distribution'))

with col2:
    st.markdown('#### Top States')
    st.dataframe(df_main[["State or union territory", "Population"]].sort_values(by="Population", ascending=False).head(10),
                 column_order=("State or union territory", "Population"),
                 hide_index=True,
                 width=None,
                 column_config={
                     "State or union territory": st.column_config.TextColumn(
                         "State",
                     ),
                     "Population": st.column_config.ProgressColumn(
                         "Population",
                         format="%f",
                         min_value=0,
                         max_value=max(df_main["Population"]),
                     )}
                 )

    with st.expander('About', expanded=True):
        st.write('''
            - Data: [India Census](https://en.wikipedia.org/wiki/List_of_states_and_union_territories_of_India_by_population).
            - :orange[**Dashboard Info**]: This dashboard provides analysis of Indian census data, including population density, literacy rates, sex ratios, and more.
            This dashboard provides analysis of various demographic indicators based on Indian census data. 
            The dataset includes information such as population density, literacy rates, sex ratios, and population growth rates 
            for different states and union territories of India. 
            Additionally, it also provides insights into the distribution of population based on literacy categories 
            (low, medium, high) and visualizes the correlation between population and other demographic factors.
            """)
            ''')

st.write("Merged Data:", merged_df)
st.write("Selected Data:", selected_data)