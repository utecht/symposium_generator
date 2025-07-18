#!/usr/bin/env python3
import jinja2
import os
from jinja2 import Template
import csv
import re


def clean_string(text):
    text = text.replace("&", "\\&")
    return text.strip()


def prep_presentation(p, reg):
    p["author"] = reg["Abstract Author"]
    p["author_ss"] = "1"
    p["title"] = clean_string(reg["Abstract Title"])
    institutions = [
        clean_string(reg["Author's Institution"]),
        # clean_string(reg["Author's Institution - Other"]),
    ]
    if "" in institutions:
        institutions.remove("")
    if "Other" in institutions:
        institutions.remove("Other")
    if len(institutions) == 1:
        p["author_ss"] == "1"
    elif len(institutions) == 2:
        p["author_ss"] == "1,2"
    p["institutions"] = institutions
    if reg["Abstract Co-Author's Name"]:
        name = clean_string(reg["Abstract Co-Author's Name"])
        org_name = clean_string(reg["Co-Author's Institution"])
        if org_name == "Other":
            # org_name = clean_string(reg["Co-Author's Institution - Other"])
            org_name = ""
        if org_name not in institutions:
            institutions.append(org_name)
        ss = institutions.index(org_name) + 1
        if "," in name:
            names = name.split(",")
            p["coauthors"] = []
            for name in names:
                p["coauthors"] = [{"name": name.strip(), "ss": ss}]
        else:
            p["coauthors"] = [{"name": name, "ss": ss}]
    if reg["Abstract Co-Author's Name2"]:
        name = reg["Abstract Co-Author's Name2"]
        org_name = reg["Co-Author's Institution2"]
        if org_name == "Other":
            org_name = ""
            # org_name = reg["Co-Author's Institution - Other2"]
        if org_name not in institutions:
            institutions.append(org_name)
        ss = institutions.index(org_name) + 1
        p["coauthors"].append({"name": name, "ss": ss})


def prep_registration(reg):
    p = {}
    p["first_name"] = reg["First Name"]
    p["last_name"] = reg["Last Name"]
    p["affiliation"] = clean_string(reg["Home Institution"])
    if p["affiliation"] == "Other":
        # p["affiliation"] = clean_string(reg["Home  affiliation - Other"])
        p["affiliation"] = ""
    p["research_program"] = clean_string(reg["Undergraduate Research Program"])
    p["reg_type"] = reg["Type of Registration"]
    # p["judge"] = reg["Judge"] == "Yes"
    if (
        p["research_program"] == "Other (Please list below)"
        or p["research_program"] == "Other"
    ):
        p["research_program"] = clean_string(
            reg["Undergraduate Research Program"]
        )
    if registration["Presenter"] == "Presenter":
        p["presenting"] = reg["presentation preference"]
        if "P" in p["presenting"]:
            p["poster_number"] = int(
                re.findall(r"(?<=P)\d+", reg["presentation preference"])[0]
            )
        if "T" in p["presenting"]:
            p["talk_number"] = int(
                re.findall(r"(?<=T)\d+", reg["presentation preference"])[0]
            )
        # p["number"] = int(reg["presentation preference"][1:])

        # if "Oral" in registration["presentation preference"]:
        #     p["presenting"] = "T"
        #     p["number"] = int(
        #         registration["presentation preference"].split()[1].replace("T", "")
        #     )
        prep_presentation(p, reg)
    else:
        p["presenting"] = reg["presentation preference"]
        if "P" in p["presenting"]:
            p["poster_number"] = int(
                re.findall(r"(?<=P)\d+", reg["presentation preference"])[0]
            )
        if "T" in p["presenting"]:
            p["talk_number"] = int(
                re.findall(r"(?<=T)\d+", reg["presentation preference"])[0]
            )
    return p


