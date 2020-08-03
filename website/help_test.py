# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# #
# # Assembly Simulator project 2020
# # GNU General Public License v3.0
#
# # Test module for a help page at templates/help.html
# # Relies on the instructions at docs/help.json
#
# import json
# from flask import Flask, render_template
#
#
# app = Flask(__name__)
# # TODO: Let's transition to using bare flask in the future, without all of the dash bullshit?
# #  This way, the main page is going to be the one developed in app.py, and the /help page or
# #  whatever is the one this module was created to test
#
#
# @app.route("/")
# def template_test():
#     with open("docs/help.json", "r") as file:
#         help_dict = json.load(file)
#     with open("modules/registers.json", "r") as file:
#         register_dict = json.load(file)["risc3"]
#
#     p_style = "color: #FFFFFF; padding-left: 12%; width: 75%"
#     return render_template('help.html', items=help_dict, p_style=p_style, reg_dict=register_dict)
#
#
# if __name__ == '__main__':
#     app.run(debug=True)

import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, render_template
import flask
import webbrowser
import os
import json


server = Flask(__name__)
app = dash.Dash(name=__name__, server=server)

app.layout = html.Div()


@app.server.route('/help')
def template_test():
    with open("docs/help.json", "r") as file:
        help_dict = json.load(file)
    with open("modules/registers.json", "r") as file:
        register_dict = json.load(file)["risc3"]

    p_style = "color: #FFFFFF; padding-left: 12%; width: 75%"
    return render_template('help.html', items=help_dict, p_style=p_style, reg_dict=register_dict)


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
