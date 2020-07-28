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

    # Title
    dcc.Markdown("ASSEMBLY SIMULATOR",
                 style={'color': title_color, 'font-family': "Roboto Mono, monospace",
                        'font-size': '25px'}),

    # Dropdowns for isa, architecture and i/o mode
    html.Div([

        dcc.Dropdown(
            id='isa-dropdown',
            options=[
                {'label': 'REGISTER RISC', 'value': 'risc3'},
                {'label': 'REGISTER CISC', 'value': 'cisc'},
                {'label': 'STACK', 'value': 'risc1'},
                {'label': 'ACCUMULATOR', 'value': 'risc2'},
            ],
            value='risc3',
            style={'display': 'inline-block'}
        ),
        dcc.Dropdown(
            id='architecture-dropdown',
            options=[
                {'label': 'VON NEUMANN', 'value': 'neumann'},
                {'label': 'HARVARD', 'value': 'harvard'},
            ],
            value='neumann',
            style={'display': 'inline-block'}
        ),
        dcc.Dropdown(
            id='io-dropdown',
            options=[
                {'label': 'MEMORY-MAPPED', 'value': 'mmio'},
                {'label': 'SPECIAL COMMANDS', 'value': 'special'},
            ],
            value='special',
            style={'display': 'inline-block'}
        ),

    ]),

    # HIDDEN DIVS
    # Main info (has default settings)
    html.Div(id="info", children='risc3 neumann special', style={'display': 'none'}),
    # Id creation and storage
    html.Div(id='target', style={'display': 'none'}),
    html.Div(id='input', style={'display': 'none'}),

])


# APP CALLBACKS
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


# CREATE GRAPHIC ELEMENTS

# Run the program
if __name__ == '__main__':
    # SERVER LAUNCH
    dev_server = app.run_server
    app.run_server(debug=True, threaded=True)
