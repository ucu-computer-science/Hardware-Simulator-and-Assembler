import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def make_instruction_table(instruction):
    fig = go.Figure(data=[go.Table(header=dict(values=["{}".format(instruction)]))])
    fig.update_layout(width=300, height=300)
    return fig


def make_registers_table(reg1, reg2, reg3, reg4):
    fig = go.Figure(data=[go.Table(cells=dict(values=[['REG01 {}'.format(reg1),
                                                       'REG02 {}'.format(reg2)], ['REG03 {}'.format(reg3),
                                                                                  'REG04 {}'.format(reg4)]], ), )])
    fig.layout['template']['data']['table'][0]['header']['fill']['color'] = 'rgba(0,0,0,0)'

    fig.update_layout(width=300, height=300)
    return fig


def make_memory_table(*args):
    fig = go.Figure(data=[go.Table(cells=dict(values=args, align=['left', 'center'],
                                              font_size=12,
                                              height=25))])
    fig.layout['template']['data']['table'][0]['header']['fill']['color'] = 'rgba(0,0,0,0)'
    fig.update_layout(width=900, height=800)
    return fig


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Button('Next', id='submit-val', n_clicks=0, style={'display': 'inline-block'}),
    html.Div(id='simulator')
])


@app.callback(Output('simulator', 'children'),
              [Input('submit-val', 'n_clicks')])
def update_tables(n_clicks):
    return html.Div([
        html.Div(dcc.Graph(figure=make_instruction_table(str(n_clicks)), config={
    'displayModeBar': False,}
    ), style={'display': 'inline-block'}),
        html.Div(dcc.Graph(figure=make_registers_table(n_clicks, "0010", "00ff", "000e")),
                 style={'display': 'inline-block'}),
        html.Div(dcc.Graph(figure=make_memory_table(["0" * 95] * 100))),
    ])


server = app.server
dev_server = app.run_server

# run the program
if __name__ == '__main__':
    app.run_server(debug=True)
