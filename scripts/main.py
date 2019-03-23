#!/usr/bin/env python3
# coding : utf-8
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import csv
import os
import json

__doc__ = '''
Extraction des propositions issues du site https://le-vrai-debat.fr/
* 9 thèmes
La première extraction consiste à lister toutes les urls des propositions par page
La deuxième consiste à extraire le texte de chacune des propositions
'''


# Extraction des données issues du vrai débat 9 thèmes
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


def get_theme_info(url):
    '''A partir d'une url de consultation récupérer les informations statistiques du thème correspondant'''
    headers = {
        "Host":"le-vrai-debat.fr",
        "Referer": "https://le-vrai-debat.fr/",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linu…) Gecko/20100101 Firefox/65.0"}
    r = requests.get(url, headers)
    print(r)
    slug = url.split(
        "/consultation/")[0].replace("https://le-vrai-debat.fr/project/", "")
    soup = bs(r.text, "lxml")
    name = soup.h1.text.strip()
    info = soup.find("span", {"class":"excerpt"})
    author = {"name": info.a.text, "url":info.a.get("href")}
    contributions = int(soup.find(
        "li", id="contributions-counter-pill").find("span", {"class": "value"}).text)
    votes = soup.find(
        "li", id="votes-counter-pill").find("span", {"class": "value"}).text
    contributors = soup.find(
        "li", id="contributors-counter-pill").find("span", {"class": "value"}).text
    page_offset = contributions//10
    if contributions % 10 != 0:
        page_offset += 1

    return {
        slug : {
        "name": name,
        "slug": slug,
        "url": url,
        "author": author,
        "date": info.text.split(",")[1].strip(),
        "nb_contributions": int(contributions),
        "nb_votes": int(votes),
        "nb_participants": int(contributors),
        "page_nb": page_offset
    }}

def build_parameters():
    data = {}
    for url in URLS:
        data.update(get_theme_info(url))
    with open("parameters.json", "w") as f:
        json.dump(data, f)

def load_parameters():
    with open("parameters.json", "r") as f:
        data = json.load(f)
        
    return data

def get_proposal_url(soup):
    '''Recupérer seulement l'url de la proposition'''
    return [ROOT_URL+soup.h3.a.get("href")]


def get_proposal_ref(soup):
    '''Etant donné un élément html d'une liste extraire les références de la proposition'''
    author = {"name": soup.p.a.text, "url": soup.p.a.get("href")}
    created_date = soup.p.text.split(" • ")[1].strip()
    stats = dict(zip(["votes", "amendements", "arguments", "sources"], [
                 n.strip for n in soup.find("p", {"class": "opinion__votes"}).text.split(" • ")]))
    proposal = {"author": author, "url": soup.h3.a.get(
        "href"), "title": soup.h3.a.text.strip(), "date": created_date, "stats": stats}
    return proposal


def extract_by_page(url, page_nb):
    # try:
    options = webdriver.FirefoxOptions()
    options.binary_location = '/usr/bin/firefox'
    options.add_argument('-headless')
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Firefox(options=options)
    page_url = url+"/page/{}".format(page_nb)
    driver.get(page_url)
    source = driver.page_source
    soup = bs(source, "lxml")
    driver.close()
    data = []
    for i in soup.findAll("div", {"class": "opinion__body"}):
        data.append(get_proposal_url(i))
    return map(get_proposal_url, soup.findAll("div", {"class": "opinion__body"}))
    # return data

def extract_content_proposal(soup):
    author_block = soup.find("div", {"class": "opinion__user"})
    title = soup.find("h3").text
    stats_block = [n.text.strip() for n in soup.find("ul").findAll("span")]
    opinion_description = "\n---\n".join([n.text.strip()
                                          for n in soup.findAll("div", {"class": 'opinion__description'})])
    # opinion_block = soup.find("div", {"class":"opinion__appendix__content"}).text.strip()
    votes = [n.text for n in soup.find("table").findAll("td")]
    actions_block = soup.find("ul", {"role": "tablist"})
    arguments_pour_block = soup.find("div", id="arguments-col--FOR")
    arguments_contre_block = soup.find("div", id="arguments-col--AGAINST")
    amendements_block = soup.find("div", id="versions-list")
    sources_block = soup.find("div", id="sources-list")



def collect_proposal(parameters, theme_nb = None):
    # options = webdriver.ChromeOptions()
    # options.binary_location = '/snap/bin/chromium/'
    # 
    #  driver = webdriver.Chrome(options=options)
    if theme_nb is None: 
        for slug, theme in parameters.items():
            with open(os.path.join("proposal_urls", slug+".csv"), "w") as f:
                w = csv.writer(f)
                for page_nb in range(1, theme["page_nb"]+1):
                    w.writerows(extract_by_page(theme["url"], page_nb))
    else:
        count = 0
        for slug, theme in parameters.items():
            count = count+1
            if count == theme_nb:
                with open(os.path.join("proposal_urls", slug+".csv"), "w") as f:
                    w = csv.writer(f)
                    for page_nb in range(1, theme["page_nb"]+1):
                        print(extract_by_page(theme["url"], page_nb))
                        w.writerows(extract_by_page(theme["url"], page_nb))
    # driver.close()
    return 

def verify_proposal_count(parameters):
    with open("propasals-scrapping-stats.csv", "w") as f:
        header = ["THEME", "CONTRIBUTIONS_NB", "RESULTS_NB", "MISSING", "PAGE_NB_TO_START"]
        f.write("\t".join(header)+'\n')
        for theme_name, theme in parameters.items():
            try:
                with open(os.path.join("proposal_urls", theme_name+".csv"), "r") as fi:
                    result_nb = len(fi.readlines())
                row = [theme_name, str(theme["nb_contributions"]), str(result_nb), str(theme["nb_contributions"]-result_nb), str((result_nb/10)+1)]
                f.write("\t".join(row)+'\n')
            except FileNotFoundError:
                row = [theme_name, str(theme["nb_contributions"]), "0", str(theme["nb_contributions"]), "1"]
                f.write("\t".join(row)+'\n')
            
if __name__ == "__main__":
    build_parameters()
    parameters = load_parameters()
    # verify_proposal_count(parameters)
    collect_proposal(parameters, 2)