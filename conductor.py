#!/usr/bin/env python3
import jinja2
import os
from jinja2 import Template
import csv

def clean_string(text):
    text = text.replace('&', '\\&')
    return text

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
    if reg["Abstract Co-Author's Name"]:
        name = reg["Abstract Co-Author's Name"]
        org_name = reg["Co-Author's Institution"]
        if org_name == "Other":
            org_name = reg["Co-Author's Institution - Other"]
        if org_name not in institutions:
            institutions.append(org_name)
        ss = institutions.index(org_name) + 1
        p['coauthors'] = [{'name': name, 'ss': ss}]
    if reg["Abstract Co-Author's Name2"]:
        name = reg["Abstract Co-Author's Name2"]
        org_name = reg["Co-Author's Institution2"]
        if org_name == "Other":
            org_name = reg["Co-Author's Institution - Other2"]
        if org_name not in institutions:
            institutions.append(org_name)
        ss = institutions.index(org_name) + 1
        p['coauthors'].append({'name': name, 'ss': ss})


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
    if(registration['Undergraduate Types'] == 'Presenter'):
        p['presenting'] = 'P'
        if('Oral' in registration['Presentation Preference']):
            p['presenting'] = 'T'
            p['number'] = int(registration['Presentation Preference'].split()[2])
        prep_presentation(p, reg)
    else:
        p['presenting'] = None
    return p


if __name__ == '__main__':
    registrations = []
    with open('registration.csv', 'r', encoding='utf-8-sig') as csvfile:
        csvreader = csv.DictReader(csvfile, dialect='excel')
        for row in csvreader:
            registrations.append(row)

    attendees = []
    for registration in registrations:
            attendees.append(prep_registration(registration))

    poster_index = 1
    for a in attendees:
        if a.get('presenting', '') == 'P':
            a['presentation_type'] = 'P'
            a['number'] = poster_index
            poster_index += 1
        elif a.get('presenting', '') == 'T':
            a['presentation_type'] = 'T'

    # from http://eosrei.net/articles/2015/11/latex-templates-python-and-jinja2-generate-pdfs
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

    presentations = list(filter(lambda x: x['presenting'] == 'P', attendees))
    template = latex_jinja_env.get_template('poster_template.tex')
    even_presentations = list(filter(lambda x: x['number'] % 2 == 0, presentations))
    odd_presentations = list(filter(lambda x: x['number'] % 2 == 1, presentations))
    with open('latex/even_poster_session.tex', 'w') as f:
        f.write(template.render(presentations=even_presentations,
                                session_times="12:15 pm  --  1:15 pm",
                                session_name="Poster Session II / even number posters"))
    with open('latex/odd_poster_session.tex', 'w') as f:
        f.write(template.render(presentations=odd_presentations,
                                session_times="10:30 am  --  11:30 am",
                                session_name="Post Session I / odd number posters"))

    presentations = list(filter(lambda x: x['presenting'] == 'T', attendees))
    template = latex_jinja_env.get_template('poster_template.tex')
    even_presentations = list(filter(lambda x: x['number'] % 2 == 0, presentations))
    odd_presentations = list(filter(lambda x: x['number'] % 2 == 1, presentations))
    even_presentations.sort(key=lambda x:x['number'])
    odd_presentations.sort(key=lambda x:x['number'])
    with open('latex/even_talk_session.tex', 'w') as f:
        f.write(template.render(presentations=even_presentations,
                                session_times="1:15 pm  --  2:45 pm",
                                session_name="Talk Session II / even number talks"))
    with open('latex/odd_talk_session.tex', 'w') as f:
        f.write(template.render(presentations=odd_presentations,
                                session_times="8:45 am  --  10:15 am",
                                session_name="Talk Session I / odd number talks"))

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
                if len(a['activities']) > 0:
                    a['activities'] += "/Judge"
                else:
                    a['activities'] += "Judge"

    template = latex_jinja_env.get_template('index_template.tex')
    with open('latex/index.tex', 'w') as f:
        f.write(template.render(attendees=attendees))
