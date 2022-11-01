import flask
import json
from website.app import app as dash_app

server = flask.Flask(__name__)


@server.route('/')
def index():
    return dash_app.index()


@server.route('/help')
def dash_help():
    with open("docs/help.json", "r") as file:
        help_dict = json.load(file)
    with open("modules/registers.json", "r") as file:
        register_dict = json.load(file)["risc"]

    p_style = "color: #FFFFFF; padding-left: 12%; width: 75%"
    return flask.render_template('help.html', items=help_dict, p_style=p_style, reg_dict=register_dict)


if __name__ == '__main__':
    dash_app.run_server(debug=True)
