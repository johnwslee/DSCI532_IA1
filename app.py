import altair as alt
from dash import Dash, html, dcc, Input, Output
from gapminder import gapminder
import dash_bootstrap_components as dbc
import pandas as pd
from vega_datasets import data

# Read in global data
gapminder = gapminder
df_pos = pd.read_csv('data/world_country.csv')
df_pos = df_pos.iloc[:, 1:4]
df_pos.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
gapminder_pos = gapminder.merge(df_pos)

# Setup app and layout/frontend
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

years = gapminder.year.unique()

app.layout = dbc.Container(
    [
        html.H1('Our Changing World', style={'textAlign': 'center'}),
        html.Br(),
        dcc.Tabs(
          [
            dcc.Tab(
              label='World View', 
              children=[
                dbc.Row(
                    [
                    dbc.Col(
                        [
                            html.Br(),
                            html.Br(),
                            html.H5('What do you want to know?'),
                            dcc.Dropdown(
                                id='topic_dropdown', value='pop',
                                options=[
                                    {'label': 'Population', 'value': 'pop'},
                                    {'label': 'Life Expectancy', 'value': 'lifeExp'},
                                    {'label': 'GDP per Capita', 'value': 'gdpPercap'}
                                ],
                                style={'max-width': '90%'}
                            ),
                            html.Br(),
                            html.H5('Choose year'),
                            dcc.Slider(
                                min=1952, 
                                max=2007, 
                                step=5,
                                id='year-slider',
                                marks={int(x): {"label": str(x)} for x in list(years)},
                                value=1957
                            )
                        ],
                        md=4
                    ),
                    dbc.Col(
                        [
                            html.Br(),
                            html.H3('World Map', style={'textAlign': 'center'}),
                            html.Iframe(
                                id='world_map',
                                style={'border-width': '0', 'width': '100%', 'height': '500px'}
                            )
                        ],
                        md=8
                    )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3('World Ranking', style={'textAlign': 'center'}),
                                html.Iframe(
                                    id='ranking_chart',
                                    style={'border-width': '0', 'width': '100%', 'height': '400px'}
                                )
                            ]
                        ),
                        dbc.Col(
                            [
                                html.H3('World Trend', style={'textAlign': 'center'}),
                                html.Iframe(
                                    id='trend_chart',
                                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
                            ]
                        )
                    ]
                )
              ]
            ),
            dcc.Tab(
              label='Country View', 
              children=[
                dbc.Row(
                    [
                    dbc.Col(
                        [
                            html.Br(),
                            html.Br(),
                            html.H5('Which country do you want to know?'),
                            dcc.Dropdown(
                                id='country_dropdown', value='Canada',
                                options=[
                                    {'label': country, 'value': country} for country in (gapminder_pos["country"]).unique()
                                ],
                                style={'max-width': '90%'}
                            ),
                            html.Br(),
                            html.H3('Location of Country', style={'textAlign': 'center'}),
                            html.Iframe(
                                id='location',
                                style={'border-width': '0', 'width': '100%', 'height': '500px'}
                            )
                        ],
                        md=5
                    ),
                    dbc.Col(
                        [
                            html.Br(),
                            html.H3('Country Data', style={'textAlign': 'center'}),
                            html.Iframe(
                                id='country_chart',
                                style={'border-width': '0', 'width': '100%', 'height': '800px'}
                        )
                        ],
                        md=7
                    )
                    ]
                )
              ]
            )
          ]
        ),
    ]
)

# Setup callbacks/backend for location chart
@app.callback(
    Output('location', 'srcDoc'),
    Input('country_dropdown', 'value'),
    )
def plot_country(country):
    country = country
    world_map = alt.topo_feature(data.world_110m.url, 'countries')
    background = alt.Chart(world_map).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        width=450,
        height=350
    ).project(type='equalEarth')
    
    points = alt.Chart(gapminder_pos.query('country == @country')).mark_point().encode(
        longitude='lon:Q',
        latitude='lat:Q'
    )
    
    return (background + points).to_html()



# Setup callbacks/backend for country data chart
@app.callback(
    Output('country_chart', 'srcDoc'),
    Input('country_dropdown', 'value'),
    )
def plot_country_data(country):
    country = country
    df = gapminder.query("country == @country")
    pop_chart = alt.Chart(df, title="Population").mark_bar().encode(
        alt.X('year:N', 
              title="Year"),  
        alt.Y(
            'pop',
            title="Population",
        ),
        color="country"
        ).properties(
            width=230,
            height=250
        )
    
    lifeExp_chart = alt.Chart(df, title="Life Expectancy").mark_bar().encode(
        alt.X('year:N', 
              title="Year"),  
        alt.Y(
            'lifeExp',
            title="Life Expectancy [years]",
            axis=alt.Axis(format=',d')
        ),
        color="country"
        ).properties(
            width=230,
            height=250
        )
    
    gdpPercap_chart = alt.Chart(df, title="GDP per Capita").mark_bar().encode(
        alt.X('year:N', 
              title="Year"),  
        alt.Y(
            'gdpPercap',
            title="GDP per Capita [USD]",
            axis=alt.Axis(format='$,d')
        ),
        color="country"
        ).properties(
            width=230,
            height=250
        )

    return (pop_chart | lifeExp_chart & gdpPercap_chart).to_html()



