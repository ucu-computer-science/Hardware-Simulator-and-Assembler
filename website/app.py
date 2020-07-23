#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

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
# ASSEMBLY/BINARY
assembly_bg_color = "#4E6585"
assembly_font_color = "#B3CBE1"
# OTHER
background_color = '#26273D'
title_color = '#C0C0DB'
text_color = '#9090AC'
# TRANSPARENT LAYOUT FOR FIGURES
layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'url(assets/reset.css)']

# LAYOUT
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([

    html.Div([html.Div([
        dcc.Markdown("ASSEMBLY SIMULATOR",
                     style={'color': title_color, 'font-family': "Roboto Mono, monospace", 'font-size': '25px',
                            'margin-left': 40, 'margin-top': 20, }),

        html.Div([
            dcc.Markdown("ASSEMBLY",
                         style={'color': text_color, 'font-family': "Roboto Mono, monospace", 'font-size': '20px',
                                'margin-left': 45, 'margin-top': 30, 'display': 'inline-block'}),
            dcc.Markdown("BINARY",
                         style={'color': text_color, 'font-family': "Roboto Mono, monospace", 'font-size': '20px',
                                'margin-left': 85, 'margin-top': 10, 'display': 'inline-block'}),

        ]),

        dcc.Textarea(id="input1", spellCheck='false', value="input assembly code here",
                     style={'width': 170, 'height': 400, 'display': 'inline-block', 'margin-right': 7,
                            'margin-left': 5, 'margin-top': 0,
                            "color": assembly_font_color, 'font-size': '15px',
                            "background-color": assembly_bg_color, 'font-family': "Roboto Mono, monospace"},
                     autoFocus='true', ),
        html.Div(id='assembly', style={'display': 'inline-block'}, )]),

        dcc.Markdown("CHOOSE ISA AND ASSEMBLE THE CODE:",
                     style={'color': text_color, 'font-family': "Roboto Mono, monospace", 'font-size': '14px',
                            'margin-left': 29, 'margin-top': 10, 'display': 'inline-block'}),


        html.Button('LOAD CODE', id='load_assembly', n_clicks=0,
                              style={'margin-left': 10, "color": button_font_color, "background-color": button_color,
                                     'width': 160, 'display': 'inline-block'}),


        html.Div([html.Button('Stack', id='assemble_risc1', n_clicks=0,
                              style={'margin-left': 10, "color": button_font_color, "background-color": button_color,
                                     'width': 160, 'display': 'inline-block'}),
                  html.Button('Register RISC', id='assemble_risc3', n_clicks=0,
                              style={'margin-left': 16, "color": button_font_color, "background-color": button_color,
                                     'width': 160, 'display': 'inline-block'})], style={"margin-bottom": 10}),

        html.Div([html.Button('Accumulator', id='assemble_risc2', n_clicks=0,
                              style={'margin-left': 10, "color": button_font_color, "background-color": button_color,
                                     'width': 160, 'display': 'inline-block'}),
                  html.Button('Register CISC', id='assemble_cisc', n_clicks=0,
                              style={'margin-left': 16, "color": button_font_color, "background-color": button_color,
                                     'width': 160, 'display': 'inline-block'})]),

    ],
        style={'display': 'block', 'height': '100px', 'margin-left': 14}, ),

    html.Div([html.Div(id='simulator'),
              html.Button('Execute next instruction', id='next-instruction', n_clicks=0,
                          style={"color": button_font_color, "background-color": button_color, 'margin-left': 400,
                                 'margin-top': 10}), ],
             style={'height': '100px', 'margin-top': 0, 'margin-left': 390, 'display': 'block'}),

    # Hidden div for storing assembly code
    html.Div(id='intermediate-value', style={'display': 'none'})
])



# INPUT AND BUTTONS

@app.callback(Output('intermediate-value', 'children'),
              [Input('load_assembly', 'n_clicks')],
              [State('input1', 'value')])
def intermediate(n_clicks, value):
    if not value or value == "input assembly code here":
        binary_program = ''
        intermediate.cpu = CPU("risc3", "neumann", "special", binary_program)
        return binary_program
    else:
        try:
            binary_program = Assembler("risc3", value).binary_code
            intermediate.cpu = CPU("risc3", "neumann", "special", binary_program)
            return binary_program
        except AssemblerError as exception:
            binary_program = "AssemblerError: {}".format(exception.args[0])
            intermediate.cpu = CPU("risc3", "neumann", "special", "")
            return binary_program



@app.callback(Output('simulator', 'children'),
              [Input('next-instruction', 'n_clicks'),
               Input('intermediate-value', 'value')])
