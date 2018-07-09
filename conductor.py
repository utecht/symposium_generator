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

def prep_authors(presentation, author_line):
    pre_name = "Abstract Co-Author's Name: "
    pre_institution = "Co-Author's Institution: "
    pre_other = "Author's Institution - Other: "

    a = author_line.split(', ')

    presentation['coauthors'] = []

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
                                              'ss': [presentation['institutions'].index(institution) + 1]})
        else:
            presentation['coauthors'].append({'name': name})

def render_poster_session(presentations):
    template = latex_jinja_env.get_template('poster_template.tex')
    print(template.render(presentations=presentations))

def prep_registration(reg):
    p = {}
    p['presenter'] = reg['Name (First)'] + ' ' + reg['Name (Last)']
    p['author'] = reg['Abstract Author']
    p['author_ss'] = '1'
    p['title'] = reg['Abstract Title']
    institutions = [reg["Author's Institution"], reg["Author's Institution - Other"]]
    if institutions[1] == "":
        institutions.pop()
    else:
        p['author_ss'] = ['1', '2']
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

render_poster_session([p, p, p])