# Setup callbacks/backend for ranking chart
@app.callback(
    Output('ranking_chart', 'srcDoc'),
    Input('year-slider', 'value'),
    Input('topic_dropdown', 'value')
    )
def plot_world_ranking(year, y_axis):
    year = year
    df = gapminder.query("year == @year").sort_values(by=y_axis, ascending=False)
    df["ranking"] = [f"#{i+1}" for i in range(142)]
    bar = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            alt.X(
                y_axis,
                title="Population"
                if y_axis == "pop"
                else ("Life Expectancy (years)" if y_axis == "lifeExp" else "GDP per Capita (USD)"),
                axis=alt.Axis(format='$,d', orient='top')
                if y_axis == "gdpPercap"
                else (alt.Axis(format=',d', orient='top')),
            ),
            alt.Y(
                "country",
                sort=alt.EncodingSortField("value", op="min", order="descending"),
                title="Country",
            ),
            color=alt.Color("continent", legend=None),
            tooltip=y_axis,
        )
    )

    text = bar.mark_text(align="left", baseline="middle", dx=3).encode(text="ranking")

    chart = bar + text
    chart_final = chart.configure_axis(
      labelFontSize=14, titleFontSize=20
      ).properties(
        width=350)
    
    return chart_final.to_html()


# Setup callbacks/backend for trend chart
@app.callback(
    Output('trend_chart', 'srcDoc'),
    Input('year-slider', 'value'),
    Input('topic_dropdown', 'value')
    )
def plot_world_trend(year, y_axis):
    df = gapminder.groupby(["year", "continent"]).mean().reset_index()

    line = alt.Chart(df).mark_line().encode(
        alt.X('year:N', 
              title="Year"),  
        alt.Y(
            y_axis,
            title="Average Population" if y_axis == "pop" else (
                "Average Life Expectancy [years]" if y_axis == "lifeExp" else "Average GDP per Capita [USD]"
            )
        ),
        color="continent")
    
    vline = alt.Chart(pd.DataFrame({'year': [year]})).mark_rule(strokeDash=[10, 10]).encode(x='year:N')
    
    chart = line + vline
    chart_final = chart.configure_axis(
        labelFontSize=14,
        titleFontSize=20
        ).configure_legend(
        titleFontSize=14
    ).properties(
        width=350,
        height=300)
    return chart_final.to_html()

# Setup callbacks/backend for world map

def get_para(year, col):
    col_name_dict = {'lifeExp': 'Life Expectancy',
                     'pop': 'Population',
                     'gdpPercap': 'GDP per Capita'
                    }
    
    col_max_scale_dict = {'lifeExp': 1000,
                          'pop': 2000,
                          'gdpPercap': 500
                         }
    
    scale = gapminder.groupby('year').sum()[col][year]/gapminder.groupby('year').sum()[col].max()
    
    return (col_name_dict[col], int(scale*col_max_scale_dict[col]))

@app.callback(
    Output('world_map', 'srcDoc'),
    Input('year-slider', 'value'),
    Input('topic_dropdown', 'value')
    )
def plot_world(year, col): # col = ['lifeExp', 'pop', 'gdpPercap']
    world_map = alt.topo_feature(data.world_110m.url, 'countries')
    background = alt.Chart(world_map).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        width=795,
        height=450
    ).project(type='equalEarth')
    
    df_pos = pd.read_csv('data/world_country.csv')
    df_pos = df_pos.iloc[:, 1:4]
    df_pos.rename (columns = {'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    
    gapminder_pos = gapminder.merge(df_pos)
    para, max_scale = get_para(year, col)
    
    points = alt.Chart(gapminder_pos[gapminder_pos['year'] == year]).mark_circle().encode(
        longitude='lon:Q',
        latitude='lat:Q',
        size = alt.Size(col, legend=None, scale=alt.Scale(range=[0, max_scale])),
        color = alt.Color('continent', legend=None),
        tooltip=['country', col]
    )
    
    text_year = alt.Chart({'values':[{}]}).mark_text(
        align='left', baseline='top'
    ).encode(
        x=alt.value(680),
        y=alt.value(10),
        size=alt.value(50),
        color=alt.value('lightgray'),
        text=alt.value(str(year))
    )

    text_para = alt.Chart({'values':[{}]}).mark_text(
        align='left', baseline='top'
    ).encode(
        x=alt.value(70),
        y=alt.value(10),
        size=alt.value(15),
        color=alt.value('gray'),
        text=alt.value(para)
    )
    final_map = background + points + text_year + text_para

    return final_map.to_html()

if __name__ == '__main__':
    app.run_server(debug=True)
