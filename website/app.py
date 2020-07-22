import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from bitarray.util import ba2hex

from modules.simulator import CPU
from modules.assembler import Assembler, AssemblerError

# COLOR PALETTE
# TABLES
table_main_color = '#414364'
table_header_color = '#414364'
table_main_font_color = '#93B6D5'
table_header_font_color = '#93B6D5'
# BUTTONS
button_color = '#46547C'
button_font_color = '#FCD848'
# OTHER
background_color = '#26273D'
# TRANSPARENT LAYOUT FOR FIGURES
layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'url(assets/reset.css)']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([html.Div([
    dcc.Textarea(id="input1", style={'display': 'inline-block'}, ),
    html.Div(id='assembly', style={'display': 'inline-block'}, ),
    html.Div(id='simulator', style={'display': 'inline-block'}, ),
]),
    html.Div([html.Div([
        html.Button('Assemble', id='assemble_input', n_clicks=0,
                    style={"color": button_font_color, "background-color": button_color}),
    ], style={'bottom': '0', 'right': '0', 'left': '0',
              'top': '0', 'display': 'inline-block'}),
        html.Button('Next', id='next-instruction', n_clicks=0,
                    style={"color": button_font_color, "background-color": button_color}),
    ], style={'bottom': '0', 'right': '0', 'left': '0',
              'top': '0', 'display': 'inline-block'})
])


@app.callback(Output('simulator', 'children'),
              [Input('next-instruction', 'n_clicks')])
def update_tables(n_clicks):
    cpu.web_next_instruction()
    time.sleep(0.05)
    return html.Div([
        html.Div(dcc.Graph(figure=make_instruction_slot(), config={
            'displayModeBar': False, 'staticPlot': True}), style={'display': 'inline-block'}, ),
        html.Div(dcc.Graph(figure=make_registers_slots(), config={
            'displayModeBar': False, 'staticPlot': True}), style={'display': 'inline-block'}, ),
        html.Div(dcc.Graph(figure=make_output_slot(), config={
            'displayModeBar': False, 'staticPlot': True}), style={'display': 'inline-block'}, ),
        html.Div(dcc.Graph(figure=make_memory_slots(), config={
            'displayModeBar': False})),
    ])


@app.callback(Output('assembly', 'children'),
              [Input('assemble_input', 'n_clicks')],
              [State('input1', 'value')])
def make_assembly_input(n_clicks, value):
    global binary_program
    global cpu
    if value:
        binary_program = Assembler("risc3", value).binary_code
        cpu = CPU("risc3", "neumann", "special", binary_program)
    else:
        binary_program = ""
    return binary_program

binary_program = ''
cpu = CPU("risc3", "neumann", "special", binary_program)


def make_instruction_slot():
    """
    Return a table figure, with information from the instruction of the CPU.
    """
    fig = go.Figure(
        data=[
            go.Table(header=dict(values=[f"{cpu.instruction.to01()}\n"], line_color=table_header_color,
                                 fill_color=table_header_color,
                                 align=['center', 'center'],
                                 font=dict(color=table_main_font_color, size=20), height=40), )], layout=layout)
    fig.update_layout(height=160, margin=dict(b=25), width=380,
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20))

    return fig


def make_output_slot():
    """
    Return a table figure, with information from the instruction of the CPU.
    """
    shell_slots = []
    for port, device in cpu.ports_dictionary.items():
        shell_slots.append(str(device))
    # print(shell_slots)
    fig = go.Figure(
        data=[
            go.Table(header=dict(values=shell_slots, line_color=table_header_color,
                                 fill_color=table_header_color,
                                 align=['left', 'center'], height=40), )], layout=layout)
    fig.update_layout(height=160, margin=dict(b=25), width=430,
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20))

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
    fig.update_layout(height=150, width=300, margin=dict(t=10, l=1, r=1, b=1),
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20))
    fig.layout['template']['data']['table'][0]['header']['fill']['color'] = 'rgba(0,0,0,0)'
    fig.layout['template']['data']['table'][0]['header']['line']['color'] = 'rgba(0,0,0,0)'

    return fig


def make_memory_slots():
    """
    Return a table figure, with information from the memory of the CPU.
    """
    headers = ["Addr   :  "]
    for i in range(0, 32, 4):
        headers.append(f"{hex(i)[2:].rjust(2, '0')} {hex(i + 1)[2:].rjust(2, '0')} "
                       f"{hex(i + 2)[2:].rjust(2, '0')} {hex(i + 3)[2:].rjust(2, '0')}")

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
        data=[go.Table(columnwidth=10,
                       header=dict(values=headers, line_color=table_header_color,
                                   fill_color=table_header_color,
                                   align=['left', 'center'],
                                   font=dict(color=table_main_font_color, size=12), ),
                       cells=dict(values=rows, line_color=table_header_color,
                                  fill_color=table_main_color,
                                  align=['left', 'center'],
                                  font=dict(color=table_main_font_color, size=12), ))], layout=layout)
    fig.update_layout(width=1100, height=400, margin=dict(t=10, b=0),
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20),
                      )
    fig.layout.update(dragmode=False)
    return fig


server = app.server
dev_server = app.run_server

# run the program
# TODO: make table undraggable (maybe switch to dash table)
# TODO: Add error field

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
    # app.run_server(debug=True, processes=3, threaded=False)
