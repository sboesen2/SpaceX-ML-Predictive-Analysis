# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas dataframe
spacex_df = pd.read_csv("spacex_web_scraped.csv")

# Convert the 'Payload mass' column to numeric, forcing errors to NaN
spacex_df['Payload mass'] = pd.to_numeric(spacex_df['Payload mass'], errors='coerce')

# Drop rows with NaN values in 'Payload mass'
spacex_df.dropna(subset=['Payload mass'], inplace=True)

# Get min and max payload for the slider
min_payload = spacex_df['Payload mass'].min()
max_payload = spacex_df['Payload mass'].max()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True
                 ),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='Launch outcome',
                     names='Launch site',
                     title='Total Success Launches by Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch site'] == entered_site]
        fig = px.pie(filtered_df, names='Launch outcome',
                     title=f'Total Success Launches for site {entered_site}')
        return fig

# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload mass'] >= payload_range[0]) &
        (spacex_df['Payload mass'] <= payload_range[1])
    ]
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch site'] == entered_site]
    fig = px.scatter(filtered_df, x='Payload mass', y='Launch outcome',
                     color='Version Booster',
                     title='Payload vs. Outcome for All Sites' if entered_site == 'ALL' else f'Payload vs. Outcome for site {entered_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