# TODO: how do I input a cpu??? what the heck
def update_tables(n_clicks, value):
    intermediate()
    cpu = intermediate.cpu
    cpu.web_next_instruction()
    time.sleep(0.05)
    return html.Div([
        html.Div(dcc.Graph(figure=make_instruction_slot(cpu), config={
            'displayModeBar': False, 'staticPlot': True}), style={'display': 'inline-block'}, ),
        html.Div(dcc.Graph(figure=make_registers_slots(cpu), config={
            'displayModeBar': False, 'staticPlot': True}), style={'display': 'inline-block'}, ),
        html.Div(dcc.Graph(figure=make_output_slot(cpu), config={
            'displayModeBar': False, 'staticPlot': True}), style={'display': 'inline-block'}, ),
        html.Div(dcc.Graph(figure=make_memory_slots(cpu), config={
            'displayModeBar': False})),
    ], style={'margin-top': -100})




@app.callback(Output('assembly', 'children'),
              [Input('assemble_risc3', 'n_clicks'),
               Input('intermediate-value', 'value')])
def make_assembly_input(n_clicks, value):
    if not value or value == "input assembly code here":
        binary_program = ""
    else:
        try:
            binary_program = Assembler("risc3", value).binary_code
        except AssemblerError as exception:
            binary_program = "AssemblerError: {}".format(exception.args[0])
    return dcc.Textarea(value=binary_program,
                        style={'width': 170, 'height': 400, "color": assembly_font_color, 'font-size': '15px',
                               "background-color": table_main_color, 'font-family': "Roboto Mono, monospace"},
                        disabled=True)















# # CPU
# binary_program = ''
# cpu = CPU("risc3", "neumann", "special", binary_program)






# GRAPHIC ELEMENTS
def make_instruction_slot(cpu):
    """
    Return a table figure, with information from the instruction of the CPU.
    """
    fig = go.Figure(
        data=[
            go.Table(header=dict(values=[f"{cpu.instruction.to01()}\n"], line_color=table_header_color,
                                 fill_color=table_header_color,
                                 align=['center', 'center'],
                                 font=dict(color=table_main_font_color, size=20), height=40), )], layout=layout)
    fig.update_layout(height=160, margin=dict(b=25, l=30, r=50), width=300,
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20))
    fig.update_layout(
        title={
            'text': "NEXT INSTRUCTION",
            'y': 0.52,
            'x': 0.459,
            'xanchor': 'center',
            'yanchor': 'top'},
        font=dict(
            family="Roboto Mono, monospace",
            size=13,
            color=text_color,
        )
    )

    return fig


def make_output_slot(cpu):
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
                                 align=['left', 'center'], height=40, font=dict(color=table_main_font_color, size=20)),
                     )], layout=layout)
    fig.update_layout(height=160, margin=dict(b=25, r=0, l=50), width=330,
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20))

    fig.update_layout(
        title={
            'text': "OUTPUT DEVICE",
            'y': 0.52,
            'x': 0.57,
            'xanchor': 'center',
            'yanchor': 'top'},
        font=dict(
            family="Roboto Mono, monospace",
            size=13,
            color=text_color,
        )
    )
    return fig


def make_registers_slots(cpu):
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
    fig.update_layout(height=150, width=400, margin=dict(t=10, l=55, r=46, b=1),
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20))
    fig.layout['template']['data']['table'][0]['header']['fill']['color'] = 'rgba(0,0,0,0)'
    fig.layout['template']['data']['table'][0]['header']['line']['color'] = 'rgba(0,0,0,0)'

    fig.update_layout(
        title={
            'text': "REGISTERS",
            'y': 0.99,
            'x': 0.489,
            'xanchor': 'center',
            'yanchor': 'top'},
        font=dict(
            family="Roboto Mono, monospace",
            size=13,
            color=text_color,
        )
    )

    return fig


def make_memory_slots(cpu):
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
        data=[go.Table(columnwidth=7,
                       header=dict(values=headers, line_color=table_header_color,
                                   fill_color=table_header_color,
                                   align=['left', 'center'],
                                   font=dict(color=table_main_font_color, size=12), ),
                       cells=dict(values=rows, line_color=table_header_color,
                                  fill_color=table_main_color,
                                  align=['left', 'center'],
                                  font=dict(color=table_main_font_color, size=12), ))], layout=layout)
    fig.update_layout(width=1032, height=450, margin=dict(t=24, b=10, r=0, l=30),
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20),
                      )
    fig.layout.update(dragmode=False)

    fig.update_layout(
        title={
            'text': "MEMORY STACK",
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        font=dict(
            family="Roboto Mono, monospace",
            size=13,
            color=text_color,
        )
    )

    return fig




# run the program
# TODO: make table undraggable (maybe switch to dash table)
# TODO: Add error field (maybe in binary textarea)
# TODO: Add I/O choice, neumann and harvard
# TODO: smaller memory, bigger assembler, change memory title
# TODO: HEX-представлення команд на додачу до двійкового. Варіант -- як опцію BIN/HEX
# TODO: access program examples and instructions
# TODO: multi-user access

if __name__ == '__main__':
    # SERVER LAUNCH
    server = app.server
    dev_server = app.run_server
    app.run_server(debug=True, threaded=True)
    # app.run_server(debug=True, processes=3, threaded=False)
