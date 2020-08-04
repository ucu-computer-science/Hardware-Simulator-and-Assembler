#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from bitarray.util import ba2hex, hex2ba
from bitarray import bitarray
from copy import deepcopy
import uuid
import dash_table
from flask import Flask, render_template, request, redirect, url_for, make_response, session
import json

# Imports from the project
from modules.processor import CPU
from modules.assembler import Assembler, AssemblerError
from website.color_palette_and_layout import table_header, table, button, assembly, background_color, title_color, \
    text_color, not_working, style_header, style_cell, tab_style, tab_selected_style, \
    dropdown_style1, dropdown_style2
from website.example_programs import examples

# CPU DICTIONARY ( key=user.id, value=dict(cpu, intervals) )
user_dict = dict()
# Numbers of buttons (used to change type of isa during cpu creation, are same for every session and user)
buttons = {0: 'risc1', 1: 'risc2', 2: 'risc3', 3: 'cisc'}

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
                        {'label': 'HARVARD', 'value': 'harvard', 'disabled': True},
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
    ], style={'margin-bottom': 20}),

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
                    dcc.Tabs(id='TABS', value='tabs', children=[
                        dcc.Tab(label='BIN:', value='binary', style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='HEX:', value='hexadecimal', style=tab_style, selected_style=tab_selected_style),
                    ], style={'width': 185, 'height': 58}),
                    html.Div(id='tabs-content')
                ], style={'display': 'inline-block', 'margin-left': 10}),

            ]),

            html.Div([
                # Button to assemble
                html.Button('ASSEMBLE', id='assemble', n_clicks=0,
                            style={'margin-left': 54, 'margin-top': 15, "color": button['font'],
                                   "background-color": button['background'],
                                   'width': 160, 'display': 'inline-block', 'font-family': "Roboto Mono, monospace",
                                   'font-size': 13}),

            ]),

        ], style={'display': 'inline-block'}),

        # Processor
        html.Div(className='row', children=[

            html.Div([

                # Next instruction
                html.Div(id='instruction', style={'display': 'inline-block', 'margin-right': 15}),

                # Output, registers and flags
                html.Div([

                    html.Div(id='output', style={'display': 'inline-block', 'margin-right': 15}),

                    # Registers
                    html.Div(html.Div(id='registers', children=dash_table.DataTable(id='registers-table',
                                                                                    columns=([{'id': ['SP', 'IP', 'LR',
                                                                                                      'FR', 'R00',
                                                                                                      'R01', 'R02',
                                                                                                      'R03'][i],
                                                                                               'name':
                                                                                                   ['SP', 'IP', 'LR',
                                                                                                    'FR', 'R00', 'R01',
                                                                                                    'R02', 'R03'][
                                                                                                       i] + ': '} for i
                                                                                              in
                                                                                              range(4)]),
                                                                                    data=([{['SP', 'IP', 'LR', 'FR',
                                                                                             'R00', 'R01', 'R02',
                                                                                             'R03'][i]: '0000' for i in
                                                                                            range(4)}]),
                                                                                    style_header=style_header[0],
                                                                                    style_cell=style_cell[0],
                                                                                    editable=True,
                                                                                    ), ),
                             style={'display': 'inline-block', 'margin-right': 15}),

                    html.Div(id='flags', children=dash_table.DataTable(id='flags-table',
                                                                       columns=([{'id': ['CF', 'ZF', 'OF', 'SF'][i],
                                                                                  'name': ['CF', 'ZF', 'OF', 'SF'][
                                                                                              i] + ': '} for i in
                                                                                 range(4)]),
                                                                       data=([{['CF', 'ZF', 'OF', 'SF'][i]: '0' for i in
                                                                               range(4)}]),
                                                                       style_header=style_header[0],
                                                                       style_cell=style_cell[0], ),
                             style={'display': 'inline-block', 'margin-right': 30}),

                    html.Div
                        ([

                        dash_table.DataTable(id='seconds',
                                             columns=([{'id': '1', 'name': 'INSTRUCTION PER SECOND'}]),
                                             data=([{'1': '1'}]),
                                             style_header=style_header[0],
                                             style_cell=style_cell[0],
                                             editable=True),

                    ],
                        style={'display': 'inline-block'}),

                ], style={'display': 'inline-block'}),

            ]),

            # Memory
            html.Div(id='memory', style={'margin-top': 20, 'margin-bottom': 20}),

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
                ), ], style={'display': 'inline-block', 'margin-right': 120}),

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
                     style={'display': 'inline-block', 'margin-right': 30}),

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

            ], style={'display': 'inline-block'})

        ], style={'display': 'inline-block', 'margin-left': 70}),

    ]),

    # Link to a help page and license name (someday github link)
    html.Div([dcc.Link('Need some help?', href='/help', refresh=True,
                       style={'color': text_color, 'display': 'inline-block',
                              'font-family': "Roboto Mono, monospace"}),
              html.Div("GNU General Public License v3.0", style={'color': text_color, 'display': 'inline-block',
                                                                 'font-family': "Roboto Mono, monospace",
                                                                 'margin-left': 960})],
             style={'margin-left': 24, 'margin-top': 55, 'display': 'block'}),

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

    # Example storage (for risc3 by default)
    html.Div(id='examples', children=examples['risc3'], style={'display': 'none'}),

], id="wrapper", )


