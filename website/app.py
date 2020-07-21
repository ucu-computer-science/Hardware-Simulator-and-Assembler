import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from bitarray.util import ba2hex

from modules.simulator import CPU

# COLOR PALETTE
# TABLES
table_main_color = '#2e003e'
table_header_color = '#2e003e'
table_main_font_color = '#e4dcf1'
table_header_font_color = '#e4dcf1'
# BUTTONS
button_color = '#283655'
button_font_color = '#f7f7f7'
# OTHER
background_color = 'black'
# TRANSPARENT LAYOUT FOR FIGURES
layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'url(assets/reset.css)']

with open("modules/program_examples/assembly_test4.bin", "r") as file:
    data = file.read()

cpu = CPU("risc3", "neumann", "special", data)


# def press_button():


def make_memory_slots():
    header_1 = []
    for i in range(0, 32, 4):
        header_1.append(
            " " + hex(i)[2:].rjust(2, "0") + " " + hex(i + 1)[2:].rjust(2, "0") + " " + hex(i + 2)[2:].rjust(2,
                                                                                                             "0") + " " + hex(
                i + 3)[2:].rjust(2, "0") + " |")
    header_1 = "".join(header_1)

    rows = []
    for i in range(0, 1024, 32):
        rows.append(hex(i)[2:].rjust(8, "0"))

    memory_data = []
    for i in range(0, len(cpu.data_memory.slots), 32 * 8):
        memory_data.append(ba2hex(cpu.data_memory.slots[i:i + 32 * 8]))

    fig = go.Figure(
        data=[go.Table(columnorder=[1, 2],
                       columnwidth=[80, 1000],
                       header=dict(values=["Addr       :  ", header_1], line_color=table_header_color,
                                   fill_color=table_header_color,
                                   align=['left', 'center'],
                                   font=dict(color=table_main_font_color, size=12), ),
                       cells=dict(values=[rows, memory_data], line_color=table_main_color,
                                  fill_color=table_main_color,
                                  align=['left', 'center'],
                                  font=dict(color=table_main_font_color, size=12), ))], layout=layout)
    fig.update_layout(height=1000,)
    return fig


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Button('Next', id='submit-val', n_clicks=0,
                style={"color": button_font_color, "background-color": button_color}),
    html.Div(id='simulator')
], style={'backgroundColor': background_color, 'bottom': '0', 'right': '0', 'left': '0',
          'top': '0'})


@app.callback(Output('simulator', 'children'),
              [Input('submit-val', 'n_clicks')])
def update_tables(n_clicks):
    cpu.web_next_instruction()
    return html.Div([
        html.Div(dcc.Graph(figure=make_memory_slots(), config={
            'displayModeBar': False})),
    ], style={'backgroundColor': background_color})


server = app.server
dev_server = app.run_server

# run the program
if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=True, processes=3, threaded=False)