#!/usr/bin/env python
import jinja2
import os
from jinja2 import Template

latex_jinja_env = jinja2.Environment(
        block_start_string = '\BLOCK{',
        block_end_string = '}',
        variable_start_string = '\VAR{',
        variable_end_string = '}',
        comment_start_string = '\#{',
        comment_end_string = '}',
        line_statement_prefix = '%%',
        line_comment_prefix = '%#',
        trim_blocks = False,
        autoescape = False,
        loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)

p = {'number': 1,
     'presenter':'Joseph Utecht',
     'author':'Joseph Utecht',
     'author_ss':'1',
     'coauthors': [ {'name': 'Sonya Utecht',
                     'ss': [1, 2]},
                    {'name': 'Quasar Jarosz',
                     'ss': [2]} ],
     'title': "A Brief History of Why Not to Accept Odd Jobs",
     'institutions': [ 'University of Arkansas for Medical Sciences',
                       'University of Arkansas at Little Rock']
     }

presentations = [p,p,p]
template = latex_jinja_env.get_template('poster_template.tex')
print(template.render(presentations=presentations))
