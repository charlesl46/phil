from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme
import requests
import meteofrance_api
from babel.dates import format_datetime
import datetime
import time,os
import nltk
import numpy as np

class EmailHighlighter(RegexHighlighter):
    """Apply style to anything that looks like an email."""

    base_style = "example."
    highlights = [r"(?P<email>[\w-]+@([\w-]+\.)+[\w-]+)"]

def get_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json').json()
        return response["ip"]
    except:
        return None

from bs4 import BeautifulSoup

class Article:
    """
    A class to modelize Le Monde newspaper articles
    - title : the title of the article
    - link : the link of the article
    - image : the image of the article
    - type : the type of the article
    - subject : the subject of the article
    """
    def __init__(self) -> None:
        pass

    def _set_title(self,title : str) -> None:
        self.title = title

    def _set_link(self,link : str) -> None:
        self.link = link

    def _set_image(self,image : str) -> None:
        self.image = image

    def _set_type(self,type : str) -> None:
        self.type = type

    def _set_subject(self,subject : str) -> None:
        self.subject = subject

class LeMonde:
    """
    A class to modelize LeMonde articles
    """
    def __init__(self) -> None:
        pass

    def get_articles(self) -> list[Article]:
        """This method returns a list of Article objects now available on Le Monde's website homepage

        Returns:
            list[Article]: the list of articles to be returned
        """
        articles = []
        response = requests.get("https://www.lemonde.fr/")
        soup = BeautifulSoup(response.text,"html.parser")
        for div in soup.findAll("div",{'class' : 'article'}):
            article = Article()
            title = div.select_one(".article__title")
            article._set_title(title.text)
            link = div.find('a')["href"]
            subject = str(link.split('/')[3])
            article._set_subject(subject)
            article._set_link(link)
            try:
                image = div.find("img")["src"]
            except:
                try:
                    image = div.find("img")["data-src"]
                except:
                    image = None
            article._set_image(image)
            try:
                type = div.select_one('.article__type').text
            except:
                type = None
            article._set_type(type)
            articles.append(article)
        return articles

def get_size(bytes, suffix="o",factor = 1024):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def link(uri, label=None):
    if label is None: 
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST 
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)

def get_location():
    try:
        ip_address = get_ip()
        city = None
        debut = time.time()
        while city is None:
            response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
            location_data = {
                "ip": ip_address,
                "city": response.get("city"),
                "region": response.get("region"),
                "country": response.get("country_name")
            }
            fin = time.time()
            if (fin - debut) > 5:
                return None
            city = location_data.get("city")
        return city
    except:
        return None

def fetch_weather(place : str):
    try:
        client = meteofrance_api.MeteoFranceClient()
        place = client.search_places(place)[0]
        forecast = client.get_forecast_for_place(place)
        return {"description" : forecast.today_forecast.get('weather12H').get("desc"),"minimal" : int(forecast.today_forecast.get('T').get("min")),"maximal" : int(forecast.today_forecast.get('T').get("max"))}
    except:
        return None

def n_first_sentences(text : str,n):
    return ''.join(nltk.sent_tokenize(text)[:n])

def n_last_sentences(text : str,n):
    return ''.join(nltk.sent_tokenize(text)[n:])

def get_date():
    date_formated = format_datetime(datetime.datetime.now(), format="full", locale='fr').replace("temps universel coordonné","").split(",")
    date_words = date_formated[0].strip().split(" ")
    date_words[0] = date_words[0].capitalize()
    date_words[2] = date_words[2].capitalize()
    date = " ".join(date_words)
    time = date_formated[1].strip()
    return date,time

class FolderParser:
    def __init__(self,path : str) -> None:
        self.path = path
        self.extensions = []
        pass

    def get_extension(self,text):
        return text.split(".")[-1]

    def find_dominant_extension(self,extensions : list):
        counts = self.find_counts()
        return counts[max(list(counts.keys()))]

    def find_counts(self):
        return {self.extensions.count(ext) : ext for ext in np.unique(self.extensions)}

    def find_percents(self,counts : dict):
        percents = {count/sum(counts.keys()) * 100 : ext for count,ext in counts.items()}
        return percents

    def has_extension(self,file : str):
        return len(file.split(".")) > 1 and not(file.startswith("."))

    def find_dominant_extensions(self):
        for file in os.listdir(self.path):
            pass
        for _,_,file in os.walk(self.path):
            print(file)
            self.extensions.extend([self.get_extension(file) for file in file if self.has_extension(file)])

        counts = self.find_counts()
        percents = self.find_percents(counts)
        return percents
    

