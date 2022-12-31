from copy import deepcopy
# COLOR PALETTE
# TABLES
table_main_color = '#414364'
table_header_color = '#414364'
table_main_font_color = '#93B6D5'
table_header_font_color = '#93B6D5'
memory_font = '#9090AC'

memory_tab = '#2D2E46'
memory_tab_selected = '#52557C'
memory_tab_font = '#696985'
memory_tab_selected_font = '#9C9CB6'

table_header = {"background": table_header_color, "font": table_header_font_color}
table = {"background": table_main_color, "font": table_main_font_color}

# BUTTONS
button_color = '#3D496C'
button_font_color = '#8AA8FE'
help_color = '#29233d'
help_font_color = '#dd5'

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

style_header = {'backgroundColor': background_color, 
                'border': f'1px {background_color}',
                'color': text_color, 
                'font-size': 12}

style_memory_header = {'backgroundColor': table_main_color, 
                       'border': f'1px {background_color}',
                       'color': memory_font, 
                       'font-size': 12}

style_cell = {'backgroundColor': table_main_color, 
              'color': table_main_font_color, 
              'textAlign': 'center',
              'border': f'1px {table_header_color}', 
              'font-size': 12}

tab_style = {
    'borderBottom': f'1px solid {background_color}',
    'borderTop': f'1px solid {background_color}',
    'borderLeft': f'1px solid {background_color}',
    'borderRight': f'1px solid {background_color}',
    'backgroundColor': background_color,
    'color': 'grey',
    'font-size': '18px'
}

memory_tab_style = deepcopy(tab_style)
memory_tab_style['font-size'] = 12
memory_tab_style['backgroundColor'] = memory_tab
memory_tab_style['color'] = memory_tab_font
memory_tab_style['padding'] = 3


tab_selected_style = {
    'borderTop': f'1px solid {background_color}',
    'borderBottom': f'1px solid {background_color}',
    'borderLeft': f'1px solid {background_color}',
    'borderRight': f'1px solid {background_color}',
    'backgroundColor': background_color,
    'color': text_color,
    'font-size': '18px'
}

memory_selected_tab_style = deepcopy(tab_selected_style)
memory_selected_tab_style['font-size'] = 12
memory_selected_tab_style['backgroundColor'] = memory_tab_selected
memory_selected_tab_style['color'] = memory_tab_selected_font
memory_selected_tab_style['padding'] = 3

memory_selected_tab_style2 = deepcopy(memory_selected_tab_style)
memory_selected_tab_style2['color'] = text_color
memory_selected_tab_style2['backgroundColor'] = background_color


dropdown_style1 = {'width': 200, 
                   'backgroundColor': background_color,
                   'color': text_color,
                   'font-size': '18px'}

dropdown_style2 = {'width': 285, 
                   'backgroundColor': background_color,
                   'color': text_color,
                   'font-size': '18px'}
