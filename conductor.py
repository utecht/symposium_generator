#!/usr/bin/env python3
import jinja2
import os
from jinja2 import Template
import csv

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

def clean_string(text):
    text = text.replace('&', '\\&')
    return text

def prep_authors(presentation, author_line):
    pre_name = "Abstract Co-Author's Name: "
    pre_institution = "Co-Author's Institution: "
    pre_other = "Author's Institution - Other: "

    a = author_line.split(', ')

    presentation['coauthors'] = []
    # no co-authors, but second institution for primary author
    if pre_institution in a[0]:
        institution = a.pop()
        institution = institution.replace(pre_institution, '')
        if institution not in presentation['institutions']:
            presentation['institutions'].append(institution)
            if len(presentation['institutions']) == 1:
                presentation['author_ss'] == '1'
            elif len(presentation['institutions']) == 2:
                presentation['author_ss'] == '1,2'
    else:
        while True:
            if(len(a) == 0):
                break
            name = a.pop(0)
            name = name.replace(pre_name, '')
            if(len(a) > 0 and pre_institution in a[0]):
                institution = a.pop(0)
                institution = institution.replace(pre_institution, '')
                if(institution == 'Other' and 
                           len(a) > 0 and
                           pre_other in a[0]):
                    institution = a.pop(0)
                    institution = institution.replace(pre_other, '')
                if institution != 'Other':
                    if institution not in presentation['institutions']:
                        presentation['institutions'].append(institution)
                    presentation['coauthors'].append({'name': name,
                                                      'ss': presentation['institutions'].index(institution) + 1})
                else:
                    presentation['coauthors'].append({'name': name})
            else:
                presentation['coauthors'].append({'name': name})

def render_poster_sessions(presentations):
    template = latex_jinja_env.get_template('poster_template.tex')
    even_presentations = list(filter(lambda x: x['number'] % 2 == 0, presentations))
    odd_presentations = list(filter(lambda x: x['number'] % 2 == 1, presentations))
    with open('latex/even_session.tex', 'w') as f:
        f.write(template.render(presentations=even_presentations,
                                times="10:30 am  --  11:30 am",
                                session_number="I",
                                even_odd="even"))
    with open('latex/odd_session.tex', 'w') as f:
        f.write(template.render(presentations=odd_presentations,
                                times="12:15 pm  --  1:15 pm",
                                session_number="II",
                                even_odd="odd"))

def prep_registration(reg):
    p = {}
    p['presenter'] = reg['Name (First)'] + ' ' + reg['Name (Last)']
    p['author'] = reg['Abstract Author']
    p['author_ss'] = '1'
    p['title'] = clean_string(reg['Abstract Title'])
    institutions = [reg["Author's Institution"], reg["Author's Institution - Other"]]
    if '' in institutions:
        institutions.remove('')
    if 'Other' in institutions:
        institutions.remove('Other')
    if len(institutions) == 1:
        p['author_ss'] == '1'
    elif len(institutions) == 2:
        p['author_ss'] == '1,2'
    p['institutions'] = institutions
    prep_authors(p, reg['Add Additional Authors'])
    return p

registrations = []
with open('registration.csv', 'r', encoding='utf-8-sig') as csvfile:
    csvreader = csv.DictReader(csvfile, dialect='excel')
    for row in csvreader:
        registrations.append(row)

presentations = []
for registration in registrations:
    if(registration['Presenter'] == 'Yes'):
        presentations.append(prep_registration(registration))

for x, p in enumerate(presentations):
    p['number'] = x + 1

render_poster_sessions(presentations)
