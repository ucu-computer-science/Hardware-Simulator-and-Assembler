#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

# Note: 'unused' parameters in callbacks are actually used to triger them

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from bitarray.util import ba2hex, hex2ba, int2ba, ba2int
from bitarray import bitarray
from copy import deepcopy
import uuid
import dash_table
from flask import Flask, render_template, make_response, session
import json
from datetime import datetime
import time

# Imports from the project
from modules.processor import CPU
from modules.assembler import Assembler, AssemblerError
from website.color_palette_and_layout import table_header, table, button, assembly, background_color, title_color, \
    text_color, not_working, style_header, style_cell, tab_style, tab_selected_style, \
    dropdown_style1, dropdown_style2, table_main_color, table_main_font_color, table_header_color, help_color, \
    help_font_color, style_memory_header, memory_font, memory_tab_style, memory_selected_tab_style, \
    memory_selected_tab_style2
from website.example_programs import examples

# CPU DICTIONARY ( key=user.id, value=dict(cpu, intervals) )
user_dict = dict()
# Numbers of buttons (used to change type of isa during cpu creation, are same for every session and user)
buttons = {0: 'risc1', 1: 'risc2', 2: 'risc3', 3: 'cisc'}
isas = {'risc1': 0, 'risc2': 1, 'risc3': 2, 'cisc': 3}
# Empty memoty cells
base_headers = ['Addr   :  ', '00 01 02 03', '04 05 06 07', '08 09 0a 0b', '0c 0d 0e 0f', '10 11 12 13', '14 15 16 17',
                '18 19 1a 1b', '1c 1d 1e 1f']
indexes = []
for i in range(0, 1024, 32):
    indexes.append(hex(i)[2:].rjust(8, "0"))
base_data = []
for x in range(32):
    base_data.append(dict())
    for y in range(9):
        if y == 0:
            base_data[x][base_headers[y]] = indexes[x]
        else:
            base_data[x][base_headers[y]] = '00 00 00 00'

empty_memory = dash_table.DataTable(id='mem', columns=([{'id': i, 'name': i} for i in base_headers]),
                                    data=base_data,
                                    style_header=style_memory_header,
                                    style_cell=style_cell,
                                    style_cell_conditional=[
                                        {
                                            'if': {'column_id': base_headers[0]},
                                            'color': memory_font
                                        }
                                    ],
                                    fixed_rows={'headers': True},
                                    style_table={'height': '300px', 'overflowY': 'auto'},
                                    editable=True
                                    )

# Create app
server = Flask(__name__)
# Actually different on server
server.secret_key = b'_5#y2L"F4Q8'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'url(assets/reset.css)']
app = dash.Dash(name=__name__, server=server, external_stylesheets=external_stylesheets, routes_pathname_prefix='/')
app.title = "ASSEMBLY SIMULATOR"

