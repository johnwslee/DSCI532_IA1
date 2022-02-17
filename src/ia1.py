import altair as alt
from dash import Dash, html, dcc, Input, Output
from gapminder import gapminder

# Read in global data
gapminder_df = gapminder

# Setup app and layout/frontend
app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = ia1.server
app.layout = html.Div([
        dcc.Dropdown(
            id='y_axis', value='lifeExp',
            options=[{'label':i, 'value': i} for i in ['lifeExp', 'pop', 'gdpPercap']]),
        html.Iframe(
            id='scatter',
            style={'border-width': '0', 'width': '100%', 'height': '400px'})])

# Setup callbacks/backend
@app.callback(
    Output('scatter', 'srcDoc'),
    Input('y_axis', 'value'))
def plot_altair(y_axis):
    chart = alt.Chart(gapminder_df).mark_point().encode(
        alt.X('year', scale=alt.Scale(domain=(1950, 2007))),
        y=y_axis,
        color="continent",
        tooltip='country').interactive()
    return chart.to_html()

if __name__ == '__main__':
    app.run_server(debug=True)