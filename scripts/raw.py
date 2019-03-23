#!/usr/bin/env python3
# coding : utf-8
import json
import os
import csv
import requests
from bs4 import BeautifulSoup as bs
from random import shuffle
# import pymongo
from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client.vrai_debat
themes = db.themes
proposal_urls = db.proposal_urls
proposals = db.proposals
arguments = db.arguments
users = db.users
votes = db.votes

ROOT_URL = "https://le-vrai-debat.fr"

URLS = [
    "https://le-vrai-debat.fr/project/democratie-institutions-referendum-dinitiative-citoyenne/consultation/consultation/types/democratie-institutions-referendum-dinitiative-citoyenne",
    "https://le-vrai-debat.fr/project/transition-ecologique-solidaire-agriculture-alimentation/consultation/consultation-2/types/transition-ecologique-et-solidaire-agriculture-alimentation-transport",
    "https://le-vrai-debat.fr/project/justice-police-armee/consultation/consultation-3/types/justice-police-armee",
    "https://le-vrai-debat.fr/project/europe-affaires-etrangeres-outre-mer/consultation/consultation-4/types/europe-affaires-etrangeres-outre-mer",
    "https://le-vrai-debat.fr/project/sante-solidarite-handicap/consultation/consultation-5/types/sante-solidarite-handicap",
    "https://le-vrai-debat.fr/project/economie-finances-travail-compte-public/consultation/consultation-6/types/economie-finances-travail-compte-public",
    "https://le-vrai-debat.fr/project/education-jeunesse-enseignement-superieur-recherche-et-innovation/consultation/consultation-7/types/education-jeunesse-enseignement-superieur-recherche-et-innovation",
    "https://le-vrai-debat.fr/project/sport-culture/consultation/consultation-8/types/sport-culture",
    "https://le-vrai-debat.fr/project/expression-libre/consultation/consultation-9/types/expression-libre"
]

def store_theme()
def store_urls(theme):
    for page_nb in range(1, theme["page_nb"]+1):
        page_url = "{}page/{}".format(theme["url"], page_nb)
        r = requests.get(page_url)
        print(r)
        # with open(page_name, "w") as fo:
        #     fo.write(r.text)
        soup = bs(r.text, "lxml")
        urls_p = [ s.h3.a.get("href") for s in soup.findAll("div", {"class": "opinion__body"})]
        # urls_proposals.extend(urls_p)
        for u in urls_p:
            f.write(u+"\n")

def collect_proposal(parameters, theme_nb = None):
    # print(parameters)
    if theme_nb is None: 
        for slug, theme in parameters.items():
            with open(os.path.join("proposal_urls", slug+"-mixed.csv"), "w") as f:
                w = csv.writer(os.path.join("raw", slug+".csv"))
                # page_nbs = random(xrange(1, theme["page_nb"]+1)
                for page_nb in range(1, theme["page_nb"]+1):
                    page_url = "{}page/{}".format(theme["url"], page_nb)
                    r = requests.get(page_url)
                    print(r)
                    # with open(page_name, "w") as fo:
                    #     fo.write(r.text)
                    soup = bs(r.text, "lxml")
                    urls_p = [ s.h3.a.get("href") for s in soup.findAll("div", {"class": "opinion__body"})]
                    # urls_proposals.extend(urls_p)
                    for u in urls_p:
                        f.write(u+"\n")
    else:
        count = 0
        # urls_proposals = []
        for slug, theme in parameters.items():
            count = count+1
            if count == theme_nb:
                with open(os.path.join("proposal_urls", slug+"-raw2.csv"), "w") as f:
                    for page_nb in range(1, theme["page_nb"]+1):
                        # page_name = os.path.join("raw", slug, "{}.html".format(page_nb))
                        page_url = "{}page/{}".format(theme["url"], page_nb)
                        r = requests.get(page_url)
                        
                        # with open(page_name, "w") as fo:
                        #     fo.write(r.text)
                        soup = bs(r.text, "lxml")
                        urls_p = [ s.h3.a.get("href") for s in soup.findAll("div", {"class": "opinion__body"})]
                        # urls_proposals.extend(urls_p)
                        for u in urls_p:
                            f.write(u+"\n")

def load_parameters():
    with open("parameters.json", "r") as f:
        data = json.load(f)
    return data

def load_proposal_page(url):
    wget.ROOT_URL+url

def extract_proposals():
    
if __name__ == "__main__":
    # build_parameters()
    parameters = load_parameters()
    # # verify_proposal_count(parameters)
    collect_proposal(parameters)