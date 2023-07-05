import time,sys
from rich.console import Console
import random
from tmdbv3api import TMDb, Movie
from bs4 import BeautifulSoup
import os
from larousse_api import larousse
from utils import get_location,fetch_weather,get_date,link
import pickle
from babel.dates import format_datetime
import spacy
import platform
from user import User
from rich.prompt import Prompt
import psutil
import googlesearch
from PIL import Image
import synonymes,imgcat
from rich import emoji

#from polyglot.detect import Detector

import wikipedia
import requests,json,urllib
from translate import Translator
from utils import n_first_sentences,n_last_sentences,get_size,LeMonde


class Assistant:
    def initialisation(self):
        self.name = "Phil"
        self.console.clear()
        self.current_user = None
        self.version = "0.0.1"
        self.timeout = 5
        wikipedia.set_lang("fr")
        self.read_registered_users()
        tmdb = TMDb()
        tmdb.api_key = 'a5beed50b62bc4886b8da6bb2b823fa3'
        tmdb.language = 'fr'
        tmdb.debug = True
        self.disk_space_taken = self.get_space_used()
        self.python_version = platform.python_version()
        self.sysname, self.nodename, _, _, self.machine = os.uname()
        names = {"linux" : "Linux","win32" : "Windows","Darwin" :"macOS"}
        self.stats = {"OS" : f"{names.get(self.sysname)} on {self.machine}","Appareil" : self.nodename}
        battery_stats = self.battery_stats()
        if battery_stats.get('power_plugged'): 
            self.description = f"{self.name} ({self.version}) sous Python {self.python_version} sur la machine {self.nodename} en charge à {battery_stats.get('percents')}% ({get_size(self.disk_space_taken,factor=1000)} occupés par le logiciel)"
        else:
            tl = battery_stats.get('time_left')
            self.description = f"{self.name} ({self.version}) sous Python {self.python_version} sur la machine {self.nodename} sur batterie ({tl[1]} {tl[0]} restante(s)) ({get_size(self.disk_space_taken,factor=1000)} occupés par le logiciel)"
        pass



    def load_user_data(self):
        file_name = f"./data/users/{self.hash_name(self.current_user.id)}.pkl"
        if os.path.exists(file_name):
            with open(file_name,"rb") as file:
                self.current_user_data = pickle.load(file)
                self.current_user_statistics = pickle.load(file)
            file.close()
        else:
            self.current_user_data = {}
            self.current_user_statistics = {}
            self.dump_user_data()
            self.load_user_data()

    def info_of_the_day(self):
        url = "https://fr.wikipedia.org/wiki/"
        r = requests.get(url)
        response = BeautifulSoup(r.text,"html.parser")
        self.log("Information du jour :",style = "underline")
        self.log(response.find_all("div",{"class" : "accueil_2017_cadre"})[2].find_all("li")[1].text,with_date=False)

    def show_definition(self,text : str):
        definition = larousse.get_definitions(text)
        if len(definition) > 0:
            self.log("Voici la définition que j'ai trouvé :")
            definition = definition[0].replace('1.','').replace('\t','')
            self.log(f"{text.capitalize()}",style = "underline",backline=False)
            self.log({definition},with_date=False,style="italic")
        else:
            self.log(f"Désolé, je n'ai pas trouvé de définition pour {text}.")

    def find_synonyms(self,query):
        synos = synonymes.linternaute(query)[:3]
        self.log(f"Comme synonymes de {query}, vous pourriez utiliser :")
        self.show_as_list(*synos)

    def get_space_used(self,path = "."):
        size = 0
        for file in os.listdir(path):
            if os.path.isdir(f"{path}/{file}"):
                size = size + self.get_space_used(path = f"{path}/{file}")
            else:
                size = size + os.path.getsize(f"{path}/{file}")
        return size

    def __init__(self) -> None:
        self.console = Console(highlight=False)
        pass

    def display_picture(self,path):
        try:
            imgcat.imgcat(Image.open(path),preserve_aspect_ratio=True)
            return True
        except:
            return None

    def get_wiki_image(self,title):
        WIKI_REQUEST = 'http://fr.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='
        try:
            response  = requests.get(WIKI_REQUEST+title)
            json_data = json.loads(response.text)
            img_link = list(json_data['query']['pages'].values())[0]['original']['source']
            return img_link      
        except:
            return None
        
    def download_image(self,link,title) -> str:
        title_path = self.hash_name(title)
        path = f"./data/pictures/{title_path}.jpg"
        try:
            urllib.request.urlretrieve(link,path)
            return path
        except:
            return None
        
    # a améliorer !!!!! split le texte en petits bouts
    def translate(self,text : str,from_lang,to_lang = "fr"):
        t = Translator(to_lang=to_lang,from_lang=from_lang)
        n = 5
        text_list = None
        try:
            return t.translate(text)
        except:
            ## à améliorer
            return None
        
    def hash_name(self,name : str):
        hash = 0
        for i,letter in enumerate(name):
            try:
                hash += ord(letter) * (i+1)
            except:
                hash += 1000
        return hash
    
    def search(self,query):
        self.log("Je vais me renseigner !")
        browsing_strings = ["Recherche en cours",f"Recherche d'informations sur {query}"]
        browsing_string = random.sample(browsing_strings,1)[0]
        page = None
        results = None
        with self.console.status(browsing_string):
            try:
                
                page = wikipedia.page(wikipedia.search(query)[0],preload = False,auto_suggest=False)


                # à chaque page consultée, enregistrer le résultat dans un fichier.pkl et, au lieu de chercher, récupérer ce qu'il y a dedans
                if page is not None:
                    previously_consulted_wiki_pages = self.current_user_data.get("previously_consulted_wiki_pages")
                    if previously_consulted_wiki_pages:
                        previously_consulted_wiki_pages[page.title] = page.summary
                    else:
                        previously_consulted_wiki_pages = {}
                        previously_consulted_wiki_pages[page.title] = page.summary
                        self.current_user_data["previously_consulted_wiki_pages"] = previously_consulted_wiki_pages

                    wikipedia_statistics = self.current_user_statistics.get("wikipedia_statistics")
                    if wikipedia_statistics:
                        if wikipedia_statistics.get(page.title):
                            wikipedia_statistics[page.title] += 1
                        else:
                            wikipedia_statistics[page.title] = 1
                    else:
                        wikipedia_statistics = {}
                        wikipedia_statistics[page.title] = 1
                        self.current_user_statistics["wikipedia_statistics"] = wikipedia_statistics

                    print(f"c'est la {self.current_user_statistics.get('wikipedia_statistics').get(page.title)} fois que vous consultez cette page")
                    # ces deux fonctionnalités font un peu doublon, l'avantage de la deuxième est qu'elle s'applique à tous les utilisateurs, mais elle démultiplie un peu le nombre de fichiers
                    if os.path.exists(f"./data/info/{self.hash_name(page.title)}.pkl"):
                        #print(f"DEBUG :  je vais chercher les données dans ./data/info/{self.hash_name(page.title)}.pkl")
                        with open(f"./data/info/{self.hash_name(page.title)}.pkl","rb") as file:
                            info = pickle.load(file)
                        file.close()
                    else:
                        #print(f"DEBUG : j'enregistre les données dans ./data/info/{self.hash_name(page.title)}.pkl")
                        info = (page.title,page.summary)
                        with open(f"./data/info/{self.hash_name(page.title)}.pkl","wb") as file:
                            pickle.dump(info,file)
                        file.close()
                
            except:
                try:
                    results = googlesearch.search(query,num_results=5,advanced=True,lang="fr")
                    results = [f"{result.url.split('.')[1]} {result.title} : {result.description} ({link(result.url)})" for result in results]
                except:
                    pass
        if page:
            self.log("Selon wikipédia :",with_date=False)
            self.log(info[0],style = "bold underline",with_date=False)
            picture_link = self.get_wiki_image(info[0])
            if picture_link:
                path = self.download_image(picture_link,info[0])
                if path and os.path.getsize(path) > 50000:
                    self.display_picture(path)
                os.remove(path)            
            self.log(info[1],with_date = False,style = "italic",speed = 0.02)

        elif results and len(list(results)) > 0:
            previously_made_google_searchs = self.current_user_data.get("previously_made_google_searchs")
            if previously_made_google_searchs:
                previously_made_google_searchs[query] = results
            else:
                previously_made_google_searchs = {}
                previously_made_google_searchs[query] = results
                self.current_user_data["previously_made_google_searchs"] = previously_made_google_searchs
            
            self.log("J'ai trouvé sur le web les résultats suivants :")
            self.show_as_list(*results,speed = 0.02)
        else:
            self.log(f"Désolé, je ne parviens pas à trouver de résultats pour {query}.")

    def read_registered_users(self) -> None:
        name = "./data/users/user_data.pkl"
        if "user_data.pkl" in os.listdir("./data/users"): 
            with open(name,"rb") as file:
                try:
                    self.registered_users = pickle.load(file)
                except:
                    file.close()
                    superuser = User("admin","admin","Lucas")
                    reg_users = {superuser.id : superuser}
                    with open(name,"wb") as file:
                        pickle.dump(reg_users,file)
                    file.close()
        else:
            raise FileNotFoundError("The users profiles file is missing.")

    #def find_subjects(self,text):
        #doc = self.nlp(text)
        #return [token.text for token in doc]

    def welcome_view(self):
        date,time = get_date()
        if self.weather or (self.current_user_data.get("last_location") and self.current_user_data.get("last_weather")):
            if not self.weather:
                self.weather = self.current_user_data.get("last_weather")
                self.location = self.current_user_data.get("last_location")
            self.log(f"Nous sommes le {date} et aujourd'hui le temps sera {self.weather.get('description').lower()} avec des températures allant de {self.weather.get('minimal')} à {self.weather.get('maximal')} degrés à {self.location}.")                
        else:
            self.log(f"Nous sommes le {date}.")
        
    def create_user_profile(self):
        id = self.ask("Entrez un identifiant (4 caractères minimum, tous caractères alphanumériques autorisés)")
        password = self.ask("Entrez un mot de passe (4 caractères minimum)",password = True)
        name = self.ask("Enfin, entrez le nom par lequel je serai amené à vous appeler")
        user = User(id,password,name)
        self.update_registered_users(user)
        return user
    
    def update_registered_users(self,new_user):
        self.registered_users[new_user.id] = new_user
        with open("./data/users/user_data.pkl","wb") as file:
            pickle.dump(self.registered_users,file)
        file.close()

    def ram_statistics(self):

        # il faudrait réfléchir à les afficher dans un tableau rich
        svmem = psutil.virtual_memory()

        memory_stats = []
        memory_stats.append(f"Mémoire totale: {get_size(svmem.total)}")
        memory_stats.append(f"Disponible : {get_size(svmem.available)}")
        memory_stats.append(f"Utilisée : {get_size(svmem.used)}")
        memory_stats.append(f"Utilisée à : {svmem.percent}%")
        self.log(f"Statistiques RAM de la machine {self.nodename} :")
        self.show_as_list(*memory_stats)

    def battery_stats(self):
        battery = psutil.sensors_battery()
        secs_left = battery.secsleft
        minutes_left = secs_left // 60
        hours_left = None
        power_plugged = battery.power_plugged
        if minutes_left > 59:
            hours_left = minutes_left // 60
        if hours_left:
            return {"power_plugged" : power_plugged,"percents_left" : battery.percent,"time_left" : ("heure(s)",hours_left)}
        else:
            return {"power_plugged" : power_plugged,"percents_left" : battery.percent,"time_left" : ("minute(s)",minutes_left)}


    def disk_statistics(self):
        disk_stats = []

        partitions = psutil.disk_partitions()
        for partition in partitions:
            disk_stats.append(f"Appareil : {partition.device}")
            disk_stats.append(f"\tMonté sur : {partition.mountpoint}")
            disk_stats.append(f"\tSystème de fichiers : {partition.fstype}")
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_stats.append(f"\tEspace total : {get_size(partition_usage.used + partition_usage.free)}")
                disk_stats.append(f"\tUtilisé : {get_size(partition_usage.used)}")
                disk_stats.append(f"\tDisponible : {get_size(partition_usage.free)}")
                disk_stats.append(f"\tPourcentage d'utilisation: {partition_usage.percent}%")
            except PermissionError:
                # this can be catched due to the disk that
                # isn't ready
                continue
        
        self.show_as_list(*disk_stats)

    def set_current_user(self,user : User) -> None:
        self.current_user = user
        self.load_user_data()
        if self.weather:
            self.current_user_data["last_weather"] = self.weather
        if self.location:
            self.current_user_data["last_location"] = self.location
        self.log(f"{self.current_user.id} connecté à {self.description}",with_date=False,speed = 0.02)

    def suggest_movie(self,query):
        movie = Movie()
        try:
            film = movie.search(query)[0]
            suggestion = movie.recommendations(film.id)[0]
            self.log(f"Si vous aimez {film.title}, je vous recommande le film suivant :")
        except:
            suggestion = None
            pass
        if not suggestion:
            suggestion = movie.popular()[0]
            self.log("Je n'ai trouvé aucun film en lien avec votre requête, mais je peux vous recommander le film suivant :")
        self.log(f"{suggestion.title} : {suggestion.overview}",style="italic",with_date=False)

    def show_weather(self,place : str):
        weather = fetch_weather(place)
        if weather:
            self.log(f"Aujourd'hui à {place.capitalize()}, il fera {weather.get('description').lower()} pour des températures allant de {weather.get('minimal')} à {weather.get('maximal')}.")
        else:
            self.log(f"Je n'ai pas trouvé de météo pour votre requête, désolé.")


    def ask(self,text,password = False,default = None) -> str:
        self.log(f"{text} ",backline=False,after_timing=False)
        return Prompt.ask("",password=password,console=self.console,default = default)

    def user_profile_selection(self):
        if len(self.registered_users) == 0:
            self.log("Aucun utilisateur n'est enregistré, souhaitez vous créer un profil ? (o/n)")
            answer = input()
            if answer.lower() == "o":
                newuser = self.create_user_profile()
                self.set_current_user(newuser)
            else:
                quit()
        else:
            create_connect = self.ask("Souhaitez vous créer un profil (1) ou vous connecter à un profil existant (2) ? (1/2)",default="2")
            if create_connect == "1":
                user = self.create_user_profile()
                self.set_current_user(user)
            else:
                self.log("J'ai trouvé les profils suivants :")
                self.show_registered_users()
                id = self.ask("Entrez votre identifiant")
                if id in list(self.registered_users.keys()):
                    ok = False
                    while not ok:
                        password = self.ask("Mot de passe",password=True)
                        if password == self.registered_users[id].password:
                            with self.console.status("Identification en cours..."):
                                time.sleep(0.5)
                            self.console.log("Identification réussie",style="bold green")
                            time.sleep(0.5)
                            self.console.clear()
                            self.set_current_user(self.registered_users[id])
                            ok = True
                        else:
                            self.log("Mauvais mot de passe, veuillez réessayer.",backline=False)
                else:
                    self.log("Cet utilisateur n'existe pas.",backline=False)
                    self.logout()
                    

    def show_as_list(self,*elements,speed = 0.04) -> None:
        for element in elements:
            self.log(f"\t - {element}",with_date=False,backline=True,speed = speed)
        pass

    def wake_up_log(self):
        strings = [("Initialisation","Initialisation terminée"),("Démarrage","Démarrage terminé")]
        wake_up_string = random.sample(strings,1)[0]
        with self.console.status(wake_up_string[0],spinner="dots",spinner_style="green"):
            self.initialisation()
            self.location = get_location()
            self.weather = fetch_weather(self.location)
            #self.nlp = spacy.load("fr_core_news_md")
        self.console.log(wake_up_string[1],style = "bold green")
        time.sleep(1)
        self.console.clear()

    def os_statistics(self):

        # à mettre en tableau
        self.log("Voici les statistiques du système d'exploitation :")        
        self.show_as_list(*[f"{stat_name} : {stat_value}" for stat_name,stat_value in zip(list(self.stats.keys()),list(self.stats.values()))])
               
    def contains_one_of_strings(self,q : str,*strings) -> bool:
        for string in strings:
            if q.lower().__contains__(string.lower()):
                return True
        return False
    
    def contains_all_of_strings(self,q : str,*strings) -> bool:
        for string in strings:
            if not q.lower().__contains__(string.lower()):
                return False
        return True
    
    def show_registered_users(self):
        self.show_as_list(*list(self.registered_users.values()))

    def delete_profile(self,id):
        user = self.registered_users[id]
        del self.registered_users[id]
        self.log(f"{user} supprimé.")

    def proposes_to_help(self):
        things = ["Que puis je faire pour vous ?","Comment puis-je vous être utile ?","Avez-vous besoin de quelque chose ?"]
        thing = random.sample(things,1)[0]
        self.log(thing)

    def show_help(self):
        self.log("Vous pourriez me demander par exemple :")
        things = ["Traduction de ...I love you... de anglais à français","Traduction de ...J'ai faim... de français à espagnol","Angelina Jolie","Photos de Paris","Système d'exploitation","Espace disque","Quitter"]
        two_things = random.sample(things,2)
        self.log(two_things[0],style = "italic",with_date=False)
        self.log("Ou encore")
        self.log(two_things[1],style = "italic",with_date=False)
    
    #def show_photos(self):

    

    def receive_query(self):
        query = input()
        thinking_strings = ["Je réfléchis","Analyse","Un instant","Chargement"]
        thinking_string = random.sample(thinking_strings,1)[0]
        with self.console.status(f"{thinking_string}..."):
            time.sleep(0.5)
            found_strings = ["Fin de processus","Analyse terminée","Terminé","Chargement terminé"]
            found_string = random.sample(found_strings,1)[0]
            self.console.log(f"{found_string}!",style="bold green")
            time.sleep(0.5)
            self.console.clear()

            # il y a des trucs a faire avec spacy ici pour mieux comprendre le sens des requêtes
            match query:
                case _ as q if q.__contains__("hello"):
                    what_to_do = "wake up"
                case _ as q if self.contains_one_of_strings(q,"os","exploitation","système"):
                    what_to_do = "os"
                case _ as q if self.contains_one_of_strings("effacer","clear"):
                    what_to_do = "clear"
                case _ as q if self.contains_all_of_strings(q,"supprimer","profil"):
                    what_to_do = "delete profile"
                case _ as q if self.contains_one_of_strings(q,"ram") or self.contains_all_of_strings(q,"mémoire","vive"):
                    what_to_do = "ram"
                case _ as q if self.contains_one_of_strings(q,"disque","memoire") or self.contains_all_of_strings(q,"espace","disque"):
                    what_to_do = "disk"
                case _ as q if self.contains_one_of_strings(q,"quitter","partir","éteindre","fermer"):
                    what_to_do = "leave"
                case _ as q if self.contains_one_of_strings(q,"traduire","traduction","traduit"):
                    what_to_do = "translate"
                case _ as q if self.contains_one_of_strings(q,"photos de","photo de"):
                    what_to_do = "photos"
                case _ as q if self.contains_one_of_strings(q,"aide"):
                    what_to_do = "help"
                case _ as q if self.contains_one_of_strings(q,"actualités","actualité"):
                    what_to_do = "news"
                case _ as q if self.contains_one_of_strings(q,"synonyme","synonymes"):
                    what_to_do = "syno"
                case _ as q if self.contains_one_of_strings(q,"météo","temps","meteo","méteo"):
                    what_to_do = "weather"
                case _ as q if self.contains_one_of_strings(q,"definition","définition","définitions","définir"):
                    what_to_do = "definition"
                case _ as q if self.contains_one_of_strings(q,"suggere","suggestion","film"):
                    what_to_do = "movie"
                case _:
                    what_to_do = "search"
        match what_to_do:
            case "wake up":
                self.wake_up_log()
            case "os":
                self.os_statistics()
            case "clear":
                self.console.clear()
            case "syno":
                word = query.split(" ")[-1]
                self.find_synonyms(word)
            case "weather":
                place = query.split(" ")[-1]
                self.show_weather(place)
            case "delete profile":
                answer = Prompt.ask(f"Voulez vous vraiment supprimer le profil {self.current_user} ?",choices = ["o","n"],console = self.console)
                if answer == "o":
                    self.delete_profile()
                    self.logout()
            case "photos":
                query = query.replace("photos de","").replace("photo de","")
                self.show_photos(query)
            case "ram":
                self.ram_statistics()
            case "disk":
                self.disk_statistics()
            case "leave":
                self.logout()
            case "search":
                self.search(query)
            case "help":
                self.show_help()
            case "movie":
                title = query.replace("film","")
                self.suggest_movie(title)
            case "definition":
                word = query.split(" ")[-1]
                self.show_definition(word)
            case "news":
                self.show_news()
            case "translate":
                text_to_translate = query.split("...")[1]
                languages = {"français" : "fr","anglais" : "en","espagnol" : "es","italien" : "it","allemand" : "de"}
                languages_reversed = {value : key for (key,value) in languages.items()}
                words = query.split(" ")
                lang_to = languages.get(words[-1])
                if lang_to is None: lang_to = "fr"
                lang_from = languages.get(words[-3])

                translation = self.translate(text_to_translate,from_lang=lang_from,to_lang=lang_to)
                if translation:
                    self.log(f"Voici la traduction en {languages_reversed[lang_to]} de votre texte en {languages_reversed[lang_from]}")
                    self.log(f"\"{translation}\"",style = "italic",with_date=False)
                else:
                    self.log("Désolé, je ne suis actuellement pas en mesure d'effectuer cette traduction.")
    pass        

    def show_news(self):
        lm = LeMonde()
        self.log(f"Voici ce que j'ai trouvé dans l'actualité")
        news = lm.get_articles()[:3]
        news = [f"{new.subject.capitalize()} : {new.title}" for new in news if new.subject]
        self.show_as_list(*news)
        
    def log(self,text : str,with_date = True,backline = True,after_timing = True,speed = 0.03,style = None):
        try:
            date,time_value = get_date()
            if with_date:
                if self.current_user is not None:
                    self.console.print(f"{time_value} ([i]{self.current_user.id}[/i] connecté) ",end="",style = "dim")
                else:
                    self.console.print(f"{time_value} ",end="",style = "dim")
            for letter in str(text):
                self.console.print(letter,end = "",style = style)
                sys.stdout.flush()
                time.sleep(speed)
            
            if backline:
                print("\n")
            
            if after_timing: 
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n\n")
            pass

    def run(self):
        try:
            # pour aller plus vite 
            self.wake_up_log()
            #self.user_profile_selection()
            self.set_current_user(self.registered_users["admin"])
            self.info_of_the_day()
            self.welcome_view()

            self.log(f"Bonjour {self.current_user.name} !")
            self.log("Comment puis-je vous aider aujourd'hui ?",with_date=False)
            self.log("Vous pouvez obtenir de l'aide sur mon fonctionnement avec la commande 'aide'",with_date=False)
            while 1:
                self.receive_query()
                self.proposes_to_help()
        
        except KeyboardInterrupt:
            self.logout()

    def dump_user_data(self):
        with open(f"./data/users/{self.hash_name(self.current_user.id)}.pkl","wb") as file:
            pickle.dump(self.current_user_data,file)
            pickle.dump(self.current_user_statistics,file)
        file.close()
    
    def logout(self):
        self.console.clear()
        logout_words = ["Fin de session","Déconnexion","Session terminée","Fin de transmission","Verrouillage","Veille enclenchée"]
        self.dump_user_data()
        logout_word = random.sample(logout_words,1)[0]
        if self.current_user:
            self.log(f"{logout_word}, à bientôt {self.current_user.name}.")
        else:
            self.log(f"{logout_word}, à bientôt.")
        quit()

a = Assistant()
a.run()

        