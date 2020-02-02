import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output

gdp2teamp2meat2ghg = pd.read_json('./input/gdp2temp2meat2ghg.json', orient='records')
sea2glacier = pd.read_json('./input/sea2glaciers.json', orient='records')

# APP
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

home_page = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H4('Data Visualization Final Project - 2019/2020', className='row'),
                html.Br(),
                html.P("A visualization of the Global Warming"),
                html.Br(),
                dcc.Markdown(
                    '''
                    #### Github
                    Enjoy the code behind this app at [Github](https://github.com/NorayrMeliksetyan/GlobalWarming).
                    '''),
                html.Br(),
                dcc.Markdown('''
                    #### Members
                    - **Norayr Meliksetyan**, M20190687''')
            ], className="row", style={'width': '98%', 'display': 'inline-block'})
        ]),

        html.Div([
            dcc.Markdown('''
                ## An Exploratory Dashboard for Global Warming
                
                ### A description of main variables
                |     Variable     |   Description                                                |
                |-------------------------|:-----------------------------------------------------------------------|
                |  |
                | **Sea level and Glacier mass** |
                | year | Indicates the .... |
                | level | Sea level .... |
                | mass | Glacier mass .... |
                | . |
                | **Second dataset** |
                | year | Indicates the .... |
                '''),
        ],
            className="row", style={'width': '80%', 'display': 'inline-block'}),
    ], className="row"),
])

dash_board = html.Div([
    html.Div([
        html.Div([
            html.H4('Year', className='h4'),
            html.P(
                'Scroll to select year to inspect all available data'
            ),
            dcc.Slider(
                id='year',
                min=gdp2teamp2meat2ghg['year'].min(),
                max=gdp2teamp2meat2ghg['year'].max(),
                marks={str(i): '{}'.format(str(i)) for i in [1970, 1980, 1990, 2000, 2010, 2014]},
                value=2007,
                step=1
            ),

            html.Br(),
            html.H4('Select Countries', className='h4'),
            dcc.Dropdown(
                id='countries',
                options=[dict(label=country, value=country) for country in gdp2teamp2meat2ghg['country'].unique()],
                value=['Armenia', 'Portugal', 'Spain', 'Italy'],
                multi=True
            ),
            html.Br(),
        ], className='column1 pretty'),

        html.Div([dcc.Graph(id='heat_map')], className='column3 pretty'),
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='bar_graph')], className='column3 pretty'),
        html.Div([dcc.Graph(id='scatter_plot')], className='column3 pretty'),
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='bubble_chart')], className='column3 pretty'),
    ], className='row'),

])

# organising Tabs in the app
app.layout = html.Div([
    html.H1('Global Warming Visualized', className='Title'),
    dcc.Tabs([
        dcc.Tab(label='Home', children=[
            home_page
        ]),
        dcc.Tab(label='Dashboard', children=[
            dash_board
        ]),
    ])
])


# Callbacks
@app.callback(
    output=[
        Output("heat_map", "figure"),
        Output("bar_graph", "figure"),
        Output("scatter_plot", "figure"),
        Output("bubble_chart", "figure"),
    ],
    inputs=[
        Input("year", "value"),
        Input("countries", "value"),
    ],
)
def plots(year, countries):
    country_codes = px.data.gapminder().query('year==2007')
    temperature_data = gdp2teamp2meat2ghg[gdp2teamp2meat2ghg['year'] == year]
    temperature_data = pd.merge(temperature_data, country_codes[['country', 'iso_alpha']], on='country', how='left')

    fig = go.Figure(data=go.Choropleth(
        locations=temperature_data['iso_alpha'],
        z=temperature_data['temperature'],
        text=temperature_data['country'],
        colorscale='Reds',
        zmin=gdp2teamp2meat2ghg['temperature'].min(),
        zmax=gdp2teamp2meat2ghg['temperature'].max(),
        autocolorscale=False,
        reversescale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_tickprefix='C',
        colorbar_title='Temperature C',
    ))

    fig.update_layout(
        title_text=f'{year} Average temperature by country',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth'
        ),
    )

    data_bar = [
        (dict(type='bar', x=sea2glacier['year'], y=sea2glacier['level'], name='Sea level')),
        (dict(type='bar', x=sea2glacier['year'], y=sea2glacier['mass'], name='Glacier Mass')),
    ]

    layout_bar = dict(title=dict(text='Glacier Mass vs Sea level by years'),
                      yaxis=dict(title='Inches'),
                      xaxis=dict(title='Year', rangeslider=dict(visible=True)),
                      paper_bgcolor='#f9f9f9')

    scatter_by_country = []
    for country in countries:
        country_df = gdp2teamp2meat2ghg[gdp2teamp2meat2ghg['country'] == country]
        scatter_by_country.append(
            dict(type='scatter', x=country_df['ghg_emission'], y=country_df['temperature'], name=country,
                 mode='markers')
        )

    layout_scatter = dict(title=dict(text='Temperature and GHG emissions'),
                          yaxis=dict(title='Temperature'),
                          xaxis=dict(title='GHG emissions'),
                          paper_bgcolor='#f9f9f9')

    bubble = px.scatter(gdp2teamp2meat2ghg[gdp2teamp2meat2ghg['country'].isin(countries)],
                        x="gdp", y="meat_consumption", size="ghg_emission",  color="country",
                        hover_name="country", log_x=True, size_max=50,
                        title='Meat consumption GDP and GHG emissions (Size of bubble = GHG emissions)')
    bubble.update_layout(xaxis=dict(title='GDP'), yaxis=dict(title='Meat Consumption'))

    return [
        fig,
        go.Figure(data=data_bar, layout=layout_bar),
        go.Figure(data=scatter_by_country, layout=layout_scatter),
        bubble,
    ]


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
