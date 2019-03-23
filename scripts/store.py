#!/usr/bin/env python3
# coding : utf-8

import json
import os
import csv
import requests
import time
from bs4 import BeautifulSoup as bs
import pymongo
from pymongo import MongoClient
import random
# from random import shuffle
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
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


def get_theme_info(page_url):
    ''' 
    Recupérer les informations liées au theme
    {
        "name": <name>,
        "url": <theme_url>,
        "slug": <slug_theme>,
        "author": {
            {"name": <author_name>, "url": <author_profile_page>}
        },
        "date": <fr_text_date>,
        "nb_contributions": <int(contributions)>,
        "nb_votes": <int(votes)>,
        "nb_participants": <int(contributors)>,
        "nb_propositions": <int(proposals)>,
        "pages": <int(page_offset)>,
        "proposal_pages": <urls>
    }
    '''
    headers = {
        "Host": "le-vrai-debat.fr",
        "Referer": "https://le-vrai-debat.fr/",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linu…) Gecko/20100101 Firefox/65.0"}
    r = requests.get(page_url, headers)
    slug = page_url.split(
        "/consultation/")[0].replace("https://le-vrai-debat.fr/project/", "")
    soup = bs(r.text, "lxml")
    name = soup.h1.text.strip()
    info = soup.find("span", {"class": "excerpt"})
    author = {"name": info.a.text, "url": info.a.get("href")}
    contributions = int(soup.find(
        "li", id="contributions-counter-pill").find("span", {"class": "value"}).text)
    votes = soup.find(
        "li", id="votes-counter-pill").find("span", {"class": "value"}).text
    contributors = soup.find(
        "li", id="contributors-counter-pill").find("span", {"class": "value"}).text
    proposals = soup.find(
        "div", {"class": "opinion__header__title"}).text.strip().split(" ")[0]
    proposals = int(proposals)
    page_offset = int(proposals/10)
    if proposals % 10 != 0:
        page_offset += 1
    # page1
    urls = [s.h3.a.get("href")
            for s in soup.findAll("div", {"class": "opinion__body"})]
    return {
        "name": name,
        "url": page_url.split("page")[0],
        "slug": slug,
        "author": author,
        "date": info.text.split(",")[1].strip(),
        "nb_contributions": int(contributions),
        "nb_votes": int(votes),
        "nb_participants": int(contributors),
        "nb_propositions": int(proposals),
        "pages": int(page_offset),
        "proposal_pages": urls
    }


def store_theme(URLS):
    '''inserer le theme dans la  base de données'''
    count = 0
    for theme in map(get_theme_info, URLS):
        count = count + 1

        theme["nb"] = count

        for u in theme["proposal_pages"]:
            try:
                db.pages.insert(
                    {"url": ROOT_URL+u, "theme": theme["nb"], "page": 1})
            except pymongo.errors.DuplicateKeyError:
                break
        del theme["proposal_pages"]
        try:
            db.themes.insert(theme)
        except pymongo.errors.DuplicateKeyError:
            pass
    return


def insert_proposal_page(url, page_nb):
    '''
    Insérer dans la base de données dans la table/collection pages l'url, 
    le theme associé et le numero de la page
    '''
    url = "{}page/{}".format(url, page_nb)
    print(url)
    for u in get_proposal_url(url):
        # print(u)
        try:
            # print(u.split("opinions")[1], page_nb)
            
            db.pages.insert(
                {"url": ROOT_URL+u, "theme": theme["nb"], "page": page_nb})
        except pymongo.errors.DuplicateKeyError:
            pass
        except:
            pass


def get_proposal_url(url):
    '''extraire les différentes pages dédiées à une proposition a partir d'une page qui les listent'''
    r = requests.get(url)
    # print(r)
    soup = bs(r.text, "lxml")
    # print(soup.text)
    # print(soup.findAll("div", {"class": "opinion__body"}))
    return [s.h3.a.get("href") for s in soup.findAll("div", {"class": "opinion__body"})]


def store_next_urls(theme):
    '''générer et insérer les pages des proposition'''
    pages_nb = list(range(0, int(theme["pages"])+1))
    # for page_nb in random.sample(pages_nb, len(pages_nb)):
    for page_nb in reversed(pages_nb):
        print(page_nb)
        url = "{}page/{}".format(theme["url"], page_nb)
        # print(url)

        for u in get_proposal_url(url):
            try:
                # print(u.split("opinions")[1], page_nb)
                print(u)
                db.pages.insert(
                    {"url": ROOT_URL+u, "theme": theme["nb"], "page": page_nb})
            except pymongo.errors.DuplicateKeyError:
                print("done")
                break
            except:
                break


