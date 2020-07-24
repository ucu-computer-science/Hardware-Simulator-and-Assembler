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
import uuid
# Might need them for help page and etc
from flask import Flask, render_template, url_for
import json

from modules.processor import CPU
from modules.assembler import Assembler, AssemblerError

# CPU DICTIONARY (key=user.id, value=cpu)
cpu_dict = dict()

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
not_working_bg = '#5C5C5C'
not_working_text = '#AFAFB2'
# TRANSPARENT LAYOUT FOR FIGURES
layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'url(assets/reset.css)']

# Create app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, routes_pathname_prefix='/')
app.title = "ASSEMBLY SIMULATOR"


# Create user id
@app.callback(Output('target', 'children'), [Input('input', 'children')])
def get_ip(value):
    """
    Return randomly generated id each time new session starts
    :param value: is not used (is here by default)
    :return: random id
    """
    session_id = str(uuid.uuid4())
    return session_id


# MAIN LAYOUT
app.layout = html.Div([
    # Hidden div for a help page
    html.Div(id="hidden"),
    # Div for an id
    html.Div(id='target', style={'display': 'none'}),
    html.Div(id='input', style={'display': 'none'}),

    html.Div([html.Div([
        dcc.Markdown("ASSEMBLY SIMULATOR",
                     style={'color': title_color, 'font-family': "Roboto Mono, monospace",
                            'font-size': '25px',
                            'margin-left': 95, 'margin-top': 20, }),

        html.Div([
            dcc.Markdown("ASSEMBLY",
                         style={'color': text_color, 'font-family': "Roboto Mono, monospace",
                                'font-size': '20px',
                                'margin-left': 80, 'margin-top': 30, 'display': 'inline-block'}),
            dcc.Markdown("BINARY",
                         style={'color': text_color, 'font-family': "Roboto Mono, monospace",
                                'font-size': '20px',
                                'margin-left': 130, 'margin-top': 10, 'display': 'inline-block'}),

        ]),

        # Textarea for input of assembly code
        dcc.Textarea(id="input1", spellCheck='false', value="input assembly code here",
                     style={'width': 250, 'height': 400, 'display': 'inline-block',
                            'margin-right': 7,
                            'margin-left': 5, 'margin-top': 0,
                            "color": assembly_font_color, 'font-size': '15px',
                            "background-color": assembly_bg_color,
                            'font-family': "Roboto Mono, monospace"},
                     autoFocus='true', ),
        # Textarea for output of binary code
        html.Div(id='assembly', style={'display': 'inline-block'}, )]),

        dcc.Markdown("CHOOSE ISA AND ASSEMBLE THE CODE:",
                     style={'color': text_color, 'font-family': "Roboto Mono, monospace",
                            'font-size': '14px',
                            'margin-left': 80, 'margin-top': 10, 'display': 'inline-block'}),

        # Buttons with ISA variants
        html.Div([html.Button('Stack', id='assemble_risc1', n_clicks=0,
                              style={'margin-left': 50, "color": not_working_text,
                                     "background-color": not_working_bg,
                                     'width': 160, 'display': 'inline-block'}),
                  html.Button('Register RISC', id='assemble_risc3', n_clicks=0,
                              style={'margin-left': 16, "color": button_font_color,
                                     "background-color": button_color,
                                     'width': 160, 'display': 'inline-block'})],
                 style={"margin-bottom": 10}),

        html.Div([html.Button('Accumulator', id='assemble_risc2', n_clicks=0,
                              style={'margin-left': 50, "color": not_working_text,
                                     "background-color": not_working_bg,
                                     'width': 160, 'display': 'inline-block'}),
                  html.Button('Register CISC', id='assemble_cisc', n_clicks=0,
                              style={'margin-left': 16, "color": not_working_text,
                                     "background-color": not_working_bg,
                                     'width': 160, 'display': 'inline-block'})]),

    ],
        style={'display': 'block', 'height': '100px', 'margin-left': 14}, ),

    # Simulator of the processor and additional switch buttons
    html.Div([html.Div(id='simulator'),
              html.Button('Execute next instruction', id='next-instruction', n_clicks=0,
                          style={"color": button_font_color, "background-color": button_color,
                                 'margin-left': 400,
                                 'margin-top': 10, 'display': 'inline-block'}),

              # TODO: link to a help page
              # dcc.Link('HELP', href='/help', id='help',
              #          style={"color": button_font_color,
              #                 'margin-left': 100,
              #                 'margin-top': 10, 'display': 'inline-block'
              #                 })
              ],
             style={'height': '100px', 'margin-top': 0, 'margin-left': 450, 'display': 'block'}),

])


