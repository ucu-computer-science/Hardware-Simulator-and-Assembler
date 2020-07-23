#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

# Test module for a help page at templates/help.html
# Relies on the instructions at docs/help.json

import json
from flask import Flask, render_template


app = Flask(__name__)
# TODO: Let's transition to using bare flask in the future, without all of the dash bullshit?
#  This way, the main page is going to be the one developed in app.py, and the /help page or
#  whatever is the one this module was created to test


@app.route("/")
def template_test():
    with open("docs/help.json", "r") as file:
        help_dict = json.load(file)

    return render_template('help.html', items=help_dict)


if __name__ == '__main__':
    app.run(debug=True)