# MAIN LAYOUT
app.layout = html.Div([

    # "MAIN MENU"
    html.Div([
        # Title
        dcc.Markdown("ASSEMBLY SIMULATOR",
                     style={'color': title_color,
                            'font-size': '25px', 'display': 'inline-block', 'margin-left': 100, 'margin-top': 5}),

        dcc.Markdown("CHOOSE AN EXAMPLE PROGRAM:",
                     style={'color': text_color,
                            'font-size': '18px', 'display': 'inline-block', 'margin-left': 153}),
        dcc.Markdown("CHOOSE ISA:",
                     style={'color': text_color,
                            'font-size': '18px', 'display': 'inline-block', 'margin-left': 75}),

        dcc.Markdown("ARCHITECTURE:",
                     style={'color': text_color,
                            'font-size': '18px', 'display': 'inline-block', 'margin-left': 60}),

        dcc.Markdown("I/O MODE:",
                     style={'color': text_color,
                            'font-size': '18px', 'display': 'inline-block', 'margin-left': 100}),

        # Dropdowns for examples, isa, architecture and i/o mode
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='example-dropdown',
                    options=[
                        {'label': 'ALPHABET PRINTOUT', 'value': 'alphabet'},
                        {'label': 'HELLO WORLD', 'value': 'hello'},
                        {'label': 'BUBBLE SORT', 'value': 'bubble_sort'},
                        {'label': 'POLYNOMIAL CALCULATION', 'value': 'polynomial', 'disabled':True},
                        {'label': 'NONE', 'value': 'none'},
                    ],
                    placeholder="NONE",
                    style=dropdown_style2,
                    clearable=False
                ),

            ], style={'display': 'inline-block'}),

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
                    style=dropdown_style1,
                    clearable=False,
                ),
            ], style={'display': 'inline-block'}),

            html.Div([

                dcc.Dropdown(
                    id='architecture-dropdown',
                    options=[
                        {'label': 'VON NEUMANN', 'value': 'neumann'},
                        {'label': 'HARVARD', 'value': 'harvard'},
                    ],
                    value='neumann',
                    style=dropdown_style1,
                    clearable=False,
                ),

            ], style={'display': 'inline-block'}),

            html.Div([

                dcc.Dropdown(
                    id='io-dropdown',
                    options=[
                        {'label': 'MEMORY-MAPPED', 'value': 'mmio'},
                        {'label': 'SPECIAL COMMANDS', 'value': 'special'},
                    ],
                    value='special',
                    style=dropdown_style1,
                    clearable=False,
                ),

            ], style={'display': 'inline-block'}),

        ], style={'display': 'inline-block', 'margin-left': 525}),
    ], style={'margin-bottom': 15}),

    # ASSEMBLER AND PROCESSOR
    html.Div([

        # Assembler
        html.Div([

            html.Div([

                # Textarea for input of assembly code
                html.Div([
                    dcc.Markdown("ASSEMBLY CODE:",
                                 style={'color': text_color,
                                        'font-size': '18px', 'margin-left': 60}),
                    dcc.Textarea(id="input1", spellCheck='false',
                                 value="loading...",
                                 style={'width': 235, 'height': 400,
                                        "color": assembly['font'], 'font-size': '15px',
                                        "background-color": assembly['background'], 'margin-left': 20},
                                 autoFocus='true'),

                ], style={'display': 'inline-block', }),

                # Tabs with bin and hex code
                html.Div([
                    dcc.Tabs(id='TABS', value='binary', children=[
                        dcc.Tab(label='BIN:', value='binary', style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='HEX:', value='hexadecimal', style=tab_style, selected_style=tab_selected_style),
                    ], style={'width': 190, 'height': 58}),
                    html.Div(id='tabs-content')
                ], style={'display': 'inline-block', 'margin-left': 10}),

            ]),

            html.Div([
                html.Div([dash_table.DataTable(id='initial-ip',
                                               columns=([{'id': '1', 'name': 'INITIAL IP'}]),
                                               data=([{'1': '0200'}]),
                                               style_header=style_header,
                                               style_cell=style_cell,
                                               editable=True), ],
                         style={'display': 'block', 'width': 100, 'margin-left': 85}),
                # Button to assemble
                html.Button('ASSEMBLE', id='assemble', n_clicks=0,
                            style={'margin-left': 280, 'margin-top': -40, "color": button['font'],
                                   'font-family': 'custom',
                                   "background-color": button['background'],
                                   'width': 160, 'display': 'block',
                                   'font-size': 13}),

            ]),

        ], style={'display': 'inline-block'}),

        # Processor
        html.Div(className='row', children=[

            html.Div([

                # Next instruction
                html.Div(id='instruction', style={'display': 'inline-block', 'margin-right': 10
                                                  }),

                # Output, registers and flags
                html.Div([

                    html.Div(id='output',
                             children=dash_table.DataTable(id='in_out', columns=([{'id': '1', 'name': 'OUTPUT'}]),
                                                           data=([{'1': ''}]),
                                                           style_header=style_header,
                                                           style_cell=style_cell,
                                                           style_table={'width': '150px'}),
                             style={'display': 'inline-block', 'margin-right': 10}),

                    # Registers
                    html.Div(html.Div(id='registers', children=dash_table.DataTable(id='registers-table',
                                                                                    columns=(
                                                                                        [{'id': ['SP:', 'IP:', 'LR:',
                                                                                                 'FR:', 'R00:',
                                                                                                 'R01:', 'R02:',
                                                                                                 'R03:'][i],
                                                                                          'name':
                                                                                              ['SP', 'IP', 'LR',
                                                                                               'FR', 'R00', 'R01',
                                                                                               'R02', 'R03'][
                                                                                                  i] + ': '} for i
                                                                                         in
                                                                                         range(4)]),
                                                                                    data=([{['SP:', 'IP:', 'LR:',
                                                                                             'FR:', 'R00:',
                                                                                             'R01:', 'R02:',
                                                                                             'R03:'][i]: '0000' for i in
                                                                                            range(4)}]),
                                                                                    style_header=style_header,
                                                                                    style_cell=style_cell,
                                                                                    editable=True,
                                                                                    ), ),
                             style={'display': 'inline-block', 'margin-right': 10}),

                    html.Div(id='flags', children=dash_table.DataTable(id='flags-table',
                                                                       columns=([{'id': ['CF', 'ZF', 'OF', 'SF'][i],
                                                                                  'name': ['CF', 'ZF', 'OF', 'SF'][
                                                                                              i] + ': '} for i in
                                                                                 range(4)]),
                                                                       data=([{['CF', 'ZF', 'OF', 'SF'][i]: '0' for i in
                                                                               range(4)}]),
                                                                       style_header=style_header,
                                                                       style_cell=style_cell, ),
                             style={'display': 'inline-block', 'margin-right': 10}),

                    html.Div
                        ([

                        dash_table.DataTable(id='seconds',
                                             columns=([{'id': '1', 'name': 'INST/SEC (max1)'}]),
                                             data=([{'1': '1'}]),
                                             style_header=style_header,
                                             style_cell=style_cell,
                                             editable=True),

                    ],
                        style={'display': 'inline-block'}),

                ], style={'display': 'inline-block'}),

            ]),

            # Memory
            html.Div(id='memory-div', children=[dcc.Tabs(id='memory-tabs', value='data_memory', children=[
                dcc.Tab(label='PROGRAM AND DATA MEMORY', id='data-memory-tab', value='data_memory',
                        style=memory_tab_style,
                        selected_style=memory_selected_tab_style2),
            ], style={'height': 25}), html.Div(id='memory', children=empty_memory)],
                     style={'margin-bottom': 20, 'margin-top': 20}),

            # Buttons
            html.Div([html.Button('NEXT INSTRUCTION', id='next', n_clicks=0,
                                  style={"color": button['font'], 'font-family': 'custom',
                                         "background-color": button['background'],
                                         'width': 200, 'display': 'inline-block', 'font-size': 13, 'margin-right': 17}),

                      html.Div(id='run-until-finished-button',
                               children=html.Button('RUN', id='run-until-finished', n_clicks=0,
                                                    style={"color": button['font'], 'font-family': 'custom',
                                                           "background-color": button['background'],
                                                           'width': 200,
                                                           'font-size': 13}), style={'display': 'inline-block'}),
                      html.Button('RESET COMPUTER', id='reset', n_clicks=0,
                                  style={"color": button['font'], 'font-family': 'custom', 'width': 150,
                                         "background-color": button['background'], 'display': 'inline-block',
                                         'font-size': 13,
                                         'margin-left': 255}),
                      ],
                     style={'display': 'block'}),

        ], style={'display': 'inline-block', 'margin-left': 70}),

    ]),

    # Link to a help page and license name (someday github link)
    html.Div([dcc.Link(html.Button('INSTRUCTION SET (HELP)', style={"color": help_font_color, 'font-family': 'custom',
                                                                    "background-color": help_color,
                                                                    'margin-bottom': 15,
                                                                    'font-size': 13}), id='link', href='/help-risc3',
                       refresh=True,
                       style={'color': text_color, 'display': 'block', 'width': 260}),
              dcc.Link(children=["GitHub Repository"], href='https://github.com/dariaomelkina/poc_project',
                       refresh=True,
                       style={'color': text_color, 'display': 'block',
                              'margin-left': 1238, 'margin-top': -35})],
             style={'margin-left': 14, 'margin-top': 40, 'display': 'block'}),

    # Additional info (is one of the last in order not to override anything)
    dcc.Markdown(
        "Hardware Simulator with its own Assembly language (check the help page below), with support for several architectures",
        style={'color': text_color,
               'font-size': '13px', 'display': 'block', 'margin-left': 62, 'margin-top': -670, 'width': 350,
               'text-align': 'center'}),

    # HIDDEN DIVS

    # Main info (has default settings)
    html.Div(id="info", children='risc3 neumann special', style={'display': 'none'}),
    # Id creation and storage
    html.Div(id='id-storage', style={'display': 'none'}),
    html.Div(id='id-creation', style={'display': 'none'}),

    # Input code storage (mostly for coookies)
    html.Div(id='input-code', children='', style={'display': 'none'}),

    # Binary and hexadecimal code translations storage
    html.Div(id='code', children=['', ''], style={'display': 'none'}),

    # Instruction storage
    html.Div(id='instruction-storage', children='0' * 16, style={'display': 'none'}),
    # Memory storage (in a list, because Harvard architecture has two separate memories)
    html.Div(id='memory-storage', children=['\n'.join(['\t'.join(['00 00 00 00'] * 32)] * 8), ''],
             style={'display': 'none'}),
    # Registers storage (first element –– registers, second –– their values )
    html.Div(id='registers-storage',
             children=[' '.join(['SP', 'IP', 'LR', 'FR', 'R00', 'R01', 'R02', 'R03']), ' '.join(['0000'] * 8)],
             style={'display': 'none'}),
    # Flags storage
    html.Div(id='flags-storage', children=['0'] * 4, style={'display': 'none'}),
    # Output storage
    html.Div(id='output-storage', children='', style={'display': 'none'}),

    # Storage for reaction on 'next instruction' button
    html.Div(id='next-storage', children='0', style={'display': 'none'}),
    # Storage for reaction on 'run until finished' button
    html.Div(id='run-storage', children=dcc.Interval(id='interval', interval=1 * 1000, n_intervals=0, disabled=True),
             style={'display': 'none'}),

    # Storage to hold seconds for instruction per second
    html.Div(id='seconds-storage', children=1, style={'display': 'none'}),

    # Example storage (for risc3 by default)
    html.Div(id='examples', children=examples['risc3'], style={'display': 'none'}),

    # Instruction pointer storage (for risc3 by default)
    html.Div(id='ip-storage', children=512, style={'display': 'none'}),

    # Div to enable input mode
    html.Div(id='store-io', style={'display': 'none'}),

    # Divs for storing changes in reset
    html.Div(id='reset-storage', children=0, style={'display': 'none'}),
    html.Div(id='reset-storage-code', children=0, style={'display': 'none'}),

    # Placeholders to enable manual changes
    html.Div(id='registers-placeholder', style={'display': 'none'}),
    html.Div(id='flags-placeholder', style={'display': 'none'}),
    html.Div(id='memory-placeholder', style={'display': 'none'}),

], id="wrapper", )


