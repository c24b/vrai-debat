#!/usr/bin/env python3
# coding : utf-8

#timing
import time
#randomization
import random
# connexion
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#parsing
from bs4 import BeautifulSoup as bs
#base de données
import pymongo
from pymongo import MongoClient

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
    # options.add_argument('window-size=1920x1080')
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    return driver

def extract_content(driver):
    '''driver with some interactions returns raw content''' 
    cookies = driver.find_element_by_id('cookie-consent')
    cookies.click()
    try:
        vote_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "opinion-votes-show-all"))
        )
    finally:
        
    # votes = driver.find_element_by_id("opinion-votes-show-all")
        vote_btn.click()
        driver.switch_to_frame("frameName")
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

def extract_theme(page_url):
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
    r = request_page(page_url)
    #parse
    soup = bs(r.text, "lxml")
    slug = page_url.split(
        "/consultation/")[0].replace("https://le-vrai-debat.fr/project/", "")

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
    # current-page contains the first set of propositions pages urls (0-10)
    # propositions_0 = get_proposal_url(soup)

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
        "pages": int(page_offset)
    }


def store_themes():
    '''inserer le theme dans la  base de données'''
    client = MongoClient('localhost', 27017)
    db = client.vrai_debat
    themes = db.themes
    db.themes.create_index([('nb', pymongo.ASCENDING)], unique=True)
    count = 0
    for theme in map(extract_theme, URLS):
        count = count + 1
        theme["nb"] = count
        try:
            db.themes.insert(theme)
        except pymongo.errors.DuplicateKeyError:
            pass
    return

def next_urls(theme):
    print(theme["url"], theme["pages"])
    '''générer les pages qui listent les propositions a partir du theme'''
    return ["{}page/{}".format(theme["url"], page_nb) for page_nb in list(range(1, int(theme["pages"])+2))]


def get_proposal_url(soup):
    '''get the url of the full description page'''
    return [s.h3.a.get("href") for s in soup.findAll("div", {"class": "opinion__body"})]

def get_proposal_short(page_url):   
    driver = load_page(page_url)
    time.sleep(3)
    r_text = driver.page_source
    driver.close()
    soup = bs(r_text, "lxml")
    for prop in soup.find_all("li", {"class":"opinion"}):
        stats_votes = {"d'accord": int(prop.get("data-ok").replace(",", "")), "pas d'accord":int(prop.get("data-nok").replace(",", "")), "mitigé":int(prop.get("data-mitige").replace(",", ""))}
        stats_votes["total"] = sum(stats_votes.values())
        # print(prop)
        author_block =  prop.find("p", {"class":"opinion__user"})
        author = {"url": ROOT_URL+author_block.a.get("href"), "name":author_block.a.text}
        date = author_block.text.split("• ")[1].strip()
        title = prop.find("h3").text
        url = ROOT_URL+prop.find("h3").a.get("href")
        stats_block =  dict([n.strip().split(" ") for n in prop.find("p", {"class":"opinion__votes"}).text.split("•")])
        stats = {v:int(k.replace(",", "")) for k,v in stats_block.items()}
        proposition = {
            "titre": title.strip(),
            "url": url,
            "date": date,
            "auteur": author,
            "stats":stats,
            "votes": stats_votes
        }
        # infos = extract_desc_proposal(url)
        # proposition.update(infos)
        yield proposition
    # ("div", {"class":"opinion__data"}
    
    

def store_proposal_short():
    client=MongoClient('localhost', 27017)
    db= client.vrai_debat
    themes=db.themes
    
    for theme in db.themes.find().sort([('nb', pymongo.ASCENDING)]):
        next_p = next_urls(theme)
        for page in sorted(next_p, key=lambda k: random.random()):  
            # print(page)
            for prop in get_proposal_short(page):
                # prop = db.proposition.insert(prop)
                prop["theme"] = theme
                db.proposal.insert(prop)
            
def extract_desc_proposal(url):
    '''ajouter simplement le texte descriptif à la proposition initiale'''
    driver = load_page(url)
    time.sleep(3)
    r_text = driver.page_source
    soup = bs(r_text, "lxml")
    driver.close()
    # title = soup.find("h3", {"class": "title"}).text.strip()
    # author_block = soup.find("div", {"class": "opinion__user"})
    # created_date = author_block.findAll("span")[1].get("title")
    
    #description
    # desc_multiple = soup.find_all("div", {"class": "opinion__description"})
    # [d.find("button").extract() for d in desc_multiple]
    try:
        desc = " ".join([p.text.strip() for p in soup.find("div", {"class":"opinion__details"}).find_all("div", {"class":"ql-editor"})])
        return desc
    except AttributeError:
        print(url)
        return None
    # return {"title":title, "date": created_date, "text": description}