# APP CALLBACKS FOR INPUT/OUTPUT OF THE INFORMATION, ASSEMBLER
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
@app.callback(Output('code', 'children'),
              [Input('assemble', 'n_clicks'),
               Input('info', 'children'),
               Input('id-storage', 'children')],
              [State('input1', 'value')])
def assemble(n_clicks, info, user_id, assembly_code):
    """
    Translate input assembly code to binary and hexadecimal ones.

    :param n_clicks: is not used (is here by default)
    :param info: isa, architecture and I/O mode
    :param user_id: id of the session/user
    :param assembly_code: input assembly code
    :return: binary and hexadecimal codes or assembler error
    """
    isa, architecture, io = info.split()

    global user_dict
    if user_id not in user_dict:
        user_dict[user_id] = dict()
        user_dict[user_id]['cpu'] = CPU(isa, architecture, io, '')
        user_dict[user_id]['save-manual'] = 0
        user_dict[user_id]['undo-manual'] = 0
        user_dict[user_id]['code'] = ''
        user_dict[user_id]['binhex'] = ['', '']

    if not assembly_code or assembly_code in ["input assembly code here", "loading...", '']:
        binary_program = hex_program = ''
        if not user_dict[user_id]['code']:
            user_dict[user_id]['cpu'] = CPU(isa, architecture, io, binary_program)
            user_dict[user_id]['code'] = assembly_code
            user_dict[user_id]['binhex'] = [binary_program, hex_program]
    else:
        try:
            binary_program = Assembler(isa, assembly_code).binary_code
            user_dict[user_id]['cpu'] = CPU(isa, architecture, io, binary_program)
            hex_program = '\n'.join(list(map(lambda x: hex(int(x, 2)), [x for x in binary_program.split('\n') if x])))

        except AssemblerError as err:
            binary_program = hex_program = f'{err.args[0]}'
            user_dict[user_id]['cpu'] = CPU(isa, architecture, io, '')
        user_dict[user_id]['code'] = assembly_code
        user_dict[user_id]['binhex'] = [binary_program, hex_program]

    return binary_program, hex_program


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
            dcc.Textarea(value=code_lst[0],
                         style={'width': 185, 'height': 400, "color": table['font'], 'font-size': '15px',
                                "background-color": table['background'], 'font-family': "Roboto Mono, monospace"},
                         disabled=True)
        ])
    elif tab == 'hexadecimal':
        return html.Div([
            dcc.Textarea(value=code_lst[1],
                         style={'text-align': 'right', 'width': 185, 'height': 400, "color": table['font'],
                                'font-size': '15px',
                                "background-color": table['background'], 'font-family': "Roboto Mono, monospace"},
                         disabled=True)
        ])
    else:
        return html.Div([
            dcc.Textarea(value=code_lst[0],
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
     Input('id-storage', 'children')])
def add_example(example_name, app_examples, user_id):
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
                                data=([{'1': value}]), style_header=style_header[0],
                                style_cell=style_cell[0], ),


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
                                         style_header=style_header[0],
                                         style_cell=style_cell[0],
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
                                style_header=style_header[0],
                                style_cell=style_cell[0],
                                editable=True)


@app.callback(Output('output', 'children'),
              [Input('output-storage', 'children')])
def create_output(value):
    """
    # TODO
    :param value:
    :return:
    """
    return dash_table.DataTable(columns=([{'id': '1', 'name': 'OUTPUT'}]),
                                data=([{'1': value}]),
                                style_header=style_header[0],
                                style_cell=style_cell[0],
                                style_table={'width': '150px'}),


@app.callback(Output('memory', 'children'),
              [Input('memory-storage', 'children')])
def create_memory(value):
    """
    # TODO
    :param value:
    :return:
    """
    if not value[1]:
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

        return dash_table.DataTable(columns=([{'id': i, 'name': i} for i in headers]),
                                    data=data,
                                    style_header=style_header[0],
                                    style_cell=style_cell[0],
                                    style_table={'height': '300px', 'overflowY': 'auto'},
                                    )


# UPDATE HIDDEN INFO FOR PROCESSOR
@app.callback(Output('next-storage', 'children'),
              [Input('next', 'n_clicks'),
               Input('id-storage', 'children'),
               Input('interval', 'n_intervals')])
def update_next(n_clicks, user_id, interval):
    """
    Return n_clicks for the 'next instruction' button,
    so it changes hidden div, on which graphic elements of
    the processor will react.
    Executes next instruction in the cpu.

    :param n_clicks: n_clicks for the 'next instruction' button
    :param user_id: id of the session/user
    :return: same n_clicks
    """
    if interval > 0:
        if user_id in user_dict:
            user_dict[user_id]['cpu'].web_next_instruction()
        return interval
    if n_clicks > 0:
        if user_id in user_dict:
            user_dict[user_id]['cpu'].web_next_instruction()
        return n_clicks