# INPUT-OUTPUT ELEMENTS AND BUTTONS
@app.callback(Output('simulator', 'children'),
              [Input('next-instruction', 'n_clicks'),
               Input('target', 'children')])
def update_tables(n_clicks, user_id):
    """
    If there is a CPU attached to a session,
    activates next instruction in it and
    returns changed tables and slots.
    :param n_clicks: is not used (is here by default)
    :param user_id: id of the session/user, by which CPU can be accessed
    :return: html div with visualised processor and some buttons
    """
    if user_id in cpu_dict:
        cpu_dict[user_id].web_next_instruction()
    # Without a small break tables produces some glitches from time to time
    time.sleep(0.05)
    return html.Div([

        # Next instruction and current output slots
        html.Div([html.Div([html.Div([html.Div(dcc.Graph(figure=make_instruction_slot(user_id), config={
            'displayModeBar': False, 'staticPlot': True})),
                                      html.Div(dcc.Graph(figure=make_output_slot(user_id), config={
                                          'displayModeBar': False, 'staticPlot': True}))],
                                     style={'display': 'inline-block'}, ),
                            html.Div(dcc.Graph(figure=make_registers_slots(user_id), config={
                                'displayModeBar': False, 'staticPlot': True}), style={'display': 'inline-block'}, ), ],
                           style={'display': 'block', 'margin-bottom': -167}, ),

                  # Additional buttons for switching I/O modes and architectures
                  html.Div([dcc.Markdown("SWITCH ARCHITECTURES:",
                                         style={'color': text_color, 'font-family': "Roboto Mono, monospace",
                                                'font-size': '14px',
                                                'margin-left': 80, 'margin-top': 0}),
                            html.Div([html.Button('Von Neumann', id='no', n_clicks=0,
                                                  style={'margin-left': 10, "color": button_font_color,
                                                         "background-color": button_color,
                                                         'width': 150, 'display': 'inline-block'}),
                                      html.Button('Harvard', id='no', n_clicks=0,
                                                  style={'margin-left': 10, 'margin-bottom': 0,
                                                         "color": not_working_text,
                                                         "background-color": not_working_bg,
                                                         'width': 150, 'display': 'inline-block'})],
                                     style={"margin-bottom": 10}),

                            dcc.Markdown("SWITCH I/O MODES:",
                                         style={'color': text_color, 'font-family': "Roboto Mono, monospace",
                                                'font-size': '14px',
                                                'margin-left': 80, 'margin-top': 10}),

                            html.Div([html.Button('Memory-Mapped', id='no', n_clicks=0,
                                                  style={'margin-bottom': 10, 'margin-left': 10,
                                                         "color": not_working_text,
                                                         "background-color": not_working_bg,
                                                         'width': 150, 'display': 'inline-block'}),
                                      html.Button('Special com-s', id='no', n_clicks=0,
                                                  style={'margin-left': 10, "color": button_font_color,
                                                         "background-color": button_color,
                                                         'width': 150, 'display': 'inline-block'})],
                                     style={'display': 'inline-block'}, ), ],
                           style={'display': 'block', 'margin-left': 645}), ], style={'margin-top': 20}),

        # Memory representation
        html.Div(dcc.Graph(figure=make_memory_slots(user_id), config={
            'displayModeBar': False})),
    ], style={'margin-top': -100})


@app.callback(Output('assembly', 'children'),
              [Input('assemble_risc3', 'n_clicks'),
               Input('target', 'children')],
              [State('input1', 'value')])