# APP CALLBACKS FOR INPUT/OUTPUT OF THE INFORMATION, ASSEMBLER

# Create user id
@app.callback(Output('id-storage', 'children'),
              [Input('id-creation', 'children')])
def get_id(value):
    """
    Return randomly generated id each time new session starts.

    :param value: is not used (is here by default)
    :return: random id
    """
    if 'user_id' in session:
        user_id = session['user_id']
    else:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
    return user_id


# Save binary and hexadecimal code
@app.callback([Output('code', 'children'),
               Output('next', 'n_clicks')],
              [Input('assemble', 'n_clicks'),
               Input('id-storage', 'children'),
               Input('reset-storage', 'children')],
              [State('info', 'children'),
               State('input1', 'value'),
               State('ip-storage', 'children'),
               State('next', 'n_clicks')])
def assemble(n_clicks, user_id, reset_clicks, info, assembly_code, ip, next_clicks):
    """
    Create cpu instance, translate input assembly code to binary and hexadecimal ones.
    Creates new empty cpu when reset is pressed, loads same cpu when page is refreshed.

    :param n_clicks: is not used (is here by default)
    :param user_id: id of the session/user
    :param reset_clicks: n_clicks of 'reset' button
    :param info: isa, architecture and I/O mode
    :param assembly_code: input assembly code
    :param ip: instruction pointer for cpu creation
    :param next_clicks: n_clicks of 'next' button
    :return: binary and hexadecimal codes or assembler error in a list, next_clicks + 1
    """
    isa, architecture, io = info.split()
    global user_dict

    if not n_clicks and user_id in user_dict:

        if reset_clicks > user_dict[user_id]['reset']:
            user_dict[user_id] = dict()
            user_dict[user_id]['cpu'] = CPU(isa, architecture, io, '')
            user_dict[user_id]['code'] = ''
            user_dict[user_id]['binhex'] = ['', '']
            user_dict[user_id]['flags-changed'] = False
            user_dict[user_id]['intervals'] = 0
            user_dict[user_id]['reset'] = reset_clicks
            user_dict[user_id]['reset-code'] = 0
            assembly_code = "input assembly code here"

            user_dict[user_id]['next-registers'] = 0
            user_dict[user_id]['next-flags'] = 0
            user_dict[user_id]['next-memory'] = 0
            user_dict[user_id]['completed-changes'] = ['1', '1', '1', '1', '1']
            user_dict[user_id]['manual-changes'] = ['1', '1', '1']
            user_dict[user_id]['time'] = 1
            user_dict[user_id]['example'] = 'none'

            next_clicks = 0
        else:
            user_dict[user_id]['reset'] = reset_clicks
            user_dict[user_id]['reset-code'] = reset_clicks

            user_dict[user_id]['next-registers'] = 0
            user_dict[user_id]['next-flags'] = 0
            user_dict[user_id]['next-memory'] = 0
            user_dict[user_id]['completed-changes'] = ['1', '1', '1', '1', '1']
            user_dict[user_id]['manual-changes'] = ['1', '1', '1']
            user_dict[user_id]['time'] = 1



    elif n_clicks:

        if user_id not in user_dict:
            user_dict[user_id] = dict()
            user_dict[user_id]['cpu'] = CPU(isa, architecture, io, '')
            user_dict[user_id]['code'] = ''
            user_dict[user_id]['binhex'] = ['', '']
            user_dict[user_id]['flags-changed'] = False
            user_dict[user_id]['intervals'] = 0
            user_dict[user_id]['reset'] = reset_clicks
            user_dict[user_id]['reset-code'] = reset_clicks

            user_dict[user_id]['next-registers'] = 0
            user_dict[user_id]['next-flags'] = 0
            user_dict[user_id]['next-memory'] = 0
            user_dict[user_id]['completed-changes'] = ['1', '1', '1', '1', '1']
            user_dict[user_id]['manual-changes'] = ['1', '1', '1']
            user_dict[user_id]['time'] = 1
            user_dict[user_id]['example'] = 'none'

        elif reset_clicks > user_dict[user_id]['reset']:
            user_dict[user_id] = dict()
            user_dict[user_id]['cpu'] = CPU(isa, architecture, io, '')
            user_dict[user_id]['code'] = ''
            user_dict[user_id]['binhex'] = ['', '']
            user_dict[user_id]['flags-changed'] = False
            user_dict[user_id]['intervals'] = 0
            user_dict[user_id]['reset'] = reset_clicks
            user_dict[user_id]['reset-code'] = 0
            assembly_code = "input assembly code here"

            user_dict[user_id]['next-registers'] = 0
            user_dict[user_id]['next-flags'] = 0
            user_dict[user_id]['next-memory'] = 0
            user_dict[user_id]['completed-changes'] = ['1', '1', '1', '1', '1']
            user_dict[user_id]['manual-changes'] = ['1', '1', '1']
            user_dict[user_id]['time'] = 1
            user_dict[user_id]['example'] = 'none'

            next_clicks = 0

        if not assembly_code or assembly_code in ["input assembly code here", "loading...", '']:
            binary_program = hex_program = ''
            if not user_dict[user_id]['code']:
                user_dict[user_id]['cpu'] = CPU(isa, architecture, io, binary_program, ip)
                user_dict[user_id]['code'] = assembly_code
                user_dict[user_id]['binhex'] = [binary_program, hex_program]
        else:
            with open('website/history.txt', 'a') as file:
                file.write(str(datetime.now()) + '\n')
                if assembly_code not in examples[isa]:
                    file.write(assembly_code)
                else:
                    if assembly_code == examples[isa][0]:
                        file.write(f'Example: Alphabet for {isa}.')
                    else:
                        file.write(f'Example: Hello World for {isa}.')
                file.write('\n\n============================================\n\n')

            try:
                binary_program = Assembler(isa, assembly_code).binary_code
                user_dict[user_id]['cpu'] = CPU(isa, architecture, io, binary_program, ip)
                hex_program = '\n'.join(
                    list(map(lambda x: hex(int(x, 2))[2:], [x for x in binary_program.split('\n') if x])))

            except AssemblerError as err:
                binary_program = hex_program = f'{err.args[0]}'
                user_dict[user_id]['cpu'] = CPU(isa, architecture, io, '', ip)
            user_dict[user_id]['code'] = assembly_code
            user_dict[user_id]['binhex'] = [binary_program, hex_program]

        return [binary_program, hex_program], next_clicks + 1
    return ['', ''], next_clicks + 1


