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

# Imports from the project
from modules.processor import CPU
from modules.assembler import Assembler, AssemblerError
from website.color_palette_and_layout import table_header, table, button, assembly, background_color, title_color, \
    text_color, not_working, layout, external_stylesheets

# CPU DICTIONARY ( key=user.id, value=[cpu, buttons list (number of clicks)] )
user_dict = dict()
# Numbers of buttons (used to change type of isa during cpu creation, are same for every session and user)
buttons = {0: 'risc1', 1: 'risc2', 2: 'risc3', 3: 'cisc'}

# Create app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "ASSEMBLY SIMULATOR"

# MAIN LAYOUT
app.layout = html.Div([

    # "MAIN MENU"
    html.Div([
        # Title
        dcc.Markdown("ASSEMBLY SIMULATOR",
                     style={'color': title_color, 'font-family': "Roboto Mono, monospace",
                            'font-size': '25px', 'display': 'inline-block'}),

        # Dropdowns for isa, architecture and i/o mode
        html.Div([

            html.Div([

                dcc.Dropdown(
                    id='isa-dropdown',
                    options=[
                        {'label': 'REGISTER RISC', 'value': 'risc3'},
                        {'label': 'REGISTER CISC', 'value': 'cisc', 'disabled': True},
                        {'label': 'STACK', 'value': 'risc1'},
                        {'label': 'ACCUMULATOR', 'value': 'risc2'},
                    ],
                    value='risc3',
                    style={'width': 200},
                    clearable=False,
                ),
            ], style={'display': 'inline-block'}),

            html.Div([

                dcc.Dropdown(
                    id='architecture-dropdown',
                    options=[
                        {'label': 'VON NEUMANN', 'value': 'neumann'},
                        {'label': 'HARVARD', 'value': 'harvard', 'disabled': True},
                    ],
                    value='neumann',
                    style={'width': 200},
                    clearable=False,
                ),

            ], style={'display': 'inline-block'}),

            html.Div([

                dcc.Dropdown(
                    id='io-dropdown',
                    options=[
                        {'label': 'MEMORY-MAPPED', 'value': 'mmio', 'disabled': True},
                        {'label': 'SPECIAL COMMANDS', 'value': 'special'},
                    ],
                    value='special',
                    style={'width': 200},
                    clearable=False,
                ),

            ], style={'display': 'inline-block'}),

        ], style={'display': 'inline-block', 'margin-left': 600}),
    ]),

    # ASSEMBLER AND PROCESSOR
    html.Div([

        # Assembler
        html.Div([

            html.Div([

                # Textarea for input of assembly code
                dcc.Textarea(id="input1", spellCheck='false', value="input assembly code here",
                             style={'width': 235, 'height': 400, 'display': 'inline-block',
                                    "color": assembly['font'], 'font-size': '15px',
                                    "background-color": assembly['background'],
                                    'font-family': "Roboto Mono, monospace"},
                             autoFocus='true'),

                # Tabs with bin and hex code
                html.Div([
                    dcc.Tabs(id='TABS', value='tabs', children=[
                        dcc.Tab(label='BIN', value='binary'),
                        dcc.Tab(label='HEX', value='hexadecimal'),
                    ], style={'width': 185, 'height': 50}),
                    html.Div(id='tabs-content')
                ], style={'display': 'inline-block'}),

            ]),

            # Button to assemble
            html.Button('ASSEMBLE', id='assemble', n_clicks=0,
                        style={'margin-left': 50, "color": button['font'],
                               "background-color": button['background'],
                               'width': 160})

        ]),

        # Processor
        html.Div([]),

    ]),

    # HIDDEN DIVS
    # Main info (has default settings)
    html.Div(id="info", children='risc3 neumann special', style={'display': 'none'}),
    # Id creation and storage
    html.Div(id='id-storage', style={'display': 'none'}),
    html.Div(id='id-creation', style={'display': 'none'}),
    # Binary and hexadecimal code translations storage
    html.Div(id='code', children=['', ''], style={'display': 'none'}),

])


# APP CALLBACKS
# Change main info
@app.callback(
    Output('info', 'children'),
    [Input('isa-dropdown', 'value'),
     Input('architecture-dropdown', 'value'),
     Input('io-dropdown', 'value')])
def update_output(isa, arch, io):
    """

    """
    return ' '.join([isa, arch, io])


# Create user id
@app.callback(Output('id-storage', 'children'), [Input('id-creation', 'children')])
def get_ip(value):
    """
    Return randomly generated id each time new session starts
    :param value: is not used (is here by default)
    :return: random id
    """
    session_id = str(uuid.uuid4())
    return session_id


# Save binary and hexadecimal code
@app.callback(Output('code', 'children'),
              [Input('assemble', 'n_clicks'),
               Input('info', 'children'),
               Input('id-storage', 'children')],
              [State('input1', 'value')])
def assemble(n_clicks, info, user_id, assembly_code):
    isa, architecture, io = info.split()

    global user_dict
    if user_id not in user_dict:
        user_dict[user_id] = CPU(isa, architecture, io, '')

    if not assembly_code or assembly_code == "input assembly code here":
        binary_program = hex_program = ''
    else:
        try:
            binary_program = Assembler(isa, assembly_code).binary_code
            user_dict[user_id] = CPU(isa, architecture, io, binary_program)
            hex_program = '\n'.join(list(map(lambda x: hex(int(x, 2)), [x for x in binary_program.split('\n') if x])))

        except AssemblerError as err:
            binary_program = hex_program = f'{err.args[0]}'
            user_dict[user_id] = CPU(isa, architecture, io, '')

    return binary_program, hex_program


# Create tabs content (bin and hex)
@app.callback(Output('tabs-content', 'children'),
              [Input('TABS', 'value'),
               Input('code', 'children')])
def render_content_hex_bin(tab, code_lst):
    """

    """
    if tab == 'binary':
        return html.Div([
            dcc.Textarea(value=code_lst[0],
                         style={'width': 185, 'height': 400, "color": assembly['font'], 'font-size': '15px',
                                "background-color": assembly['background'], 'font-family': "Roboto Mono, monospace"},
                         disabled=True)
        ])
    elif tab == 'hexadecimal':
        return html.Div([
            dcc.Textarea(value=code_lst[1],
                         style={'width': 185, 'height': 400, "color": assembly['font'], 'font-size': '15px',
                                "background-color": assembly['background'], 'font-family': "Roboto Mono, monospace"},
                         disabled=True)
        ])
    else:
        return html.Div([
            dcc.Textarea(value=code_lst[0],
                         style={'width': 185, 'height': 400, "color": assembly['font'], 'font-size': '15px',
                                "background-color": assembly['background'], 'font-family': "Roboto Mono, monospace"},
                         disabled=True)
        ])


# CREATE GRAPHIC ELEMENTS OF THE PROCESSOR

# Run the program
if __name__ == '__main__':
    # SERVER LAUNCH
    dev_server = app.run_server
    app.run_server(debug=True, threaded=True)

# TODO: help page,
#  add program examples,
#  cookies to save previous program,
#  edit memory and registers,
#  make next execute till the program is not finished (additional button, user can choose seconds),
#  change memory slots,
#  add new version to server,
#  add bitwise flag,
#  make table undraggable