# Work with intervals
@app.callback(
    Output("interval", "disabled"),
    [Input("run-until-finished", "n_clicks"),
     Input('id-storage', 'children'),
     Input("instruction-storage", "children")],
    [State("interval", "disabled")]
)
def run_interval(n, user_id, instruction, current_state):
    if not n:
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
    Output("interval", "interval"),
    [Input("seconds", "data")]
)
def update_seconds(instructions):
    try:
        int(instructions[0]['1'])
        return 1000 / int(instructions[0]['1'])
    except ValueError:
        return 1 * 1000


@app.callback(Output('instruction-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children')])
def update_instruction(value, user_id):
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


@app.callback(Output('registers-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('save-manual', 'n_clicks'),
               Input('undo-manual', 'n_clicks')
               ],
              [State('registers-table', 'data')])
def update_registers(value_not_used, user_id, save_manual, undo_manual, data):
    """
    Reacts on changes in the div, which is
    affected by the 'next instruction' button

    :param value_not_used: is not used
    :param user_id: id of the session/user
    :return: string registers
    """
    if user_id in user_dict:
        if save_manual > user_dict[user_id]['save-manual']:
            user_dict[user_id]['save-manual'] = save_manual
            new_reg_dict = data[0]
            for key, value in new_reg_dict.items():
                user_dict[user_id]['cpu'].registers[key[:-1]]._state = hex2ba(value)

        elif undo_manual > user_dict[user_id]['undo-manual']:
            user_dict[user_id]['undo-manual'] = undo_manual

        items = [(value.name, value._state.tobytes().hex()) for key, value in
                 user_dict[user_id]['cpu'].registers.items()]
        values = []
        for i in range(len(items)):
            values.append(f"{(items[i][0] + ':')} {items[i][1]}")
        return values
    return ['SP: 0400', 'IP: 0200', 'LR: 0000', 'FR: 0000', 'R00: 0000', 'R01: 0000', 'R02: 0000', 'R03: 0000']


@app.callback(Output('flags-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children'),
               Input('save-manual', 'n_clicks'),
               Input('undo-manual', 'n_clicks')
               ],
              [State('flags-table', 'data')])
def update_flags(value, user_id, save_manual, undo_manual, data):
    """
    Reacts on changes in the div, which is
    affected by the 'next instruction' button
    # TODO: about manual

    :param value: is not used
    :param user_id: id of the session/user
    :return: string flags
    """
    if user_id in user_dict:
        if save_manual > user_dict[user_id]['save-manual']:
            user_dict[user_id]['save-manual'] = save_manual
            cf, zf, of, sf = data[0]['CF'], data[0]['ZF'], data[0]['OF'], data[0]['SF'],
            user_dict[user_id]['cpu'].registers['FR']._state[12:16] = bitarray(''.join([cf, zf, of, sf]))

            return [cf, zf, of, sf]
        elif undo_manual > user_dict[user_id]['undo-manual']:
            user_dict[user_id]['undo-manual'] = undo_manual
            cf, zf, of, sf = list(user_dict[user_id]['cpu'].registers['FR']._state.to01()[12:])

            return [cf, zf, of, sf]
        else:
            return list(user_dict[user_id]['cpu'].registers['FR']._state.to01()[-4:])
    return [0, 0, 0, 0]


@app.callback(Output('output-storage', 'children'),
              [Input('next-storage', 'children'),
               Input('id-storage', 'children')])
def update_output(value, user_id):
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
               Input('id-storage', 'children')])
def update_memory(value, user_id):
    """
    Reacts on changes in the div, which is
    affected by the 'next instruction' button

    :param value: is not used
    :param user_id: id of the session/user
    :return: string memory
    """
    if user_id in user_dict:
        memory_data = [[], [], [], [], [], [], [], []]
        for i in range(0, len(user_dict[user_id]['cpu'].data_memory.slots), 32 * 8):
            string = ba2hex(user_dict[user_id]['cpu'].data_memory.slots[i:i + 32 * 8])
            for x in range(8):
                memory_data[x].append(" ".join([string[8 * x:8 * x + 8][y:y + 2] for y in range(0, 8, 2)]))
        lst = []
        for i in memory_data:
            lst.append('\t'.join(i))
        return ['\n'.join(lst), '']
    lst1 = '\t'.join(['00 00 00 00'] * 32)
    lst2 = '\n'.join([lst1] * 8)
    return [lst2, '']


# HELP PAGE
@app.server.route('/help')
def template_test():
    with open("docs/help.json", "r") as file:
        help_dict = json.load(file)
    with open("modules/registers.json", "r") as file:
        register_dict = json.load(file)["risc3"]

    p_style = "color: #FFFFFF; padding-left: 12%; width: 75%"
    return render_template('help.html', items=help_dict, p_style=p_style, reg_dict=register_dict)


@app.server.route('/')
def index():
    resp = make_response(app)
    return resp


# Run the program
if __name__ == '__main__':
    app.run_server(debug=True)
# TODO:
#  cookies to save previous program,
#  edit memory,
#  change memory slots (numeration????????),
#  add new version to server,
#  documentation