def store_proposals():
    '''ajouter la description à la proposition'''
    print("Ok")
    client = MongoClient('localhost', 27017)
    db = client.vrai_debat
    # try:
    nb = db.proposal.count({"text":{"exists": False}})
    print(nb)

    for short_desc in  db.proposal.find({"text":{"exists": False}}):
        titre = short_desc["titre"].strip()
        desc = extract_desc_proposal(short_desc["url"])
        if desc is None:
            
            db.proposal.update({"url":short_desc["url"]}, {"$set":{"titre": titre}})
        else:
            # print("insert desc")
            db.proposal.update({"url":short_desc["url"]}, {"$set":{"titre": titre, "text": desc}}, upsert=False)
        
        # print(res)
    # except pymongo.errors.CursorNotFound:
        # print("error")
        # return store_proposals()
def extract_proposal(url):
    '''extraire les informations relative à la proposition'''
    driver = load_page(url)
    time.sleep(2)
    r_text = driver.page_source
    driver.close()
    soup = bs(r_text, "lxml")
    author_block = soup.find("div", {"class": "opinion__user"})
    author = {"name": author_block.a.text, "url": author_block.a.get("href")}
    created_date = author_block.findAll("span")[1].get("title")
    title = soup.find("h3", {"class": "title"}).text.strip()
    stats = {
        "votes":0,
        "amendement":0,
        "arguments":0,
        "sources": 0
    }

    stats_block = soup.find(
        "li", {"class": "list-group-item__opinion"}).find("ul", {"class": "excerpt"}).findAll("li")
    # stats = dict(zip(["votes", "amendements", "arguments", "sources"], [
    #              stats_block.split(" • ")]))
    stats_x = dict(zip(["votes", "amendements", "arguments", "sources"],
                     [int(n.span.text.split(" ")[0].replace("\u202f", "")) for n in stats_block]))
    
    stats.update(stats_x)
    #repartition des votes
    votes_stats = {
        "d'accord":None,
        "mitigé": None,
        "pas d'accord": None,
        "total": None,
    } 
    votes_table = soup.find("table")
    if votes_table is not None:
        votes = [td.text for td in soup.find("table").find_all("td")]
        votes_values = [int(v.replace(",", ""))
                    for i, v in enumerate(votes) if i % 2 != 0]
        votes_labels = [v.lower() for i, v in enumerate(votes) if i % 2 == 0]
        votes_stats["total"] = sum(votes_values)
        votes_stats_x = dict(zip(votes_labels, votes_values))
        votes_stats.update(votes_stats_x)
    #repartition des arguments
    arguments_stats = { "pour": 0, "contre":0, "total":0} 
    arg_for_block = soup.find(
        "div", {"id": "opinion__arguments--FOR"})
    if arg_for_block is not None:

        arguments_stats["pour"] = int(soup.find("div", {"id": "opinion__arguments--FOR"}).h4.text.split(" ")[0])
    arg_against_block = soup.find(
        "div", {"id": "opinion__arguments--AGAINST"})
    if arg_against_block is not None:

        arguments_stats["contre"] = int(soup.find("div", {"id": "opinion__arguments--AGAINST"}).h4.text.split(" ")[0])
    arguments_stats["total"] = arguments_stats["pour"] + arguments_stats["contre"]
    #description
    desc_multiple = soup.find_all("div", {"class": "opinion__description"})
    try:
        desc_multiple[1].button.decompose()
        desc_multiple[1].find("div", {"class": "opinion__votes__box"}).decompose()
        desc_multiple[1].find("div", {"class": "opinion__buttons"}).decompose()
        desc = " \n---\n ".join([desc.text.strip() for desc in desc_multiple])
    except IndexError:
        desc = " \n---\n ".join([desc.text.strip() for desc in desc_multiple])
    description = desc.replace("\n", "").replace("\\'", " ").strip()
    return  {
        "author": author,
        "url": soup.h3.a.get("href"),
        "title": title,
        "description": description,
        "date": created_date,
        "stats": stats,
        "votes": votes_stats, 
        "arguments": arguments_stats
        }


def get_detail_votants(soup):
    print(soup.find_all("opinion__votes__more__modal"))
    votes_users = [
        {
            "url":block.a.get("href"), 
            "name":block.a.text, 
            "contributions_nb":block.find("p", {"class":"excerpt"})
        } for block in soup.find_all("opinion__votes__more__modal")]

if __name__ == "__main__":
    # store_proposal_short()
    print("....")
    store_proposals()
    