#!/usr/bin/env python3
# coding : utf-8

import json
# import pickle
import os
import csv
import requests
import time
from bs4 import BeautifulSoup as bs
import pymongo
from pymongo import MongoClient
import random
# from random import shuffle
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

ROOT_URL = "https://le-vrai-debat.fr"

URLS = [
    "https://le-vrai-debat.fr/project/democratie-institutions-referendum-dinitiative-citoyenne/consultation/consultation/types/democratie-institutions/page/1",
    "https://le-vrai-debat.fr/project/transition-ecologique-solidaire-agriculture-alimentation/consultation/consultation-2/types/transition-ecologique-et-solidaire-agriculture-alimentation-transport/page/1",
    "https://le-vrai-debat.fr/project/justice-police-armee/consultation/consultation-3/types/justice-police-armee/page/1",
    "https://le-vrai-debat.fr/project/europe-affaires-etrangeres-outre-mer/consultation/consultation-4/types/europe-affaires-etrangeres-outre-mer/page/1",
    "https://le-vrai-debat.fr/project/sante-solidarite-handicap/consultation/consultation-5/types/sante-solidarite-handicap/page/1",
    "https://le-vrai-debat.fr/project/economie-finances-travail-compte-public/consultation/consultation-6/types/economie-finances-travail-compte-public/page/1",
    "https://le-vrai-debat.fr/project/education-jeunesse-enseignement-superieur-recherche-et-innovation/consultation/consultation-7/types/education-jeunesse-enseignement-superieur-recherche-et-innovation/page/1",
    "https://le-vrai-debat.fr/project/sport-culture/consultation/consultation-8/types/sport-culture/page/1",
    "https://le-vrai-debat.fr/project/expression-libre/consultation/consultation-9/types/expression-libre-sujets-de-societe/page/1"
]


def request_page(url):
    '''
    load page using request return raw content response
    '''
    headers = {
        "Host": "le-vrai-debat.fr",
        "Referer": "https://le-vrai-debat.fr/",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linu…) Gecko/20100101 Firefox/65.0"}
    r = requests.get(url, headers)
    return r.text


def load_page(url):
    '''
    charger la page a l'aide du navigateur
    selenium.common.exceptions.WebDriverException: Message: 'geckodriver' executable needs to be in PATH.
    avant lancement du script ajouter le chemin vers le  geckodriver téléchargé dans la ligne de commande
    export PATH=$PATH:~/accounts/
    return l'objet driver
    '''
    options = webdriver.FirefoxOptions()
    options.binary_location = '/usr/bin/firefox'
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    return driver


def get_item(soup):
    return {
        "id": soup.get("id"),
        "date": soup.find("p", {"class": "opinion__date"}).text.strip(),
        "text": soup.find("p", {"class": "opinion__text"}).text.strip(),
        "votes": int(soup.find("span", {"class": "opinion__votes-nb"}).text.strip()),
        "author": {
            "name": soup.find("p", {"class": "opinion__user"}).a.text,
            "url": soup.find("p", {"class": "opinion__user"}).a.get("href")
        },
    }


def get_argument(soup, opinion):
    return {
        "id": soup.get("id"),
        "date": soup.find("p", {"class": "opinion__date"}).text.strip().replace("\n", "").replace("\'", " "),
        "text": soup.find("p", {"class": "opinion__text"}).text.strip().replace("\n", "").replace("\'", " "),
        "votes": int(soup.find("span", {"class": "opinion__votes-nb"}).text.strip()),
        "author": {
            "name": soup.find("p", {"class": "opinion__user"}).a.text,
            "url": soup.find("p", {"class": "opinion__user"}).a.get("href")
        },
        "opinion": opinion
    }


def extract_arguments(soup):
    # print(soup.find_all("div", class_="list-group"))
    args_pour_block = soup.find("div", {
                                "id": "opinion__arguments--FOR"}).find_all("span", {"class": "opinion--argument"})
    args_contre_block = soup.find(
        "div", {"id": "opinion__arguments--AGAINST"}).find_all("span", {"class": "opinion"})
    args_pour = [get_argument(a, 1) for a in args_pour_block]
    args_contre = [get_argument(b, -1) for b in args_contre_block]
    return list(args_pour + args_contre)
    # "opinion--argument"})]
    # print([n for n in args_pour][0:5])
    # args = [n.get("id") for n in args_pour_block.find_all(
    #     )]
    # print(len(args))
    # args = [n.get("id") for n in args_contre_block.find_all(
    #     "span", {"class": "opinion--argument"})]
    # print(len(args))
    # print(len(args_pour_block.find_all("span",{"class":"opinion--argument"})))


def extract_sources(soup):
    source_block = soup.find("div", {
                             "id": "sources-list"}).find_all("span", {"class": "list-group-item__opinion"})
    return list(map(get_item, source_block))


def extract_versions(soup):
    version_block = soup.find("div", {
                              "id": "versions-list"}).find_all("span", {"class": "list-group-item__opinion"})
    return list(map(get_item, version_block))


def store_proposal_pages():
    for theme in db.themes.find({}):
        print(theme["slug"])
        print(theme["nb"])
        print(theme["pages"])
        store_next_urls(theme)