def load_page(url):
    '''
    charger la page a l'aide du navigateur
    selenium.common.exceptions.WebDriverException: Message: 'geckodriver' executable needs to be in PATH. 
    avant lancement du script ajouter le chemin vers le  geckodriver téléchargé dans la ligne de commande
    export PATH=$PATH:~/accounts/
    '''
    options = webdriver.FirefoxOptions()
    options.binary_location = '/usr/bin/firefox'
    # options.add_argument('-headless')
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    
    cookies = driver.find_element_by_id('cookie-consent')
    cookies.click()
    try:
        vote_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "opinion-votes-show-all"))
        )
    finally:
        
    # votes = driver.find_element_by_id("opinion-votes-show-all")
        vote_btn.click()
        driver.switchTo().activeElement()
    # time.sleep(3)
        source = driver.page_source
        soup = bs(source, "lxml")
    
    #click_more_arguments(driver, soup)
    # args = soup.find_all("span", {"class":"opinion--argument"})
    # if len(args) == 0:
    #     return None
    # else:
        driver.close()
        return soup
def get_votes_details():
    pass


def click_more_arguments(driver, soup):
    cookies = driver.find_element_by_id('cookie-consent')
    cookies.click()
    btn_info = soup.find_all("button", class_="btn-link")
    button_more = driver.find_elements_by_css_selector('button.btn-link')
    #button pour,contre
    index_btn = [i for i,n in enumerate(btn_info) if n.text == "Voir plus"]
    print(btn_info, len(btn_info), len(button_more))
    
    args_pour_nb = soup.find(
        "div", {"id": "opinion__arguments--FOR"}).h4.text.split(" ")[0]
    args_contre_nb = soup.find(
        "div", {"id": "opinion__arguments--AGAINST"}).h4.text.split(" ")[0]
    arg_stats = {
        "pour": int(args_pour_nb),
        "contre": int(args_contre_nb),
        "total": int(args_pour_nb)+int(args_contre_nb)
    }
    print(arg_stats)
    #arguments
    nb_click_pour = int(arg_stats["pour"] / 25)
    nb_click_contre = int(arg_stats["contre"] / 25)
    # essai d'extraction des arguments
    # print(nb_click_contre, nb_click_pour)
    # element = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.ID, "myDynamicElement"))
    # )
    # if nb_click_pour > nb_click_contre:
    #     nb_click = nb_click_pour
    # else:
    #     nb_click = nb_click_contre
    # for i in range(nb_click):
    #     try:
    #         # driver.execute_script("arguments[0].scrollIntoView();",button_more[index_btn[0]])
    #         button_more[index_btn[0]].click()
    #         # driver.execute_script("arguments[0].scrollIntoView();",button_more[index_btn[1]])
    #         button_more[index_btn[1]].click()
            
    #     except StaleElementReferenceException:
    #         pass
            # time.sleep(3)
            # WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.css_selector, "button.btn-click']")));
            # driver.execute_script("arguments[0].scrollIntoView();",button_more[index_btn[0]])
            # button_more[index_btn[0]].click()
            # driver.execute_script("arguments[0].scrollIntoView();",button_more[index_btn[1]])
            # button_more[index_btn[1]].click()
            
            # button_more[index_btn[1]].click()
            # # fastrack.click()
            # # from selenium.webdriver.common.action_chains import ActionChains
            # element= driver.find_elements_by_css_selector('button.container')
            
            
            # driver.find_element_by_tag_name('body').send_keys(Keys.HOME)
            # button_more[index_btn[0]].click()
            # button_more[index_btn[1]].click()
            
            # button_more[index_btn[1]].click()
    # for i in range(nb_click_pour+1):
    #     button_more[index_btn[0]].click()
    #     button_more[index_btn[1]].click()
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # try:
    #     for i in range(nb_click_contre+1):
    #         button_more[index_btn[1]].click()
    # except:
    #     #selenium.common.exceptions.StaleElementReferenceException
    #     pass
    # try:
    #     for i in range(nb_click_pour+1):
    #         button_more[index_btn[0]].click()
    # except:
    #     #selenium.common.exceptions.StaleElementReferenceException
    #     pass
    return driver
    