# Make sure, that after refreshing the page, dropdowns values stay the same and
# enable only Harvard architecture for stack
@app.callback([Output('architecture-dropdown', 'options'),
               Output('architecture-dropdown', 'value'),
               Output('io-dropdown', 'value')],
              [Input('isa-dropdown', 'value')],
              [State('info', 'children')])
def control_architecture(chosen_isa, info):
    """
    Control architecture and io dropdowns.
    Return same ones when refreshing the page, enable only Harvard architecture for Stack ISA.

    :param chosen_isa: current value of isa dropdown
    :param info: isa, architecture and I/O mode
    :return: lables for architecture dropdown, availabe/chosen architecture, chosen I/O
    """
    isa, arch, io = info.split()
    isa = chosen_isa
    if isa == 'risc1':
        return [{'label': 'VON NEUMANN', 'value': 'neumann', 'disabled': True},
                {'label': 'HARVARD', 'value': 'harvard'}, ], 'harvard', io
    else:
        return [{'label': 'VON NEUMANN', 'value': 'neumann'}, {'label': 'HARVARD', 'value': 'harvard'}, ], arch, io


@app.callback(Output('isa-dropdown', 'value'),
              [Input('id-storage', 'children')],
              [State('info', 'children')])
def control_isa(user_id, current_info):
    """
    Control ISA dropdown (return same one when refreshing the page).

    :param user_id: id of the session/user
    :param current_info: isa, architecture and I/O mode
    :return: isa
    """
    if user_id in user_dict:
        return user_dict[user_id]['cpu'].isa
    return current_info.split()[0]


# If computer is reset get rid of example
@app.callback(Output('example-dropdown', 'value'),
              [Input('reset-storage', 'children')],
              [State('id-storage', 'children')])
def update_examples(n_clicks, user_id):
    """
    Control example dropdown in case of reset.

    :param n_clicks: n_clicks of 'reset' button (processed in additional div)
    :param user_id: id of the session/user
    :return: example dropdown value
    """
    if user_id in user_dict:
        return user_dict[user_id]['example']
    return 'none'


# Change main info
@app.callback(
    Output('info', 'children'),
    [Input('isa-dropdown', 'value'),
     Input('architecture-dropdown', 'value'),
     Input('io-dropdown', 'value'),
     Input('id-storage', 'children')])
def update_output(isa, arch, io, user_id):
    """
    Update main information about the cpu,
    depending on the choice from dropdowns.

    :param isa: chosen isa
    :param arch: chosen architecture
    :param io: chosen I/O mode
    :param user_id: id of the session/user
    :return: string with information
    """
    return ' '.join([isa, arch, io])


# Reset the computer if info changes
@app.callback(
    Output('reset', 'n_clicks'),
    [Input('info', 'children')],
    [State('reset', 'n_clicks')])
def reset_computer(info, n_clicks):
    """
    Trigger reset button, if main info changes.

    :param info: isa, architecture and I/O mode
    :param n_clicks: n_clicks of 'reset' button
    :return: new n_clicks
    """
    return n_clicks + 1


# Create tabs content (bin and hex)
@app.callback(Output('tabs-content', 'children'),
              [Input('TABS', 'value'),
               Input('code', 'children'),
               Input('id-storage', 'children')])
def render_content_hex_bin(tab, code_lst, user_id):
    """
    Render two tabs: with binary and with hexadecimal code translations (and intional one, binary too).

    :param tab: one of two: binary or hexadecimal
    :param user_id: id of the session/user
    :param code_lst: list with binary and with hexadecimal code translations
    :return: tabs
    """
    if user_id in user_dict:
        code_lst = user_dict[user_id]['binhex']
    if tab == 'binary':
        return html.Div([
            dcc.Textarea(id='bin_hex', value=code_lst[0],
                         style={'width': 190, 'height': 400, "color": table['font'], 'font-size': '15px',
                                "background-color": table['background']},
                         disabled=True)
        ])
    elif tab == 'hexadecimal':
        return html.Div([
            dcc.Textarea(id='bin_hex', value=code_lst[1],
                         style={'text-align': 'right', 'width': 190, 'height': 400, "color": table['font'],
                                'font-size': '15px',
                                "background-color": table['background']},
                         disabled=True)
        ])
    else:
        return html.Div([
            dcc.Textarea(id='bin_hex', value=code_lst[0],
                         style={'width': 190, 'height': 400, "color": table['font'], 'font-size': '15px',
                                "background-color": table['background']},
                         disabled=True)
        ])


# Update div with examples
@app.callback(
    Output('examples', 'children'),
    [Input('isa-dropdown', 'value')])
def update_examples(isa):
    """
    Return code examples for the current isa.

    :param isa: isa dropdown value
    :return: list with examples
    """
    return examples[isa]


# Add current code to the textarea
@app.callback(
    Output('input1', 'value'),
    [Input('input-code', 'children')])
def code(input_code):
    """
    Add initial or example code to the textarea.

    :param input_code: code saved in a div
    :return: input_code
    """
    return input_code


# Add a chosen example to the textarea
@app.callback(
    Output('input-code', 'children'),
    [Input('example-dropdown', 'value'),
     Input('examples', 'children'),
     Input('reset-storage-code', 'children')],
    [State('id-storage', 'children')])
def add_example_code(example_name, app_examples, reset_clicks, user_id):
    """
    Control code storage: return examples, loading state, input pointer
    or code, assembled before page refreshing.

    :param example_name: chosen example name
    :param app_examples: available list with examples
    :param reset_clicks: n_clicks of 'reset' button
    :param user_id: id of the session/user
    :return: code
    """
    if user_id in user_dict:
        if reset_clicks > user_dict[user_id]['reset-code']:
            user_dict[user_id]['reset-code'] = reset_clicks
            return "input assembly code here"
    if example_name == 'alphabet':
        if user_id in user_dict:
            user_dict[user_id]['example'] = 'alphabet'
        return app_examples[0]
    elif example_name == 'hello':
        if user_id in user_dict:
            user_dict[user_id]['example'] = 'hello'
        return app_examples[1]
    elif example_name == 'bubble_sort':
        if user_id in user_dict:
            user_dict[user_id]['example'] = 'bubble_sort'
        return app_examples[2]
    elif example_name == 'polynomial':
        if user_id in user_dict:
            user_dict[user_id]['example'] = 'polynomial'
        return app_examples[3]
    if user_id in user_dict:
        user_dict[user_id]['example'] = 'none'
        if user_dict[user_id]['code']:
            return user_dict[user_id]['code']
        else:
            return "input assembly code here"
    else:
        return "input assembly code here"


# APP CALLBACKS FOR CREATION OF GRAPHIC ELEMENTS OF THE PROCESSOR
@app.callback(Output('instruction', 'children'),
              [Input('instruction-storage', 'children')],
              [State('id-storage', 'children')])