def extract_profile(author):
    '''extract data activity from user profile'''
    r = requests.get(author["url"])
    soup = bs(r.text, "lxml")
    activity_block = soup.find("div", {"class": "profile__values"})
    labels = [n.text.strip().lower() for n in activity_block.find_all(
        "h2", {"class": "profile__value__label"})]
    values = [int(n.text.strip()) for n in activity_block.find_all(
        "p", {"class": "profile__value__number"})]
    stats = {
        "contributions": 0,
        "propositions": 0,
        "commentaires": 0,
        "arguments": 0,
        "sources": 0,
        "votes": 0
    }
    stats.update(dict(zip(labels, values)))
    author.update(stats)
    stats = {
        "stats": stats,
        "arguments": get_arguments(author),
        "propositions": [n for n in get_proposals(author)],
        "votes": get_votes(author)
    }

    author.update(stats)
    return author


def get_arguments(author):
    '''s'affcihe par 5'''
    nb_clicks = author["arguments"]/5
    if nb_clicks % 5 != 0:
        nb_clicks = int(nb_clicks+1)
    else:
         nb_clicks = int(nb_clicks)

    url_args = author["url"]+"/arguments"
    if int(nb_clicks) > 0:
        driver = load_page(url_args)
        cookies = driver.find_element_by_id('cookie-consent')
        cookies.click()
        button_more = driver.find_elements_by_css_selector('button.btn-link')

        for i in range(nb_clicks):
            try:
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                button_more = driver.find_elements_by_css_selector(
                    'button.btn-link')
                button_more[0].click()
                time.sleep(2)
            except selenium.common.exceptions.ElementNotInteractableException:
                break

        source = driver.page_source
        soup = bs(source, "lxml")
        driver.close()

        return list(map(get_arg, soup.find_all("span", {"class": "opinion"})))
    return []

def get_arg(arg):
    return {
        "_id": arg.get("id"),
        "proposition_url": arg.find_all("p")[2].a.get("href"),
        "proposition_titre": arg.find_all("p")[2].a.text,
        "vote": arg.find("span", {"class": "label"}).text.lower(),
        "date": arg.find("p", {"class": "opinion__date"}).text.strip(),
        "texte": arg.find("p", {"class": "opinion__text"}).text.strip()
    }

def get_proposals(author):
    url_args = author["url"]+"/opinions"
    driver = load_page(url_args)
    soup = bs(driver.page_source, "lxml")
    for theme in soup.find_all("div", {"class": "panel-default"}):
        theme = theme.find("div", {"class": "panel-heading"})

        nb_prop_par_theme = int(theme.find("span", {"class": "badge"}).text)
        theme.span.decompose()
        theme_name = theme.text

    for prop in soup.find_all("div", {"class": "opinion__body"}):
        print(prop)
        date = prop.find("div", {"class": "opinion__data"}).find("p")
        print(date)
        titre = prop.find("h3", {"class": "opinion__title"}).text.strip()
        url = prop.find("h3", {"class": "opinion__title"}).get("href")
        stats_block = dict([n.strip().split(" ") for n in prop.find(
            "p", {"class": "opinion__votes"}).text.split("•")])
        stats = {v: int(k.replace(",", ""))
                for k, v in stats_block.items()}
        # repartition des votes
        votes_stats = {
            "d'accord": None,
            "mitigé": None,
                "pas d'accord": None,
                "total": None,
            }
        votes_table = prop.find("table")
        if votes_table is not None:
            votes = [td.text for td in soup.find("table").find_all("td")]
            votes_values = [int(v.replace(",", ""))
                            for i, v in enumerate(votes) if i % 2 != 0]
            votes_labels = [v.lower()
                            for i, v in enumerate(votes) if i % 2 == 0]
            votes_stats["total"] = sum(votes_values)
            votes_stats_x = dict(zip(votes_labels, votes_values))
            votes_stats.update(votes_stats_x)
        yield {
            "url": url,
            "titre": titre,
            # "description": description,
            # "date": date,
            "stats": stats,
            "votes": votes_stats,
            "theme": theme_name,
            "nb_proposition_theme": nb_prop_par_theme
        }


def get_votes(author):
    '''s'affcihe par 5'''
    url_args = author["url"]+"/votes"
    nb_clicks = author["votes"]/5
    if nb_clicks%5 != 0:
        nb_clicks = int(nb_clicks+1)
    else:
         nb_clicks = int(nb_clicks)
    if nb_clicks > 0:
        driver = load_page(url_args)
        time.sleep(3)
        cookies = driver.find_element_by_id('cookie-consent')
        cookies.click()
        button_more = driver.find_elements_by_css_selector('button.btn-link')
         
        for i in range(nb_clicks):
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                button_more = driver.find_elements_by_css_selector('button.btn-link')
                button_more[0].click()
                time.sleep(2)
            except selenium.common.exceptions.ElementNotInteractableException:
                break
        
        soup = bs(driver.page_source, "lxml")
        driver.close()
        return list(map(get_vote, soup.find_all("span", {"class": "opinion"})))
    return []

def get_vote(vote):
    return {
        "vote": vote.find("span", {"class": "label"}).text.lower(),
        "date": vote.find("span", {"class": "opinion__date"}).text.strip(),
        "proposition_url": vote.p.a.get("href"),
        "proposition_titre": vote.p.a.text.strip()
    }   


def get_sources():
    pass


def get_comments():
    pass


if __name__ == "__main__":
    client = MongoClient('localhost', 27017)
    db = client.vrai_debat
    themes = db.themes
    # db.themes.create_index([('nb', pymongo.ASCENDING)], unique=True)
    # pages=db.pages
    db.profile.create_index([('url', pymongo.ASCENDING)], unique=True)

    # store_theme(URLS)
    # store_proposal_pages()
    for prop in db.proposal.find():
        author = prop["auteur"]
        try:
            db.profile.insert(extract_profile(author))
        except pymongo.errors.DuplicateKeyError:
            pass
        print("insert")
        