def make_assembly_input_risk3(n_clicks, user_id, value):
    """
    (For register RISC architecture)
    If there is an assembly code written in the textarea,
    writes it into the cpu, attached to session/user id.
    Returns a text area with a corresponding binary code.
    :param n_clicks: is not used (is here by default)
    :param user_id: id of the session/user, by which CPU can be accessed
    :param value: assembly code
    :return: text area with a binary code/assembler error
    """
    global cpu_dict
    if not value or value == "input assembly code here":
        binary_program = ""
    else:
        try:
            binary_program = Assembler("risc3", value).binary_code
            cpu_dict[user_id] = CPU("risc3", "neumann", "special", binary_program)
        except AssemblerError as err:
            binary_program = f'{err.args[0]}'
    return dcc.Textarea(value=binary_program,
                        style={'width': 170, 'height': 400, "color": assembly_font_color, 'font-size': '15px',
                               "background-color": table_main_color, 'font-family': "Roboto Mono, monospace"},
                        disabled=True)


@app.callback(Output('assembly', 'children'),
              [Input('assemble_risc2', 'n_clicks'),
               Input('target', 'children')],
              [State('input1', 'value')])
def make_assembly_input_risk3(n_clicks, user_id, value):
    """
    (For Accumulator architecture)
    If there is an assembly code written in the textarea,
    writes it into the cpu, attached to session/user id.
    Returns a text area with a corresponding binary code.
    :param n_clicks: is not used (is here by default)
    :param user_id: id of the session/user, by which CPU can be accessed
    :param value: assembly code
    :return: text area with a binary code/assembler error
    """
    global cpu_dict
    if not value or value == "input assembly code here":
        binary_program = ""
    else:
        try:
            binary_program = Assembler("risc2", value).binary_code
            cpu_dict[user_id] = CPU("risc2", "neumann", "special", binary_program)
        except AssemblerError as err:
            binary_program = f'{err.args[0]}'
    return dcc.Textarea(value=binary_program,
                        style={'width': 170, 'height': 400, "color": assembly_font_color, 'font-size': '15px',
                               "background-color": table_main_color, 'font-family': "Roboto Mono, monospace"},
                        disabled=True)


@app.callback(Output('assembly', 'children'),
              [Input('assemble_risc1', 'n_clicks'),
               Input('target', 'children')],
              [State('input1', 'value')])
def make_assembly_input_risk3(n_clicks, user_id, value):
    """
    (For Stack architecture)
    If there is an assembly code written in the textarea,
    writes it into the cpu, attached to session/user id.
    Returns a text area with a corresponding binary code.
    :param n_clicks: is not used (is here by default)
    :param user_id: id of the session/user, by which CPU can be accessed
    :param value: assembly code
    :return: text area with a binary code/assembler error
    """
    global cpu_dict
    if not value or value == "input assembly code here":
        binary_program = ""
    else:
        try:
            binary_program = Assembler("risc1", value).binary_code
            cpu_dict[user_id] = CPU("risc1", "neumann", "special", binary_program)
        except AssemblerError as err:
            binary_program = f'{err.args[0]}'
    return dcc.Textarea(value=binary_program,
                        style={'width': 170, 'height': 400, "color": assembly_font_color, 'font-size': '15px',
                               "background-color": table_main_color, 'font-family': "Roboto Mono, monospace"},
                        disabled=True)


@app.callback(Output('assembly', 'children'),
              [Input('assemble_cisc', 'n_clicks'),
               Input('target', 'children')],
              [State('input1', 'value')])
def make_assembly_input_risk3(n_clicks, user_id, value):
    """
    (For register CISC architecture)
    If there is an assembly code written in the textarea,
    writes it into the cpu, attached to session/user id.
    Returns a text area with a corresponding binary code.
    :param n_clicks: is not used (is here by default)
    :param user_id: id of the session/user, by which CPU can be accessed
    :param value: assembly code
    :return: text area with a binary code/assembler error
    """
    global cpu_dict
    if not value or value == "input assembly code here":
        binary_program = ""
    else:
        try:
            binary_program = Assembler("cisc", value).binary_code
            cpu_dict[user_id] = CPU("cisc", "neumann", "special", binary_program)
        except AssemblerError as err:
            binary_program = f'{err.args[0]}'
    return dcc.Textarea(value=binary_program,
                        style={'width': 170, 'height': 400, "color": assembly_font_color, 'font-size': '15px',
                               "background-color": table_main_color, 'font-family': "Roboto Mono, monospace"},
                        disabled=True)


