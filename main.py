#!/usr/bin/env python3
# coding : utf-8

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import csv
import os

__doc__ = '''
Extraction des propositions issues du site https://le-vrai-debat.fr/
* 9 thèmes
La première extraction consiste à lister toutes les urls des propositions par page
La deuxième consiste à extraire le texte de chacune des propositions
'''


# Extraction des données issues du vrai débat 9 thèmes
ROOT_URL = "https://le-vrai-debat.fr"

parameters = {
    "democratie-institutions":
        {
            "url": "https://le-vrai-debat.fr/project/democratie-institutions-referendum-dinitiative-citoyenne/consultation/consultation/types/democratie-institutions",
            "totalCount": 3807,
            "pageNb": 381,
        },
    "transition-ecologique-solidaire-agriculture-alimentation":
        {
            "url": "https://le-vrai-debat.fr/project/transition-ecologique-solidaire-agriculture-alimentation/consultation/consultation-2/types/transition-ecologique-et-solidaire-agriculture-alimentation-transport",
            "totalCount": 3155,
            "pageNb": 316,
        },
    "justice-police-armee":
        {
            "url": "https://le-vrai-debat.fr/project/justice-police-armee/consultation/consultation-3/types/justice-police-armee",
            "totalCount": 1420,
            "pageNb": 142,
        },
    "europe-affaires-etrangeres-outre-mer":
        {
            "url": "https://le-vrai-debat.fr/project/europe-affaires-etrangeres-outre-mer/consultation/consultation-4/types/europe-affaires-etrangeres-outre-mer",
            "totalCount": 905,
            "pageNb": 91,
        },
    "sante-solidarite-handicap":
        {
            "url": "https://le-vrai-debat.fr/project/europe-affaires-etrangeres-outre-mer/consultation/consultation-5/types/sante-solidarite-handicap",
            "totalCount": 1820,
            "pageNb": 182,
        },
    "economie-finances-travail-compte-public":
        {
            "url":"https://le-vrai-debat.fr/project/economie-finances-travail-compte-public/consultation/consultation-6/types/economie-finances-travail-compte-public",
            "totalCount":6146,
            "pageNb":615
        },
    "education-jeunesse-enseignement-superieur-recherche-et-innovation":
        {
            "url":"https://le-vrai-debat.fr/project/education-jeunesse-enseignement-superieur-recherche-et-innovation/consultation/consultation-7/types/education-jeunesse-enseignement-superieur-recherche-et-innovation",
            "totalCount":1507,
            "pageNb":151
        },
    "sport-culture":
        {
            "url":"https://le-vrai-debat.fr/project/sport-culture/consultation/consultation-8/types/sport-culture",
            "totalCount":566,
            "pageNb":57
        },
    "expression-libre":
        {
            "url":"https://le-vrai-debat.fr/project/expression-libre/consultation/consultation-9/types/expression-libre-sujets-de-societe",
            "totalCount":3589,
            "pageNb":359
        }
}

def get_proposal_url(soup):
    '''Recupérer seulement l'url de la proposition'''
    return [ROOT_URL+soup.h3.a.get("href")]

def get_proposal_ref(soup):
    '''Etant donné un élément html d'une liste extraire les références de la proposition'''
    author = {"name":soup.p.a.text, "url":soup.p.a.get("href")}
    created_date = soup.p.text.split(" • ")[1].strip()
    stats = dict(zip(["votes", "amendements", "arguments","sources"] , [n.strip for n in soup.find("p", {"class":"opinion__votes"}).text.split(" • ")]))
    proposal = {"author":author, "url": soup.h3.a.get("href"), "title":soup.h3.a.text.strip(), "date": created_date, "stats": stats}
    return proposal

def extract_by_page(driver, url, page_nb):
    page_url = url+"/page/{}".format(page_nb)
    # try:
    driver.get(page_url)
    source = driver.page_source
    soup = bs(source, "lxml")
    # except TimeoutException:
    #     pass    
    return map(get_proposal_url, soup.findAll("div", {"class":"opinion__body"})) 

def extract_content_proposal():
    pass


if __name__ == "__main__":
    options = webdriver.FirefoxOptions()
    options.binary_location = '/usr/bin/firefox'
    options.add_argument('-headless')
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Firefox(options=options)
    for theme_name, theme in parameters.items():
        print(theme["url"], theme["pageNb"])
        counter = 0
        with open(theme_name+"-2.csv", "w") as f:
            w = csv.writer(f)
            offset = theme["totalCount"]//10
            if theme["totalCount"]%10 > 0:
                offset +=1
            for page_nb in range(1, offset+1):
                w.writerows(extract_by_page(driver, theme["url"], page_nb))
    driver.close()
