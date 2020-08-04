# COLOR PALETTE
# TABLES
table_main_color = '#414364'
table_header_color = '#414364'
table_main_font_color = '#93B6D5'
table_header_font_color = '#93B6D5'

table_header = {"background": table_header_color, "font": table_header_font_color}
table = {"background": table_main_color, "font": table_main_font_color}

# BUTTONS
button_color = '#3D496C'
button_font_color = '#8AA8FE'

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


style_header = {'backgroundColor': background_color, 'border': f'1px {background_color}',
                'color': text_color,
                'font-family': "Roboto Mono, monospace", 'font-size': 12},
style_cell = {'backgroundColor': table_main_color, 'color': table_main_font_color, 'textAlign': 'center',
              'border': f'1px {table_header_color}', 'font-family': "Roboto Mono, monospace", 'font-size': 12},

tab_style = {
    'borderBottom': f'1px solid {background_color}',
    'borderTop': f'1px solid {background_color}',
    'borderLeft': f'1px solid {background_color}',
    'borderRight': f'1px solid {background_color}',
    'font-family': "Roboto Mono, monospace",
    'backgroundColor': background_color,
    'color': 'grey',
    'font-size': '18px'
}

tab_selected_style = {
    'borderTop': f'1px solid {background_color}',
    'borderBottom': f'1px solid {background_color}',
    'borderLeft': f'1px solid {background_color}',
    'borderRight': f'1px solid {background_color}',
    'backgroundColor': background_color,
    'font-family': "Roboto Mono, monospace",
    'color': text_color,
    'font-size': '18px'
}

dropdown_style1 = {'width': 200, 'backgroundColor': background_color,
                   'font-family': "Roboto Mono, monospace",
                   'color': text_color,
                   'font-size': '18px'}
dropdown_style2 = {'width': 310, 'margin-top': -60, 'backgroundColor': background_color,
                   'font-family': "Roboto Mono, monospace",
                   'color': text_color,
                   'font-size': '18px'}
