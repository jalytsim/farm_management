import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def generate_choropleth_map(data_variable='actual_yield', start_date=None, end_date=None, crop=None):
    # Your code to generate the choropleth map based on the parameters
    # Example:
    df = pd.read_csv('data.csv')
    fig = px.choropleth(df, locations='region', color=data_variable)
    return fig.to_html()