if __name__ == "__main__":
    registrations = []
    with open("registration.csv", "r", encoding="utf-8-sig") as csvfile:
        csvreader = csv.DictReader(csvfile, dialect="excel")
        for row in csvreader:
            registrations.append(row)

    attendees = []
    for registration in registrations:
        attendees.append(prep_registration(registration))

    poster_index = 1
    for a in attendees:
        if a.get("presenting", "") == "P":
            a["presentation_type"] = "P"
            a["number"] = poster_index
            poster_index += 1
        elif a.get("presenting", "") == "T":
            a["presentation_type"] = "T"

    # from http://eosrei.net/articles/2015/11/latex-templates-python-and-jinja2-generate-pdfs
    latex_jinja_env = jinja2.Environment(
        block_start_string="\BLOCK{",
        block_end_string="}",
        variable_start_string="\VAR{",
        variable_end_string="}",
        comment_start_string="\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=False,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.abspath(".")),
    )

    presentations = list(filter(lambda x: "P" in x["presenting"], attendees))
    for p in presentations:
        p["number"] = p["poster_number"]
    template = latex_jinja_env.get_template("poster_template.tex")
    even_presentations = list(
        filter(lambda x: x["poster_number"] % 2 == 0, presentations)
    )
    odd_presentations = list(
        filter(lambda x: x["poster_number"] % 2 == 1, presentations)
    )
    even_presentations.sort(key=lambda x: x["poster_number"])
    odd_presentations.sort(key=lambda x: x["poster_number"])
    with open("latex/even_poster_session.tex", "w") as f:
        f.write(
            template.render(
                presentations=even_presentations,
                session_type="P",
                session_times="12:15 pm  --  1:15 pm",
                session_name="Poster Session II / even number posters",
            )
        )
    with open("latex/odd_poster_session.tex", "w") as f:
        f.write(
            template.render(
                presentations=odd_presentations,
                session_type="P",
                session_times="10:30 am  --  11:30 am",
                session_name="Post Session I / odd number posters",
            )
        )

    presentations = list(filter(lambda x: "T" in x["presenting"], attendees))
    for p in presentations:
        p["number"] = p["talk_number"]
    template = latex_jinja_env.get_template("poster_template.tex")
    even_presentations = list(
        filter(lambda x: x["talk_number"] % 2 == 0, presentations)
    )
    odd_presentations = list(filter(lambda x: x["talk_number"] % 2 == 1, presentations))
    even_presentations.sort(key=lambda x: x["talk_number"])
    odd_presentations.sort(key=lambda x: x["talk_number"])
    with open("latex/even_talk_session.tex", "w") as f:
        f.write(
            template.render(
                presentations=even_presentations,
                session_type="T",
                session_times="1:15 pm  --  2:45 pm",
                session_name="Talk Session II / even number talks",
            )
        )
    with open("latex/odd_talk_session.tex", "w") as f:
        f.write(
            template.render(
                presentations=odd_presentations,
                session_type="T",
                session_times="8:45 am  --  10:15 am",
                session_name="Talk Session I / odd number talks",
            )
        )

    for a in attendees:
        if "P" in a.get("presenting", "") and "T" in a.get("presenting", ""):
            a["activities"] = f"T{a['talk_number']} Oral, P{a['poster_number']} Poster"
        elif "P" in a.get("presenting", ""):
            a["activities"] = f"P{a['poster_number']} Poster"
        elif "T" in a.get("presenting", ""):
            a["activities"] = f"T{a['talk_number']} Oral"
        elif a["reg_type"] == "Undergraduate":
            a["activities"] = "Non-Presenter"
        else:
            a["activities"] = a["reg_type"]
            # if a["judge"]:
            #     if len(a["activities"]) > 0:
            #         a["activities"] += "/Judge"
            #     else:
            #         a["activities"] += "Judge"

    template = latex_jinja_env.get_template("index_template.tex")
    with open("latex/index.tex", "w") as f:
        f.write(template.render(attendees=attendees))