# TODO: a help page callback
# @app.callback(Output('hidden', 'children'),
#               [Input('help', 'href')])
# def help_page(href):
#     return dcc.Location(pathname=href, id="help_page")


# CREATE GRAPHIC ELEMENTS
def make_instruction_slot(user_id):
    """
    Return a table figure, with information from the instruction of the CPU,
    which belongs to that exact user and session.
    :return: plotly table
    """
    if user_id not in cpu_dict:
        cpu = CPU("risc3", "neumann", "special", "")
    else:
        cpu = cpu_dict[user_id]
    fig = go.Figure(
        data=[
            go.Table(header=dict(values=[f"{cpu.instruction.to01()}\n"],
                                 line_color=table_header_color,
                                 fill_color=table_header_color,
                                 align=['center', 'center'],
                                 font=dict(color=table_main_font_color, size=20), height=40), )], layout=layout)
    fig.update_layout(height=60, margin=dict(b=0, l=65, r=0, t=20), width=285,
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20))
    fig.update_layout(
        title={
            'text': "NEXT INSTRUCTION",
            'y': 0.99,
            'x': 0.60,
            'xanchor': 'center',
            'yanchor': 'top'},
        font=dict(
            family="Roboto Mono, monospace",
            size=13,
            color=text_color,
        )
    )

    return fig


def make_output_slot(user_id):
    """
    Return a table figure, with information from the output device of the CPU,
    which belongs to that exact user and session.
    :return: plotly table
    """
    if user_id not in cpu_dict:
        cpu = CPU("risc3", "neumann", "special", '')
    else:
        cpu = cpu_dict[user_id]
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
    fig.update_layout(height=75, margin=dict(b=0, r=0, l=35, t=25), width=315,
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20))

    fig.update_layout(
        title={
            'text': "OUTPUT DEVICE",
            'y': 0.92,
            'x': 0.54,
            'xanchor': 'center',
            'yanchor': 'top'},
        font=dict(
            family="Roboto Mono, monospace",
            size=13,
            color=text_color,
        )
    )
    return fig


def make_registers_slots(user_id):
    """
    Return a table figure, with information from registers of the CPU,
    which belongs to that exact user and session.
    :return: plotly table
    """
    if user_id not in cpu_dict:
        cpu = CPU("risc3", "neumann", "special", '')
    else:
        cpu = cpu_dict[user_id]
    items = [(value.name, value._state.tobytes().hex()) for key, value in
             cpu.registers.items()]
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
    fig.update_layout(height=140, width=329, margin=dict(t=10, l=15, r=15, b=0),
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


def make_memory_slots(user_id):
    """
    Return a table figure, with information from the memory of the CPU,
    which belongs to that exact user and session.
    :return: plotly table
    """
    if user_id not in cpu_dict:
        cpu = CPU("risc3", "neumann", "special", '')
    else:
        cpu = cpu_dict[user_id]
    headers = ["Addr   :  "]
    for i in range(0, 32, 4):
        headers.append(f"{hex(i)[2:].rjust(2, '0')} {hex(i + 1)[2:].rjust(2, '0')} "
                       f"{hex(i + 2)[2:].rjust(2, '0')} {hex(i + 3)[2:].rjust(2, '0')}")

    rows = []
    for i in range(0, 1024, 32):
        rows.append(hex(i)[2:].rjust(8, "0"))

    # Read cpu data
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
    fig.update_layout(width=980, height=450, margin=dict(t=24, b=10, r=0, l=30),
                      font=dict(family="Roboto Mono, monospace", color=table_main_font_color, size=20),
                      )
    fig.layout.update(dragmode=False)

    fig.update_layout(
        title={
            'text': "MEMORY",
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


# TODO: make table undraggable (maybe switch to dash table)
# TODO: HEX-представлення команд на додачу до двійкового. Варіант -- як опцію BIN/HEX
# TODO: access program examples and instructions
# TODO: a hidden div for storing information about architecture (like "(neumann, special) (it will be by default),
#  (harvard, mmio)"), so I can read from it before creating cpu in the first place
# Run the program
if __name__ == '__main__':
    # SERVER LAUNCH
    dev_server = app.run_server
    app.run_server(debug=True, threaded=True)
