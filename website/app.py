#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from bitarray.util import ba2hex, hex2ba, int2ba, ba2int
from bitarray import bitarray
from copy import deepcopy
import uuid
import dash_table
from flask import Flask, render_template, request, redirect, url_for, make_response, session
import json
from datetime import datetime

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
server.secret_key = b'_5#y2L"F4Q8'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'url(assets/reset.css)', ]
app = dash.Dash(name=__name__, server=server, external_stylesheets=external_stylesheets, routes_pathname_prefix='/')
app.title = "ASSEMBLY SIMULATOR"

# MAIN LAYOUT
app.layout = html.Div([

    # "MAIN MENU"
    html.Div([
        # Title
        dcc.Markdown("ASSEMBLY SIMULATOR",
                     style={'color': title_color, 'font-family': "Roboto Mono, monospace",
                            'font-size': '25px', 'display': 'inline-block', 'margin-left': 100, 'margin-top': 5}),

        dcc.Markdown("CHOOSE ISA:",
                     style={'color': text_color, 'font-family': "Roboto Mono, monospace",
                            'font-size': '18px', 'display': 'inline-block', 'margin-left': 510}),

        dcc.Markdown("ARCHITECTURE:",
                     style={'color': text_color, 'font-family': "Roboto Mono, monospace",
                            'font-size': '18px', 'display': 'inline-block', 'margin-left': 60}),

        dcc.Markdown("I/O MODE:",
                     style={'color': text_color, 'font-family': "Roboto Mono, monospace",
                            'font-size': '18px', 'display': 'inline-block', 'margin-left': 100}),

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
                        {'label': 'MEMORY-MAPPED', 'value': 'mmio', 'disabled': True},
                        {'label': 'SPECIAL COMMANDS', 'value': 'special'},
                    ],
                    value='special',
                    style=dropdown_style1,
                    clearable=False,
                ),

            ], style={'display': 'inline-block'}),

        ], style={'display': 'inline-block', 'margin-left': 800}),
    ], style={'margin-bottom': 5}),

    # ASSEMBLER AND PROCESSOR
    html.Div([

        # Assembler
        html.Div([

            html.Div([

                # Textarea for input of assembly code
                html.Div([
                    dcc.Markdown("ASSEMBLY CODE:",
                                 style={'color': text_color, 'font-family': "Roboto Mono, monospace",
                                        'font-size': '18px', 'margin-left': 60}),
                    dcc.Textarea(id="input1", spellCheck='false',
                                 value="loading...",
                                 style={'width': 235, 'height': 400,
                                        "color": assembly['font'], 'font-size': '15px',
                                        "background-color": assembly['background'],
                                        'font-family': "Roboto Mono, monospace", 'margin-left': 20},
                                 autoFocus='true'),

                ], style={'display': 'inline-block', }),

                # Tabs with bin and hex code
                html.Div([
                    dcc.Tabs(id='TABS', value='binary', children=[
                        dcc.Tab(label='BIN:', value='binary', style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='HEX:', value='hexadecimal', style=tab_style, selected_style=tab_selected_style),
                    ], style={'width': 185, 'height': 58}),
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
                            style={'margin-left': 278, 'margin-top': -40, "color": button['font'],
                                   "background-color": button['background'],
                                   'width': 160, 'display': 'block', 'font-family': "Roboto Mono, monospace",
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

                    html.Div(id='output', children=dash_table.DataTable(id='in_out', columns=([{'id': '1', 'name': 'OUTPUT'}]),
                                        data=([{'1': ''}]),
                                        style_header=style_header,
                                        style_cell=style_cell,
                                        style_table={'width': '150px'}), style={'display': 'inline-block', 'margin-right': 10}),

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
                                             columns=([{'id': '1', 'name': 'INSTRUCTION PER SECOND (Hz)'}]),
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

            html.Div([
                dcc.Dropdown(
                    id='example-dropdown',
                    options=[
                        {'label': 'ALPHABET PRINTOUT', 'value': 'alphabet'},
                        {'label': 'HELLO WORLD', 'value': 'hello'},
                    ],
                    placeholder="CHOOSE AN EXAMPLE PROGRAM",
                    style=dropdown_style2,
                    clearable=False
                ), ], style={'display': 'inline-block', 'margin-right': 30}),

            html.Div([html.Button('NEXT INSTRUCTION', id='next', n_clicks=0,
                                  style={"color": button['font'],
                                         "background-color": button['background'],
                                         'width': 200, 'display': 'block', 'margin-bottom': 15,
                                         'font-family': "Roboto Mono, monospace", 'font-size': 13}),

                      html.Button('RUN | STOP', id='run-until-finished', n_clicks=0,
                                  style={"color": button['font'],
                                         "background-color": button['background'],
                                         'width': 200, 'display': 'block', 'font-family': "Roboto Mono, monospace",
                                         'font-size': 13}), ],
                     style={'display': 'inline-block', 'margin-right': 17}),

            html.Div([
                html.Div([

                    html.Button('SAVE MANUAL CHANGES', id='save-manual', n_clicks=0,
                                style={"color": button['font'],
                                       "background-color": button['background'],
                                       'width': 220, 'display': 'block', 'margin-bottom': 15,
                                       'font-family': "Roboto Mono, monospace", 'font-size': 13}),
                    html.Button('UNDO MANUAL CHANGES', id='undo-manual', n_clicks=0,
                                style={"color": button['font'],
                                       "background-color": button['background'],
                                       'width': 220, 'display': 'block', 'font-family': "Roboto Mono, monospace",
                                       'font-size': 13}),
                ]),

            ], style={'display': 'inline-block'}),

            html.Button('RESET', id='reset', n_clicks=0,
                        style={"color": button['font'], 'display': 'block',
                               "background-color": button['background'], 'margin-left': 780,
                               'margin-top': -70, 'height': 50, 'text-align': 'left',
                               'font-family': "Roboto Mono, monospace", 'font-size': 13}),

        ], style={'display': 'inline-block', 'margin-left': 70}),

    ]),

    # Link to a help page and license name (someday github link)
    html.Div([dcc.Link(html.Button('INSTRUCTION SET (HELP)', style={"color": help_font_color,
                                                                    "background-color": help_color,
                                                                    'margin-bottom': 15,
                                                                    'font-family': "Roboto Mono, monospace",
                                                                    'font-size': 13}), id='link', href='/help-risc3',
                       refresh=True,
                       style={'color': text_color, 'display': 'block',
                              'font-family': "Roboto Mono, monospace", 'width': 260}),
              html.Div("GNU General Public License v3.0", style={'color': text_color, 'display': 'block',
                                                                 'font-family': "Roboto Mono, monospace",
                                                                 'margin-left': 1100, 'margin-top': -35})],
             style={'margin-left': 14, 'margin-top': 40, 'display': 'block'}),

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
    html.Div(id='store-io', style={'display': 'none'})

], id="wrapper", )


# APP CALLBACKS FOR INPUT/OUTPUT OF THE INFORMATION, ASSEMBLER


# Create user id
@app.callback(Output('id-storage', 'children'),
              [Input('id-creation', 'children')])
def get_id(value):
    """
    Return randomly generated id each time new session starts

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
               Input('reset', 'n_clicks')],
              [State('info', 'children'),
               State('id-storage', 'children'),
               State('input1', 'value'),
               State('ip-storage', 'children'),
               State('next', 'n_clicks')])
def assemble(n_clicks, not_used, reset_clicks, info, user_id, assembly_code, ip, next_clicks):
    """
    Translate input assembly code to binary and hexadecimal ones.

    :param n_clicks: is not used (is here by default)
    :param info: isa, architecture and I/O mode
    :param user_id: id of the session/user
    :param assembly_code: input assembly code
    :return: binary and hexadecimal codes or assembler error
    """
    global user_dict

    if not n_clicks and user_id in user_dict:
        user_dict[user_id]['save-manual-flags'] = 0
        user_dict[user_id]['undo-manual-flags'] = 0
        user_dict[user_id]['save-manual-registers'] = 0
        user_dict[user_id]['undo-manual-registers'] = 0
        user_dict[user_id]['save-manual-memory'] = 0
        user_dict[user_id]['undo-manual-memory'] = 0
        user_dict[user_id]['reset'] = 0
        user_dict[user_id]['reset-code'] = 0


    elif n_clicks:
        isa, architecture, io = info.split()

        if user_id not in user_dict:
            user_dict[user_id] = dict()
            user_dict[user_id]['cpu'] = CPU(isa, architecture, io, '')
            user_dict[user_id]['save-manual-flags'] = 0
            user_dict[user_id]['undo-manual-flags'] = 0
            user_dict[user_id]['save-manual-registers'] = 0
            user_dict[user_id]['undo-manual-registers'] = 0
            user_dict[user_id]['save-manual-memory'] = 0
            user_dict[user_id]['undo-manual-memory'] = 0
            user_dict[user_id]['code'] = ''
            user_dict[user_id]['binhex'] = ['', '']
            user_dict[user_id]['flags-changed'] = False
            user_dict[user_id]['intervals'] = 0
            user_dict[user_id]['reset'] = 0
            user_dict[user_id]['reset-code'] = 0
        elif reset_clicks > user_dict[user_id]['reset']:
            user_dict[user_id] = dict()
            user_dict[user_id]['cpu'] = CPU(isa, architecture, io, '')
            user_dict[user_id]['save-manual-flags'] = 0
            user_dict[user_id]['undo-manual-flags'] = 0
            user_dict[user_id]['save-manual-registers'] = 0
            user_dict[user_id]['undo-manual-registers'] = 0
            user_dict[user_id]['save-manual-memory'] = 0
            user_dict[user_id]['undo-manual-memory'] = 0
            user_dict[user_id]['code'] = ''
            user_dict[user_id]['binhex'] = ['', '']
            user_dict[user_id]['flags-changed'] = False
            user_dict[user_id]['intervals'] = 0
            user_dict[user_id]['reset'] = reset_clicks
            user_dict[user_id]['reset-code'] = 0
            assembly_code = "input assembly code here"

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
    :return: string with information
    """
    return ' '.join([isa, arch, io])


# Create tabs content (bin and hex)
@app.callback(Output('tabs-content', 'children'),
              [Input('TABS', 'value'),
               Input('code', 'children'),
               Input('id-storage', 'children')])
def render_content_hex_bin(tab, code_lst, user_id):
    """
    Render two tabs: with binary and with hexadecimal code translations

    :param tab: one of two: binary or hexadecimal
    :param code_lst: list with binary and with hexadecimal code translations
    :return: tabs
    """
    if user_id in user_dict:
        code_lst = user_dict[user_id]['binhex']
    if tab == 'binary':
        return html.Div([
            dcc.Textarea(id='bin_hex', value=code_lst[0],
                         style={'width': 185, 'height': 400, "color": table['font'], 'font-size': '15px',
                                "background-color": table['background'], 'font-family': "Roboto Mono, monospace"},
                         disabled=True)
        ])
    elif tab == 'hexadecimal':
        return html.Div([
            dcc.Textarea(id='bin_hex', value=code_lst[1],
                         style={'text-align': 'right', 'width': 185, 'height': 400, "color": table['font'],
                                'font-size': '15px',
                                "background-color": table['background'], 'font-family': "Roboto Mono, monospace"},
                         disabled=True)
        ])
    else:
        return html.Div([
            dcc.Textarea(id='bin_hex', value=code_lst[0],
                         style={'width': 185, 'height': 400, "color": table['font'], 'font-size': '15px',
                                "background-color": table['background'], 'font-family': "Roboto Mono, monospace"},
                         disabled=True)
        ])


# Update div with examples
@app.callback(
    Output('examples', 'children'),
    [Input('isa-dropdown', 'value')])
def update_examples(isa):
    return examples[isa]


# Add a chosen example to the textarea
@app.callback(
    Output('input-code', 'children'),
    [Input('example-dropdown', 'value'),
     Input('examples', 'children'),
     Input('id-storage', 'children'),
     Input('reset', 'n_clicks')])
def add_example(example_name, app_examples, user_id, reset_clicks):
    if user_id in user_dict:
        if reset_clicks > user_dict[user_id]['reset-code']:
            user_dict[user_id]['reset-code'] = reset_clicks
            return "input assembly code here"
    if example_name == 'alphabet':
        return app_examples[0]
    elif example_name == 'hello':
        return app_examples[1]
    if user_id in user_dict:
        if user_dict[user_id]['code']:
            return user_dict[user_id]['code']
        else:
            return "input assembly code here"
    else:
        return "input assembly code here"


# Add current code to the textarea
@app.callback(
    Output('input1', 'value'),
    [Input('input-code', 'children')])
def code(input_code):
    return input_code


# APP CALLBACKS FOR CREATION OF GRAPHIC ELEMENTS OF THE PROCESSOR
@app.callback(Output('instruction', 'children'),
              [Input('instruction-storage', 'children')])
def create_instruction(value):
    """
    # TODO
    :param value:
    :return:
    """
    return dash_table.DataTable(columns=([{'id': '1', 'name': 'NEXT INSTRUCTION'}]),
                                data=([{'1': value}]), style_header=style_header,
                                style_cell=style_cell, ),


@app.callback(Output('registers', 'children'),
              [Input('registers-storage', 'children')])
def create_registers(value):
    """
    # TODO
    :param value:
    :return:
    """
    regs = []
    values = []
    for i in value:
        regs.append(i.split(' ')[0])
        values.append(i.split(' ')[1])

    return html.Div(dash_table.DataTable(id='registers-table',
                                         columns=([{'id': regs[i], 'name': regs[i]} for i in range(len(regs))]),
                                         data=([{regs[i]: values[i] for i in range(len(regs))}]),
                                         style_header=style_header,
                                         style_cell={'backgroundColor': table_main_color,
                                                     'color': table_main_font_color, 'textAlign': 'center',
                                                     'border': f'1px {table_header_color}',
                                                     'font-family': "Roboto Mono, monospace", 'font-size': 12,
                                                     'minWidth': 33.5},
                                         editable=True
                                         ))


@app.callback(Output('flags', 'children'),
              [Input('flags-storage', 'children')])
def create_flags(value):
    """
    # TODO
    :param value:
    :return:
    """
    flags = ['CF', 'ZF', 'OF', 'SF']
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
    # TODO
    :param value:
    :return:
    """
    if user_id in user_dict:
        if user_dict[user_id]['cpu'].is_input_active:
            return dash_table.DataTable(id='in_out', columns=([{'id': '1', 'name': 'INPUT'}]),
                                        data=([{'1': ''}]),
                                        style_header=style_header,
                                        style_cell=style_cell,
                                        style_table={'width': '150px'}, editable=True)

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
    if editable:
        char = data[0]['1']
        if len(char) != 0:
            user_dict[user_id]['cpu'].input_finish(hex2ba(char).to01())
        return char

# mov_low %R00, $1 in %R00, $1 mov_low %R00, $10

@app.callback(Output('memory-div', 'children'),
              [Input('next', 'n_clicks')],
              [State('info', 'children')])
def change_memory_tabs(n_clicks, info):
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
               Input('memory-storage', 'children')])
def create_memory(tab, value):
    """
    # TODO
    :param value:
    :return:
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
    Executes next instruction in the cpu.

    :param n_clicks: n_clicks for the 'next instruction' button
    :param user_id: id of the session/user
    :return: same n_clicks
    """
    if user_id in user_dict:
        if not user_dict[user_id]['cpu'].is_input_active:
            if interval > 0:
                user_dict[user_id]['cpu'].web_next_instruction()
                return interval
            if n_clicks > 0:
                user_dict[user_id]['cpu'].web_next_instruction()
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
    Output("run-until-finished", "style"),
    [Input('interval', 'disabled'),
     Input('reset', 'n_clicks')]
)
def change_button_color(disabled, reset):
    if disabled:
        return {"color": button['font'],
                "background-color": button['background'],
                'width': 200, 'display': 'block', 'font-family': "Roboto Mono, monospace",
                'font-size': 13}
    else:
        return {"color": assembly['font'],
                "background-color": assembly['background'],
                'width': 200, 'display': 'block', 'font-family': "Roboto Mono, monospace",
                'font-size': 13}


@app.callback(
    Output("interval", "interval"),
    [Input('seconds-storage', 'children'),
     Input('reset', 'n_clicks')]
)
def update_seconds_interval(instructions, reset):
    return 1000 / instructions


@app.callback(
    Output('seconds-storage', 'children'),
    [Input("seconds", "data"),
     Input('reset', 'n_clicks')]
)
def update_seconds_div(instructions, reset):
    try:
        inst_per_second = int(instructions[0]['1'])
        if inst_per_second >= 8:
            inst_per_second = 7
        return inst_per_second
    except ValueError:
        return 1


@app.callback(
    Output("seconds", "data"),
    [Input('next', 'n_clicks'),
     Input('reset', 'n_clicks')],
    [State('interval', 'interval'),
     ]
)
def update_seconds_table(n_clicks, reset, interval):
    return [{'1': (interval / 1000) ** (-1)}]


@app.callback(Output('instruction-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('reset', 'n_clicks')])
def update_instruction(value, user_id, reset):
    """
    Reacts on changes in the div, which is
    affected by the 'next instruction' button

    :param value: is not used
    :param user_id: id of the session/user
    :return: string instruction
    """
    if user_id in user_dict:
        return f"{user_dict[user_id]['cpu'].instruction.to01()}"
    return '0' * 16


@app.callback(Output('flags-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('save-manual', 'n_clicks'),
               Input('undo-manual', 'n_clicks'),
               Input('reset', 'n_clicks')
               ],
              [State('flags-table', 'data'),
               State('registers-table', 'data')])
def update_flags(value, user_id, save_manual, undo_manual, reset, data_flags, data_regs):
    """
    Reacts on changes in the div, which is
    affected by the 'next instruction' button
    # TODO: about manual

    :param value: is not used
    :param user_id: id of the session/user
    :return: string flags
    """
    if user_id in user_dict:
        flags = ''.join([data_flags[0]['CF'], data_flags[0]['ZF'], data_flags[0]['OF'], data_flags[0]['SF']])
        if list(user_dict[user_id]['cpu'].registers['FR']._state.to01()[12:]) == [data_flags[0]['CF'],
                                                                                  data_flags[0]['ZF'],
                                                                                  data_flags[0]['OF'],
                                                                                  data_flags[0]['SF']]:
            if user_dict[user_id]['cpu'].registers['FR']._state.to01()[12:] != hex2ba(data_regs[0]['FR:']).to01().rjust(
                    4, '0')[12:]:
                flags = hex2ba(data_regs[0]['FR:']).to01()[-4:]
            else:
                save_manual -= 1

        if save_manual > user_dict[user_id]['save-manual-flags']:
            user_dict[user_id]['save-manual-flags'] = save_manual
            try:
                cf, zf, of, sf = list(flags)
                user_dict[user_id]['cpu'].registers['FR']._state[12:16] = bitarray(''.join([cf, zf, of, sf]))
                user_dict[user_id]['flags-changed'] = True
                return [cf, zf, of, sf]
            except ValueError:
                cf, zf, of, sf = list(user_dict[user_id]['cpu'].registers['FR']._state.to01()[12:])

                return [cf, zf, of, sf]
        elif undo_manual > user_dict[user_id]['undo-manual-flags']:
            user_dict[user_id]['undo-manual-flags'] = undo_manual
            cf, zf, of, sf = list(user_dict[user_id]['cpu'].registers['FR']._state.to01()[12:])

            return [cf, zf, of, sf]
        else:
            return list(user_dict[user_id]['cpu'].registers['FR']._state.to01()[-4:])
    return ['0', '0', '0', '0']


@app.callback(Output('registers-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('save-manual', 'n_clicks'),
               Input('undo-manual', 'n_clicks'),
               Input('ip-storage', 'children'),
               Input('reset', 'n_clicks'),
               Input('store-io', 'children')
               ],
              [State('registers-table', 'data')])
def update_registers(value_not_used, user_id, save_manual, undo_manual, ip_changes, reset, if_input, data):
    """
    Reacts on changes in the div, which is
    affected by the 'next instruction' button

    :param value_not_used: is not used
    :param user_id: id of the session/user
    :return: string registers
    """
    if user_id in user_dict:
        if save_manual > user_dict[user_id]['save-manual-registers']:
            user_dict[user_id]['save-manual-registers'] = save_manual
            new_reg_dict = data[0]

            if user_dict[user_id]['flags-changed']:
                user_dict[user_id]['flags-changed'] = False
                new_reg_dict['FR:'] = ba2hex(user_dict[user_id]['cpu'].registers['FR']._state)

            for key, value in new_reg_dict.items():
                user_dict[user_id]['cpu'].registers[key[:-1]]._state = bitarray(hex2ba(value).to01().rjust(16, '0'))

        elif undo_manual > user_dict[user_id]['undo-manual-registers']:
            user_dict[user_id]['undo-manual-registers'] = undo_manual

        items = [(value.name, value._state.tobytes().hex()) for key, value in
                 user_dict[user_id]['cpu'].registers.items()]
        values = []
        for i in range(len(items)):
            values.append(f"{(items[i][0] + ':')} {items[i][1]}")
        return values
    elif ip_changes != 512:
        return ['SP: 0400', f'IP: {ba2hex(int2ba(int(ip_changes), 16))}', 'LR: 0000', 'FR: 0000', 'R00: 0000',
                'R01: 0000', 'R02: 0000', 'R03: 0000']
    return ['SP: 0400', 'IP: 0200', 'LR: 0000', 'FR: 0000', 'R00: 0000', 'R01: 0000', 'R02: 0000', 'R03: 0000']


@app.callback(Output('output-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('reset', 'n_clicks')])
def update_output(value, user_id, reset):
    """
    Reacts on changes in the div, which is
    affected by the 'next instruction' button

    :param value: is not used
    :param user_id: id of the session/user
    :return: string output
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
               Input('save-manual', 'n_clicks'),
               Input('undo-manual', 'n_clicks'),
               Input('reset', 'n_clicks')
               ],
              [State('mem', 'data'),
               State('memory-tabs', 'value')])
def update_memory(value, user_id, save_manual, undo_manual, reset, data, chosen_tab):
    """
    Reacts on changes in the div, which is
    affected by the 'next instruction' button

    :param value: is not used
    :param user_id: id of the session/user
    :return: string memory
    """
    if user_id in user_dict:
        if save_manual > user_dict[user_id]['save-manual-memory']:
            user_dict[user_id]['save-manual-memory'] = save_manual
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


        elif undo_manual > user_dict[user_id]['undo-manual-memory']:
            user_dict[user_id]['undo-manual-memory'] = undo_manual
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


# Update buttons
@app.callback([Output('save-manual', 'n_clicks'),
               Output('undo-manual', 'n_clicks'), ],
              [Input('id-storage', 'children'),
               Input('reset', 'n_clicks')])
def update_buttons(user_id, reset):
    if user_id in user_dict:
        return user_dict[user_id]['save-manual-flags'], user_dict[user_id]['undo-manual-flags']
    return 0, 0


# Update IP - info
@app.callback(Output('ip-storage', 'children'),
              [Input('initial-ip', 'data'),
               Input('reset', 'n_clicks')], )
def update_ip(new_ip, reset):
    return ba2int(hex2ba(new_ip[0]['1']))


# Enable only Harvard architecture for stack
@app.callback([Output('architecture-dropdown', 'options'),
               Output('architecture-dropdown', 'value')],
              [Input('input1', 'value')],
              [State('info', 'children'),
               State('architecture-dropdown', 'value')])
def control_architecture(not_used, info, initial_arch):
    if info.split()[0] == 'risc1':
        return [{'label': 'VON NEUMANN', 'value': 'neumann', 'disabled': True},
                {'label': 'HARVARD', 'value': 'harvard'}, ], 'harvard'
    else:
        return [{'label': 'VON NEUMANN', 'value': 'neumann'}, {'label': 'HARVARD', 'value': 'harvard'}, ], initial_arch


@app.callback(Output('link', 'href'),
              [Input('info', 'children')])
def change_link(info):
    return f'/help-{info.split()[0]}'


# HELP PAGES
def help(isa):
    with open("docs/help.json", "r") as file:
        help_dict = json.load(file)
    with open("modules/registers.json", "r") as file:
        register_dict = json.load(file)[isa]

    p_style = "color: #FFFFFF; padding-left: 12%; width: 75%"
    return render_template('help.html', items=help_dict, p_style=p_style, reg_dict=register_dict)


@app.server.route('/help-risc1')
def help_risc1():
    return help('risc1')


@app.server.route('/help-risc2')
def help_risc2():
    return help('risc2')


@app.server.route('/help-risc3')
def help_risc3():
    return help('risc3')


@app.server.route('/help-cisc')
def help_cisc():
    return help('cisc')


@app.server.route('/')
def index():
    resp = make_response(app)
    return resp


# Run the program
if __name__ == '__main__':
    app.run_server(debug=True)
# TODO: documentation
