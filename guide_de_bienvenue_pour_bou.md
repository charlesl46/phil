# Guide de bienvenue pour bou

Alors, ce que tu pourrais faire c'est essayer de travailler avec l'api python de TMDB (https://github.com/AnthonyBloomer/tmdbv3api)

Pour démarrer il te faut juste ça :

```python
    tmdb = TMDb()
    tmdb.api_key = 'a5beed50b62bc4886b8da6bb2b823fa3'
    tmdb.language = 'fr'
    tmdb.debug = True
```

La ```api_key``` c'est ma clé d'api, c'est mon mot de passe en gros.

Après pour démarrer tu peux te renseigner sur le lien que j'ai indiqué au-dessus, y'a plein d'exemple. Donc voilà en gros il faut que tu développes des fonctions du style : 

```python
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
```

Celle là je l'ai déjà faite, mais en gros ce que tu dois faire c'est faire des fonctions avec un titre qui réponde à une "query", sauf si bien sûr la question n'a pas de paramètres (ex. : "trouve moi un film pour ce soir")

