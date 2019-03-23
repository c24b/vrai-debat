from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
page_url = "https://le-vrai-debat.fr/projects/economie-finances-travail-compte-public/consultation/consultation-6/opinions/economie-finances-travail-compte-public/nationaliser-les-autoroutes-amorties"
options = webdriver.FirefoxOptions()
options.binary_location = '/usr/bin/firefox'
options.add_argument('-headless')
options.add_argument('window-size=1920x1080')
driver = webdriver.Firefox(options=options)
driver.get(page_url)
time.sleep(10)
source = driver.page_source

soup = bs(source, "lxml")
print(soup.find_all("ul", {"class":"tabs"}))
# driver.close()11

driver.get("https://le-vrai-debat.fr/projects/economie-finances-travail-compte-public/consultation/consultation-6/opinions/economie-finances-travail-compte-public/suppression-des-remunerations-de-tous-les-elus-apres-la-fin-dun-mandat")