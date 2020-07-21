import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from bitarray.util import ba2hex

from modules.simulator import CPU

# COLOR PALETTE
# TABLES
table_main_color = '#414364'
table_header_color = '#414364'
table_main_font_color = '#93B6D5'
table_header_font_color = '#93B6D5'
# BUTTONS
button_color = '#46547C'
button_font_color = '#EAB646'
# OTHER
background_color = '#26273D'
# TRANSPARENT LAYOUT FOR FIGURES


# TRANSPARENT LAYOUT FOR FIGURES
layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'url(assets/reset.css)']

with open("modules/program_examples/assembly_test6.bin", "r") as file:
    data = file.read()

cpu = CPU("risc3", "neumann", "special", data)


def make_instruction_slot():
    """
    Return a table figure, with information from the instruction of the CPU.
    """
    fig = go.Figure(
        data=[
            go.Table(header=dict(values=[f"{cpu.instruction.to01()}\n"], line_color=table_header_color,
                                 fill_color=table_header_color,
                                 align=['left', 'center'],
                                 font=dict(color=table_main_font_color, size=20), height=40), )], layout=layout)
    fig.update_layout(height=200, margin=dict(b=10), width=380)

    return fig


def make_output_slot():
    """
    Return a table figure, with information from the instruction of the CPU.
    """
    shell_slots = []
    for port, device in cpu.ports_dictionary.items():
        shell_slots.append(str(device))
    fig = go.Figure(
        data=[
            go.Table(header=dict(values=shell_slots, line_color=table_header_color,
                                 fill_color=table_header_color,
                                 align=['left', 'center'],
                                 font=dict(color=table_main_font_color, size=20), height=40), )], layout=layout)
    fig.update_layout(height=200, margin=dict(b=10), width=500)

    return fig


def make_registers_slots():
    """
    Return a table figure, with information from registers of the CPU.
    """
    items = [(value.name, value._state.tobytes().hex()) for key, value in cpu.registers.items()]
    values = [[], []]
    for i in range(1, len(items), 2):
        values[0].append(f" {(items[i - 1][0] + ':').ljust(4, ' ')} {items[i - 1][1]}  ")
        values[1].append(f"{(items[i][0] + ':').ljust(4, ' ')} {items[i][1]}\n")

    fig = go.Figure(
        data=[
            go.Table(cells=dict(values=values, line_color=table_header_color,
                                fill_color=table_header_color,
                                align=['left', 'center'],
                                font=dict(color=table_main_font_color, size=15), height=25),
                     )], layout=layout)
    fig.update_layout(height=150, width=300, margin=dict(t=10, l=1, r=1, b=1))
    fig.layout['template']['data']['table'][0]['header']['fill']['color'] = 'rgba(0,0,0,0)'
    fig.layout['template']['data']['table'][0]['header']['line']['color'] = 'rgba(0,0,0,0)'

    return fig


def make_memory_slots():
    """
    Return a table figure, with information from the memory of the CPU.
    """
    headers = ["Addr       :  "]
    for i in range(0, 32, 4):
        headers.append(hex(i)[2:].rjust(2, "0") + " " + hex(i + 1)[2:].rjust(2, "0") + " " + hex(i + 2)[2:].rjust(2,
                                                                                                                  "0") + " " + hex(
            i + 3)[2:].rjust(2, "0"))

    rows = []
    for i in range(0, 1024, 32):
        rows.append(hex(i)[2:].rjust(8, "0"))

    memory_data = [[], [], [], [], [], [], [], []]
    for i in range(0, len(cpu.data_memory.slots), 32 * 8):
        string = ba2hex(cpu.data_memory.slots[i:i + 32 * 8])
        for x in range(8):
            memory_data[x].append(" ".join([string[8 * x:8 * x + 8][y:y + 2] for y in range(0, 8, 2)]))

    rows = [rows] + memory_data
    fig = go.Figure(
        data=[go.Table(columnwidth=50,
                       header=dict(values=headers, line_color=table_header_color,
                                   fill_color=table_header_color,
                                   align=['left', 'center'],
                                   font=dict(color=table_main_font_color, size=12), ),
                       cells=dict(values=rows, line_color=table_header_color,
                                  fill_color=table_main_color,
                                  align=['left', 'center'],
                                  font=dict(color=table_main_font_color, size=12), ))], layout=layout)
    fig.update_layout(height=850, margin=dict(t=10, b=10))
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
        html.Div(dcc.Graph(figure=make_instruction_slot(), config={
            'displayModeBar': False}), style={'display': 'inline-block'}, ),
        html.Div(dcc.Graph(figure=make_registers_slots(), config={
            'displayModeBar': False}), style={'display': 'inline-block'}, ),
        html.Div(dcc.Graph(figure=make_output_slot(), config={
            'displayModeBar': False}), style={'display': 'inline-block'}, ),
        html.Div(dcc.Graph(figure=make_memory_slots(), config={
            'displayModeBar': False})),
    ], style={'backgroundColor': background_color})


server = app.server
dev_server = app.run_server

# run the program
if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=True, processes=3, threaded=False)
