import plotly.graph_objects as go

# COLOR PALETTE
# TABLES
table_main_color = '#414364'
table_header_color = '#414364'
table_main_font_color = '#93B6D5'
table_header_font_color = '#93B6D5'

table_header = {"background": table_header_color, "font": table_header_font_color}
table = {"background": table_main_color, "font": table_main_font_color}

# BUTTONS
button_color = '#46547C'
button_font_color = '#FCD848'

button = {"background": button_color, "font": button_font_color}

# ASSEMBLY/BINARY
assembly_bg_color = "#4E6585"
assembly_font_color = "#B3CBE1"

assembly = {"background": assembly_bg_color, "font": assembly_font_color}

# OTHER
background_color = '#26273D'
title_color = '#C0C0DB'
text_color = '#9090AC'

not_working_bg = '#5C5C5C'
not_working_text = '#AFAFB2'

not_working = {"background": not_working_bg, "font": not_working_text}

# TRANSPARENT LAYOUT FOR FIGURES
layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'url(assets/reset.css)']
