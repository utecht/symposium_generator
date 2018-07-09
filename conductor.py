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
                presentation['author_ss'] = '1'
            elif len(presentation['institutions']) == 2:
                presentation['author_ss'] = '1,2'
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
                                session_times="12:15 pm  --  1:15 pm",
                                session_name="Poster Session II / even number posters"))
    with open('latex/odd_session.tex', 'w') as f:
        f.write(template.render(presentations=odd_presentations,
                                session_times="10:30 am  --  11:30 am",
                                session_name="Post Session I / odd number posters"))

def prep_presentation(p, reg):
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

def prep_registration(reg):
    p = {}
    p['first_name'] = reg['Name (First)']
    p['last_name'] = reg['Name (Last)']
    p['affiliation'] = reg['Registrant Affiliation']
    if p['affiliation'] == 'Other':
        p['affiliation'] = reg["Registrant Affiliation - Other"]
    p['research_program'] = reg["Registrant's Undergraduate Research Program"]
    p['reg_type'] = reg["Type of Registration"]
    p['judge'] = reg['Are you willing to help judge student posters and oral presentations?'] == 'Yes'
    if p['research_program'] == "Other (Please list below)":
        p['research_program'] = reg["Registrant's Undergraduate Research Program - Other"]
    if(registration['Presenter'] == 'Yes'):
        p['presenting'] = 'P'
        prep_presentation(p, reg)
    else:
        p['presenting'] = None
    return p

registrations = []
with open('registration.csv', 'r', encoding='utf-8-sig') as csvfile:
    csvreader = csv.DictReader(csvfile, dialect='excel')
    for row in csvreader:
        registrations.append(row)

attendees = []
for registration in registrations:
        attendees.append(prep_registration(registration))

poster_index = 1
talk_index = 1
for a in attendees:
    if a.get('presenting', '') == 'P':
        a['presentation_type'] = 'P'
        a['number'] = poster_index
        poster_index += 1

presentations = list(filter(lambda x: x['presenting'] == 'P', attendees))
render_poster_sessions(presentations)

for a in attendees:
    if a.get('presenting', '') == 'P':
        a['activities'] = f"P{a['number']}, Poster"
    elif a.get('presenting', '') == 'T':
        a['activities'] = f"T{a['number']}, Oral"
    elif a['reg_type'] == 'Undergraduate':
        a['activities'] = 'Non-Presenter'
    else:
        a['activities'] = a['reg_type']
        if a['judge']:
            a['activities'] += "/Judge"

template = latex_jinja_env.get_template('index_template.tex')
with open('latex/index.tex', 'w') as f:
    f.write(template.render(attendees=attendees))