def create_instruction(value, user_id):
    """
    Return a table with current binary instruction and its assembly mnemonic.

    :param value: current instruction in the div
    :param user_id: id of the session/user
    :return: dash table
    """
    if user_id in user_dict:
        user_dict[user_id]['completed-changes'][0] = '1'
        return dash_table.DataTable(columns=([{'id': '1', 'name': 'NEXT INSTRUCTION'}]),
                                    data=([{
                                        '1': f'{value} ({user_dict[user_id]["cpu"].instructions_dict[user_dict[user_id]["cpu"].opcode.to01()][0]})'}]),
                                    style_header=style_header,
                                    style_cell=style_cell, style_table={'width': 200})
    return dash_table.DataTable(columns=([{'id': '1', 'name': 'NEXT INSTRUCTION'}]),
                                data=([{'1': value}]),
                                style_header=style_header,
                                style_cell=style_cell, style_table={'width': 200})


@app.callback(Output('registers', 'children'),
              [Input('registers-storage', 'children')],
              [State('id-storage', 'children')])
def create_registers(value, user_id):
    """
    Return a table with current registers and their values.

    :param value: current registers in the div
    :param user_id: id of the session/user
    :return: dash table
    """
    regs = []
    values = []
    for i in value:
        regs.append(i.split(' ')[0])
        values.append(i.split(' ')[1])
    if user_id in user_dict:
        user_dict[user_id]['completed-changes'][1] = '1'
    return html.Div(dash_table.DataTable(id='registers-table',
                                         columns=([{'id': regs[i], 'name': regs[i]} for i in range(len(regs))]),
                                         data=([{regs[i]: values[i] for i in range(len(regs))}]),
                                         style_header=style_header,
                                         style_cell={'backgroundColor': table_main_color,
                                                     'color': table_main_font_color, 'textAlign': 'center',
                                                     'border': f'1px {table_header_color}', 'font-size': 12,
                                                     'minWidth': 33.5},
                                         editable=True
                                         ))


@app.callback(Output('flags', 'children'),
              [Input('flags-storage', 'children')],
              [State('id-storage', 'children')])
def create_flags(value, user_id):
    """
    Return a table with flags and their values.

    :param value: current flags in the div
    :param user_id: id of the session/user
    :return: dash table
    """
    flags = ['CF', 'ZF', 'OF', 'SF']
    if user_id in user_dict:
        user_dict[user_id]['completed-changes'][2] = '1'
    return dash_table.DataTable(id='flags-table',
                                columns=([{'id': flags[i], 'name': flags[i] + ': '} for i in range(len(flags))]),
                                data=([{flags[i]: value[i] for i in range(len(flags))}]),
                                style_header=style_header,
                                style_cell=style_cell,
                                editable=True)


@app.callback(Output('output', 'children'),
              [Input('output-storage', 'children'),
               Input('next', 'n_clicks')],
              [State('id-storage', 'children')])
def create_output(value, n_clicks, user_id):
    """
    Return a table with current cpu output/Activate input mode and read user input.

    :param value: current output in the div
    :param n_clicks:n_clicks of 'next' button
    :param user_id: id of the session/user
    :return: dash table (in input case: editable dash table)
    """
    if user_id in user_dict:
        if user_dict[user_id]['cpu'].is_input_active:
            user_dict[user_id]['completed-changes'][3] = '1'
            return dash_table.DataTable(id='in_out', columns=([{'id': '1', 'name': 'INPUT'}]),
                                        data=([{'1': ''}]),
                                        style_header=style_header,
                                        style_cell=style_cell,
                                        style_table={'width': '150px'}, editable=True)
        else:
            user_dict[user_id]['completed-changes'][3] = '1'

    return dash_table.DataTable(id='in_out', columns=([{'id': '1', 'name': 'OUTPUT'}]),
                                data=([{'1': value}]),
                                style_header=style_header,
                                style_cell=style_cell,
                                style_table={'width': '150px'})


@app.callback(Output('store-io', 'children'),
              [Input('in_out', 'data')],
              [State('in_out', 'editable'),
               State('id-storage', 'children')])
def get_io(data, editable, user_id):
    """
    Read input data and store it in the cpu.

    :param data: data from the tables
    :param editable: bool
    :param user_id: id of the session/user
    :return: input char
    """
    if editable:
        char = data[0]['1']
        if char:
            if len(char) != 0:
                user_dict[user_id]['cpu'].input_finish(bin(ord(char[0]))[2:])
        return char


@app.callback(Output('memory-div', 'children'),
              [Input('next', 'n_clicks')],
              [State('info', 'children')])
def change_memory_tabs(n_clicks, info):
    """
    Return memory according;y to a chosen architecture.

    :param n_clicks: n_clicks of 'next' button
    :param info: isa, architecture and I/O mode
    """
    arch = info.split()[1]
    if arch == 'neumann':
        return [dcc.Tabs(id='memory-tabs', value='data_memory', children=[
            dcc.Tab(label='PROGRAM AND DATA MEMORY', id='data-memory-tab', value='data_memory', style=memory_tab_style,
                    selected_style=memory_selected_tab_style2),
        ], style={'height': 25}), html.Div(id='memory', children=empty_memory)]
    else:
        return [dcc.Tabs(id='memory-tabs', value='data_memory', children=[
            dcc.Tab(label='DATA MEMORY:', id='data-memory-tab', value='data_memory', style=memory_tab_style,
                    selected_style=memory_selected_tab_style),
            dcc.Tab(label='PROGRAM MEMORY:', id='program-memory-tab', value='program_memory',
                    style=memory_tab_style,
                    selected_style=memory_selected_tab_style, disabled_style=memory_tab_style)
        ], style={'height': 25}), html.Div(id='memory', children=empty_memory)]


@app.callback(Output('memory', 'children'),
              [Input('memory-tabs', 'value'),
               Input('memory-storage', 'children')],
              [State('id-storage', 'children')])
