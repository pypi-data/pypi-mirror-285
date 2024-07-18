<img src="static/Marianne.png" alt="Marianne" width="150"/>

# Olympiabhub

Olympiabhub est une librairie Python pour interagir avec l'API Olympia.

## Installation

Vous pouvez installer la librairie via pip :

```sh
pip install olympiabhub
```

## Documentation

1. Ajouter `OLYMPIA_API_TOKEN` à votre `.env` ou passer `token` en paramètre à `OlympiaAPI`

2. Chat depuis Nubonyxia

```py
from olympiabhub import OlympiaAPI

model = OlympiaAPI(model)

reponse = model.ChatNubonyxia(prompt)
```

3. Chat depuis un environnement sans proxy

```py
from olympiabhub import OlympiaAPI

model = OlympiaAPI(model)

reponse = model.Chat(prompt)
```