def get_proposal(soup):
    '''extraire les informations relative à la proposition'''
    author_block = soup.find("div", {"class": "opinion__user"})
    author = {"name": author_block.a.text, "url": author_block.a.get("href")}
    created_date = author_block.findAll("span")[1].get("title")
    title = soup.find("h3", {"class": "title"}).text.strip()
    stats_block = soup.find(
        "li", {"class": "list-group-item__opinion"}).find("ul", {"class": "excerpt"}).findAll("li")
    # print(stats_block)
    votes_table = soup.find("table")
    if votes_table is None:
        votes_stats = {}
    else:
        votes = [td.text for td in soup.find("table").find_all("td")]
        votes_nb = [int(v.replace(",", ""))
                    for i, v in enumerate(votes) if i % 2 != 0]
        # votes_total = sum(votes_nb)
        votes_labels = [v for i, v in enumerate(votes) if i % 2 == 0]
        votes_stats = dict(zip(votes_labels, votes_nb))
        votes_stats["total"] = sum(votes_nb)
    
    arguments_stats = { "pour": 0, "contre":0, "total":0} 
    args_pour_nb = soup.find(
        "div", {"id": "opinion__arguments--FOR"}).h4.text.split(" ")[0]
    args_contre_nb = soup.find(
        "div", {"id": "opinion__arguments--AGAINST"}).h4.text.split(" ")[0]
    arguments_stats = {
        "pour": int(args_pour_nb),
        "contre": int(args_contre_nb),
        "total": int(args_pour_nb)+int(args_contre_nb)
    }
    
    stats = dict(zip(["votes", "amendements", "arguments", "sources"],
                     [int(n.span.text.split(" ")[0].replace("\u202f", "")) for n in stats_block]))
    # stats = dict(zip(["votes", "amendements", "arguments", "sources"], [
    #              stats_block.split(" • ")]))
    desc_multiple = soup.find_all("div", {"class": "opinion__description"})
    try:
        desc_multiple[1].button.decompose()
        desc_multiple[1].find("div", {"class": "opinion__votes__box"}).decompose()
        desc_multiple[1].find("div", {"class": "opinion__buttons"}).decompose()
        desc = "\n---\n".join([desc.text.strip() for desc in desc_multiple]).replace("Bénéfices apportés", "")
    except IndexError:
        desc = "\n---\n".join([desc.text.strip() for desc in desc_multiple]).replace("Bénéfices apportés", "")
        pass
    print(soup.find_all("opinion__votes__more__modal"))
    votes_users = [
        {
            "url":block.a.get("href"), 
            "name":block.a.text, 
            "contributions_nb":block.find("p", {"class":"excerpt"})
        } for block in soup.find_all("opinion__votes__more__modal")]
    
    proposal = {
        "author": author,
        "url": soup.h3.a.get("href"),
        "title": title,
        "description": desc.replace("\n", "").replace("\\'", " "),
        "date": created_date,
        "stats": stats,
        "stats_details": {
            "votes": votes_stats, 
            "arguments": arguments_stats
            # "sources": votes_sources
        },
        "votes": votes_users

        # "arguments":extract_arguments(soup),
        # "sources": extract_sources(soup),
        # "amendements": extract_versions(soup)
    }
    return proposal

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
    args_pour_block=soup.find("div", {"id": "opinion__arguments--FOR"}).find_all("span", {"class":"opinion--argument"})
    args_contre_block=soup.find("div", {"id": "opinion__arguments--AGAINST"}).find_all("span", {"class":"opinion"})
    args_pour = [get_argument(a, 1) for a in args_pour_block]
    args_contre = [get_argument(b, -1) for b in args_contre_block]
    return list(args_pour + args_contre)
    #"opinion--argument"})]
    # print([n for n in args_pour][0:5])
    # args = [n.get("id") for n in args_pour_block.find_all(
    #     )]
    # print(len(args))
    # args = [n.get("id") for n in args_contre_block.find_all(
    #     "span", {"class": "opinion--argument"})]
    # print(len(args))
    # print(len(args_pour_block.find_all("span",{"class":"opinion--argument"})))

def extract_sources(soup):
    source_block = soup.find("div", {"id":"sources-list"}).find_all("span", {"class":"list-group-item__opinion"})
    return list(map(get_item, source_block))

def extract_versions(soup):
    version_block = soup.find("div", {"id":"versions-list"}).find_all("span", {"class":"list-group-item__opinion"})
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
    activity_block = soup.find("div", {"class":"profile__values"})
    labels = [n.text for n in activity_block.find_all("h2", {"class":"profile__value__label"})]
    values = [n.text for n in activity_block.find_all("p", {"class":"profile__value__number"})]
    print(zip(labels, values))
    stats = {
        "contributions":0,
        "propositions": 0,
        "commentaires": 0,
        "arguments": 0,
        "sources":0,
        "votes": 0
    }

    
if __name__ == "__main__":
    client=MongoClient('localhost', 27017)
    db=client.vrai_debat
    themes=db.themes
    # db.themes.create_index([('nb', pymongo.ASCENDING)], unique=True)
    # pages=db.pages
    # db.pages.create_index([('url', pymongo.ASCENDING)], unique=True)

    # store_theme(URLS)
    # store_proposal_pages()
    propositions = db.propositions
    # db.propositions.create_index([('url', pymongo.ASCENDING)], unique=True)
    # db.arguments.create_index([('url', pymongo.ASCENDING)], unique=True)
    for page in db.pages.find({}):
        if page is None:
            break
        if page["url"] in db.propositions.distinct("url"):
            continue
        else:
            soup = load_page(page["url"])
            if soup is None:
                continue
            else:
                try:
                    proposition = get_proposal(soup)
                    print(proposition)
                    
                    propositions.insert(proposition)
                    
                except pymongo.errors.DuplicateKeyError:
                    # extract_profile(proposition["author"])
                    pass
    # page = db.pages.find_one()
    # p = load_proposal_page(page["url"])
    # print(p)