def create_memory(tab, value, user_id):
    """
    Create a table with memory of the cpu.

    :param tab: chosen tab
    :param value: current memory in the div
    :param user_id: id of the session/user
    :return: dash table
    """
    if tab == 'data_memory':
        headers = ["Addr   :  "]
        for i in range(0, 32, 4):
            headers.append(f"{hex(i)[2:].rjust(2, '0')} {hex(i + 1)[2:].rjust(2, '0')} "
                           f"{hex(i + 2)[2:].rjust(2, '0')} {hex(i + 3)[2:].rjust(2, '0')}")

        rows = []
        for i in range(0, 1024, 32):
            rows.append(hex(i)[2:].rjust(8, "0"))

        temp_lst1 = value[0].split('\n')
        memory_data = []
        for i in temp_lst1:
            memory_data.append(i.split('\t'))

        rows = [rows] + memory_data

        data_lst = []
        for y in range(len(rows[0])):
            data_lst.append([])
            for x in range(len(rows)):
                data_lst[y].append(rows[x][y])

        # Create a list of dictionaries (key -- column name)
        data = []
        for x in range(len(rows[0])):
            data.append(dict())
            for y in range(len(rows)):
                data[x][headers[y]] = data_lst[x][y]
        if user_id in user_dict:
            user_dict[user_id]['completed-changes'][4] = '1'
        return dash_table.DataTable(id='mem', columns=([{'id': i, 'name': i} for i in headers]),
                                    data=data,
                                    style_header=style_memory_header,
                                    style_cell=style_cell,
                                    style_cell_conditional=[
                                        {
                                            'if': {'column_id': headers[0]},
                                            'color': memory_font
                                        }
                                    ],
                                    fixed_rows={'headers': True},
                                    style_table={'height': '300px', 'overflowY': 'auto'},
                                    editable=True
                                    )
    else:
        headers = ["Addr   :  "]
        for i in range(0, 32, 4):
            headers.append(f"{hex(i)[2:].rjust(2, '0')} {hex(i + 1)[2:].rjust(2, '0')} "
                           f"{hex(i + 2)[2:].rjust(2, '0')} {hex(i + 3)[2:].rjust(2, '0')}")

        rows = []
        for i in range(0, 1024, 32):
            rows.append(hex(i)[2:].rjust(8, "0"))

        temp_lst1 = value[1].split('\n')
        memory_data = []
        for i in temp_lst1:
            memory_data.append(i.split('\t'))

        rows = [rows] + memory_data

        data_lst = []
        for y in range(len(rows[0])):
            data_lst.append([])
            for x in range(len(rows)):
                data_lst[y].append(rows[x][y])

        # Create a list of dictionaries (key -- column name)
        data = []
        for x in range(len(rows[0])):
            data.append(dict())
            for y in range(len(rows)):
                data[x][headers[y]] = data_lst[x][y]
        if user_id in user_dict:
            user_dict[user_id]['completed-changes'][4] = '1'
        return dash_table.DataTable(id='mem', columns=([{'id': i, 'name': i} for i in headers]),
                                    data=data,
                                    style_header=style_memory_header,
                                    style_cell=style_cell,
                                    style_cell_conditional=[
                                        {
                                            'if': {'column_id': headers[0]},
                                            'color': memory_font
                                        }
                                    ],
                                    fixed_rows={'headers': True},
                                    style_table={'height': '300px', 'overflowY': 'auto'},
                                    editable=True
                                    )


# UPDATE HIDDEN INFO FOR PROCESSOR
@app.callback(Output('next-storage', 'children'),
              [Input('next', 'n_clicks'),
               Input('id-storage', 'children'),
               Input('interval', 'n_intervals'),
               Input('reset', 'n_clicks')],
              [State('next-storage', 'children')])
def update_next(n_clicks, user_id, interval, reset, current_situation):
    """
    Return n_clicks for the 'next instruction' button,
    so it changes hidden div, on which graphic elements of
    the processor will react.
    Executes next instruction in the cpu if page was completly reloaded after previous execution.

    :param n_clicks: n_clicks for the 'next instruction' button
    :param user_id: id of the session/user
    :param interval: intervals (in case of pressing 'run' button)
    :param reset:  n_clicks of 'reset' button
    :param current_situation: current children of next storage
    :return: same n_clicks/interval
    """
    if user_id in user_dict:
        if not user_dict[user_id]['cpu'].is_input_active:

            if (interval > 0 and user_dict[user_id]['completed-changes'] == ['1', '1', '1', '1', '1']) or interval == 1:
                user_dict[user_id]['cpu'].web_next_instruction()
                if user_dict[user_id]['cpu'].instruction.to01() != '0' * len(
                        user_dict[user_id]['cpu'].instruction.to01()):
                    user_dict[user_id]['completed-changes'] = ['0', '0', '0', '0', '0']
                    user_dict[user_id]['manual-changes'] = ['0', '0', '0']
                return interval

            if (n_clicks > 0 and user_dict[user_id]['completed-changes'] == ['1', '1', '1', '1', '1'] and \
                user_dict[user_id]['manual-changes'] == ['1', '1', '1']) or n_clicks == 1:
                user_dict[user_id]['cpu'].web_next_instruction()
                if user_dict[user_id]['cpu'].instruction.to01() != '0' * len(
                        user_dict[user_id]['cpu'].instruction.to01()):
                    user_dict[user_id]['completed-changes'] = ['0', '0', '0', '0', '0']
                    user_dict[user_id]['manual-changes'] = ['0', '0', '0']
                return n_clicks
    else:
        return current_situation


# Work with intervals
@app.callback(
    Output("interval", "disabled"),
    [Input("run-until-finished", "n_clicks"),
     Input('id-storage', 'children'),
     Input("instruction-storage", "children")],
    [State("interval", "disabled")]
)
def run_interval(n, user_id, instruction, current_state):
    """
    If the 'run' button is triggered, launch interval, which
    will execute instructions one by one.
    Stop interval if the 'stop' button is triggered, or
    execution cycle is finished and came to a halt.

    :param n: n_clicks of 'run-until-finished' button
    :param user_id: id of the session/user
    :param instruction: current instruction in the div
    :param current_state: current state of the interval
    :return: new state of the interval
    """
    if not n and user_id in user_dict:
        user_dict[user_id]['intervals'] = 0
    elif user_id in user_dict:
        if instruction == '0' * len(instruction):
            copied_cpu = deepcopy(user_dict[user_id]['cpu'])
            copied_cpu.web_next_instruction()
            user_dict[user_id]['intervals'] = n
            if copied_cpu.instruction.to01() == instruction:
                return True
            else:
                return not current_state
        elif n > user_dict[user_id]['intervals']:
            user_dict[user_id]['intervals'] = n
            return not current_state
        else:
            return current_state
    return True


@app.callback(
    Output("run-until-finished-button", "children"),
    [Input('interval', 'disabled'),
     Input('reset', 'n_clicks')],
    [State('run-until-finished', 'n_clicks')]
)
def change_button_color(disabled, reset, n_clicks):
    """
    Change 'run' button to a 'stop' button, when interval is active.

    :param disabled: current state of the interval
    :param reset: n_clicks of 'reset' button
    :param n_clicks: n_clicks of 'run-until-finished' button
    :return: button object
    """
    if disabled:
        return html.Button('RUN', id='run-until-finished', n_clicks=n_clicks,
                           style={"color": button['font'],
                                  "background-color": button['background'],
                                  'width': 200, 'display': 'block',
                                  'font-size': 13})
    else:
        return html.Button('STOP', id='run-until-finished', n_clicks=n_clicks,
                           style={"color": assembly['font'],
                                  "background-color": assembly['background'],
                                  'width': 200, 'display': 'block',
                                  'font-size': 13})


@app.callback(
    Output("interval", "interval"),
    [Input('seconds-storage', 'children'),
     Input('reset', 'n_clicks')]
)
def update_seconds_interval(instructions, reset):
    """
    Change interval, when its is changed in the table by user.

    :param instructions: number of instructions per second
    :param reset: n_clicks of 'reset' button
    :return: new interval value
    """
    return 1000 / instructions


@app.callback(
    Output('seconds-storage', 'children'),
    [Input("seconds", "data"),
     Input('reset', 'n_clicks')]
)
def update_seconds_div(instructions, reset):
    """
    Read users input for instruction/second,
    process it and return a right one. (0<= inst/sec <=1)

    :param instructions: data from the table
    :param reset: n_clicks of 'reset' button
    :return: instruction/second
    """
    try:
        inst_per_second = float(instructions[0]['1'])
        if inst_per_second >= 1 or inst_per_second < 0:
            inst_per_second = 1
        return inst_per_second
    except ValueError:
        return 1


@app.callback(
    Output("seconds", "data"),
    [Input('next', 'n_clicks'),
     Input('reset', 'n_clicks')],
    [State('interval', 'interval')]
)
def update_seconds_table(n_clicks, reset, interval):
    """
    Display the actual interval in the table.

    :param n_clicks: n_clicks of 'next' button
    :param reset: n_clicks of 'reset' button
    :param interval: current interval value
    :raturn: new table data
    """
    return [{'1': (interval / 1000) ** (-1)}]


@app.callback(Output('instruction-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('reset', 'n_clicks')])
def update_instruction(value, user_id, reset):
    """
    Reacts on changes in the instruction div.

    :param value: is not used (is here by default)
    :param user_id: id of the session/user
    :param reset: n_clicks of 'reset' button
    :return: string with instruction
    """
    if user_id in user_dict:
        return f"{user_dict[user_id]['cpu'].instruction.to01()}"
    return '0' * 16


@app.callback(Output('flags-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('reset', 'n_clicks')],
              [State('next', 'n_clicks')])
def update_flags(value, user_id, reset, n_clicks):
    """
    Reacts on changes in the flags div.

    :param value: is not used (is here by default)
    :param user_id: id of the session/user
    :param reset: n_clicks of 'reset' button
    :param n_clicks: n_clicks of 'next' button
    :return: list with flags values
    """
    if user_id in user_dict:
        user_dict[user_id]['next-flags'] = n_clicks
        return list(user_dict[user_id]['cpu'].registers['FR']._state.to01()[-4:])
    return ['0', '0', '0', '0']


@app.callback(Output('registers-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('ip-storage', 'children'),
               Input('reset', 'n_clicks'),
               Input('store-io', 'children'),
               Input('info', 'children')
               ],
              [State('next', 'n_clicks')])
def update_registers(value_not_used, user_id, ip_changes, reset, if_input, info, n_clicks):
    """
    Reacts on changes in the registers div.

    :param value_not_used: is not used (is here by default)
    :param user_id: id of the session/user
    :param ip_changes: new ip value
    :param reset: n_clicks of 'reset' button
    :param if_input: reacts on enabked input
    :param info: isa, architecture and I/O mode
    :param n_clicks: n_clicks of 'next' button
    :return: list with registers
    """
    coef = isas[info.split()[0]]

    if user_id in user_dict:
        user_dict[user_id]['next-registers'] = n_clicks

        items = [(value.name, value._state.tobytes().hex()) for key, value in
                 user_dict[user_id]['cpu'].registers.items()]
        values = []
        for i in range(len(items)):
            values.append(f"{(items[i][0] + ':')} {items[i][1]}")

        return values

    elif ip_changes != 512:
        new_ip = ba2hex(int2ba(int(ip_changes), 16))
        return [['FR: 0000', 'SP: 0000', f'IP: {new_ip}', 'TOS: 0000'], ['FR: 0000', 'SP: 0400', f'IP: {new_ip}',
                                                                         'IR: 0000', 'ACC: 0000'], ['SP: 0400',
                                                                                                    f'IP: {new_ip}',
                                                                                                    'LR: 0000',
                                                                                                    'FR: 0000',
                                                                                                    'R00: 0000',
                                                                                                    'R01: 0000',
                                                                                                    'R02: 0000',
                                                                                                    'R03: 0000'], []][
            coef]
    return \
        [['FR: 0000', 'SP: 0400', 'IP: 0200', 'TOS: 0000'],
         ['FR: 0000', 'SP: 0400', 'IP: 0200', 'IR: 0000', 'ACC: 0000'],
         ['SP: 0400', 'IP: 0200', 'LR: 0000', 'FR: 0000', 'R00: 0000', 'R01: 0000', 'R02: 0000', 'R03: 0000'], []][coef]


@app.callback(Output('output-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('reset', 'n_clicks')])
def update_output(value, user_id, reset):
    """
    Reacts on changes in the output div.

    :param value: is not used
    :param user_id: id of the session/user
    :param reset: n_clicks of 'reset' button
    :return: string with output
    """
    if user_id in user_dict:
        shell_slots = []
        for port, device in user_dict[user_id]['cpu'].ports_dictionary.items():
            shell_slots.append(str(device))

        return " ".join(shell_slots)
    return ""


@app.callback(Output('memory-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('reset', 'n_clicks')
               ],
              [State('next', 'n_clicks')])
def update_memory(value, user_id, reset, n_clicks):
    """
    Reacts on changes in the memory div.

    :param value: is not used (is here by default)
    :param user_id: id of the session/user
    :param reset: n_clicks of 'reset' button
    :param n_clicks: n_clicks of 'next' button
    :return: list with data and program memories
    """
    if user_id in user_dict:
        user_dict[user_id]['next-memory'] = n_clicks
        memory_data = [[], [], [], [], [], [], [], []]
        for i in range(0, len(user_dict[user_id]['cpu'].data_memory.slots), 32 * 8):
            string = ba2hex(user_dict[user_id]['cpu'].data_memory.slots[i:i + 32 * 8])
            for x in range(8):
                memory_data[x].append(" ".join([string[8 * x:8 * x + 8][y:y + 2] for y in range(0, 8, 2)]))
        lst = []
        for i in memory_data:
            lst.append('\t'.join(i))
        if user_dict[user_id]['cpu'].architecture in ["neumann", "harvardm"]:

            return ['\n'.join(lst), '']
        else:
            memory_program = [[], [], [], [], [], [], [], []]
            for i in range(0, len(user_dict[user_id]['cpu'].program_memory.slots), 32 * 8):
                string = ba2hex(user_dict[user_id]['cpu'].program_memory.slots[i:i + 32 * 8])
                for x in range(8):
                    memory_program[x].append(" ".join([string[8 * x:8 * x + 8][y:y + 2] for y in range(0, 8, 2)]))
            lst_program = []
            for i in memory_program:
                lst_program.append('\t'.join(i))

            return ['\n'.join(lst), '\n'.join(lst_program)]

    lst1 = '\t'.join(['00 00 00 00'] * 32)
    lst2 = '\n'.join([lst1] * 8)
    return [lst2, '']


# Update reset-storage
@app.callback(Output('reset-storage', 'children'),
              [Input('reset', 'n_clicks')])
def update_reset(n_clicks):
    """
    Add new value to a reset storage.
    (in order to separate some of the processes)

    :param n_clicks: n_clicks of 'reset' button
    :return: n_clicks
    """
    return n_clicks


@app.callback(Output('reset-storage-code', 'children'),
              [Input('reset-storage', 'children')])
def update_reset(children):
    """
    Add new value to a code reset storage.
    (in order to separate some of the processes)

    :param children: n_clicks of 'reset' button
    :return: children
    """
    return children


# Update IP - info
@app.callback(Output('ip-storage', 'children'),
              [Input('initial-ip', 'data'),
               Input('reset', 'n_clicks')], )
def update_ip(new_ip, reset):
    """
    Add chosen or default instruction pointer to a storage.

    :param new_ip: data from ip table
    :param reset: n_clicks of 'reset' button
    :return: ip as integer
    """
    return ba2int(hex2ba(new_ip[0]['1']))


@app.callback(Output('flags-placeholder', 'children'),
              [Input('flags-table', 'data')],
              [State('id-storage', 'children'),
               State('next', 'n_clicks')])
def manually_change_flags(data_flags, user_id, n_clicks):
    """
    Applies manual changes in the flags to the cpu (or skips, if there were no changes),
    if page was completely loaded and user could have already made that changes.
    (checks time for that situation)

    :param data_flags: data from the flags table
    :param user_id: id of the session/user
    :param n_clicks: n_clicks of 'next' button
    :return: does not matter, updates placeholder
    """
    if user_id in user_dict:
        if user_dict[user_id]['completed-changes'] == ['1', '1', '1', '1', '1'] and (
                time.time() - user_dict[user_id]['time']) > 3:

            flags = ''.join([data_flags[0]['CF'], data_flags[0]['ZF'], data_flags[0]['OF'], data_flags[0]['SF']])
            # Check if flags table did changed (not due to pressing 'next' button)
            if list(user_dict[user_id]['cpu'].registers['FR']._state.to01()[12:]) != [data_flags[0]['CF'],
                                                                                      data_flags[0]['ZF'],
                                                                                      data_flags[0]['OF'],
                                                                                      data_flags[0][
                                                                                          'SF']] and n_clicks == \
                    user_dict[user_id]['next-flags']:
                user_dict[user_id]['time'] = time.time()
                try:
                    cf, zf, of, sf = list(flags)
                    user_dict[user_id]['cpu'].registers['FR']._state[12:16] = bitarray(''.join([cf, zf, of, sf]))
                    user_dict[user_id]['flags-changed'] = True
                    user_dict[user_id]['manual-changes'][0] = '1'
                except ValueError:
                    user_dict[user_id]['manual-changes'][0] = '1'
        user_dict[user_id]['time'] = time.time()
        user_dict[user_id]['manual-changes'][0] = '1'
    return 0


@app.callback(Output('registers-placeholder', 'children'),
              [Input('registers-table', 'data')],
              [State('id-storage', 'children'),
               State('next', 'n_clicks')])
def manually_change_registers(data, user_id, n_clicks):
    """
    Applies manual changes in the registers to the cpu (or skips, if there were no changes),
    if page was completely loaded and user could have already made that changes.
    (checks time for that situation)

    Does not override manual changes in flags!

    :param data: data from the registers table
    :param user_id: id of the session/user
    :param n_clicks: n_clicks of 'next' button
    :return: does not matter, updates placeholder
    """
    if user_id in user_dict:
        if user_dict[user_id]['completed-changes'] == ['1', '1', '1', '1', '1'] and (
                time.time() - user_dict[user_id]['time']) > 3:
            user_dict[user_id]['time'] = time.time()

            items = [(value.name, value._state.tobytes().hex()) for key, value in
                     user_dict[user_id]['cpu'].registers.items()]
            cpu_registers = []
            for i in range(len(items)):
                cpu_registers.append(f"{(items[i][0] + ':')} {items[i][1]}")

            current_table = []
            for key in data[0]:
                current_table.append(f'{key} {data[0][key]}')

            # Some changes in the table occurred (not due to pressing 'next' button)
            if current_table != cpu_registers and n_clicks == user_dict[user_id]['next-registers']:

                new_reg_dict = data[0]

                if user_dict[user_id]['flags-changed']:
                    user_dict[user_id]['flags-changed'] = False
                    new_reg_dict['FR:'] = ba2hex(user_dict[user_id]['cpu'].registers['FR']._state)

                for key, value in new_reg_dict.items():
                    user_dict[user_id]['cpu'].registers[key[:-1]]._state = bitarray(hex2ba(value).to01().rjust(16, '0'))
        user_dict[user_id]['time'] = time.time()
        user_dict[user_id]['manual-changes'][1] = '1'
    return 0


@app.callback(Output('memory-placeholder', 'children'),
              [Input('mem', 'data')],
              [State('id-storage', 'children'),
               State('next', 'n_clicks'),
               State('memory-tabs', 'value')])
def manually_change_memory(data, user_id, n_clicks, chosen_tab):
    """
    Applies manual changes in the memory to the cpu (or skips, if there were no changes),
    if page was completely loaded and user could have already made that changes.
    (checks time for that situation)

    :param data: data from the memory table
    :param user_id: id of the session/user
    :param n_clicks: n_clicks of 'next' button
    :param chosen_tab: determines, with which memory we work (data/program/both)
    :return: does not matter, updates placeholder
    """
    if user_id in user_dict:
        if user_dict[user_id]['completed-changes'] == ['1', '1', '1', '1', '1'] and (
                time.time() - user_dict[user_id]['time']) > 3:
            user_dict[user_id]['time'] = time.time()

            # Callback was provoked, but 'next' ('run') button was not pressed...
            if n_clicks == user_dict[user_id]['next-memory']:

                new_data = bitarray('')
                try:
                    for dictionary in data:
                        for key in dictionary:
                            if key != 'Addr   :  ':
                                new_data += hex2ba(dictionary[key].replace(" ", "").rjust(8, '0'))
                except ValueError:
                    new_data = user_dict[user_id]['cpu'].data_memory.slots

                if chosen_tab == 'data_memory':
                    if new_data != user_dict[user_id]['cpu'].data_memory.slots:
                        user_dict[user_id]['cpu'].data_memory.slots = new_data
                else:
                    if new_data != user_dict[user_id]['cpu'].program_memory.slots:
                        user_dict[user_id]['cpu'].program_memory.slots = new_data
        user_dict[user_id]['time'] = time.time()
        user_dict[user_id]['manual-changes'][2] = '1'
    return 0


@app.callback(Output('link', 'href'),
              [Input('info', 'children')])
def change_link(info):
    """
    Changes help page link accordingly to a chosen ISA.

    :param info: isa, architecture and I/O mode
    :return: new link part
    """
    return f'/help-{info.split()[0]}'


# HELP PAGES
def help(isa):
    """
    Helper function, renders a template for the help page.

    :param isa: current isa of the computer
    :return: html page
    """
    with open("docs/help.json", "r") as file:
        help_dict = json.load(file)[isa]
    with open("modules/registers.json", "r") as file:
        register_dict = json.load(file)[isa]

    p_style = "color: #FFFFFF; padding-left: 12%; width: 75%"
    return render_template('help.html', items=help_dict, p_style=p_style, reg_dict=register_dict)


@app.server.route('/help-risc1')
def help_risc1():
    """
    Create a help page for the risc1 isa.

    :return: html page
    """
    return help('risc1')


@app.server.route('/help-risc2')
def help_risc2():
    """
    Create a help page for the risc2 isa.

    :return: html page
    """
    return help('risc2')


@app.server.route('/help-risc3')
def help_risc3():
    """
    Create a help page for the risc3 isa.

    :return: html page
    """
    return help('risc3')


@app.server.route('/help-cisc')
def help_cisc():
    """
    Create a help page for the cisc isa.

    :return: html page
    """
    return help('cisc')


@app.server.route('/')
def index():
    """
    Create main page of the app.

    :return: app page
    """
    resp = make_response(app)
    return resp


# Run the program
if __name__ == '__main__':
    app.run_server(debug=True)
