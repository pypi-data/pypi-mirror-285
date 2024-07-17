<img src="static/Marianne.png" alt="Marianne" width="150"/>

# Olympiabhub

Olympiabhub est une librairie Python pour interagir avec l'API Olympia.

## Installation

Vous pouvez installer la librairie via pip :

```sh
pip install olympiabhub
```

## Documentation

1. Chat depuis Nubonyxia

```py
from olympiabhub import OlympiaAPI

api = OlympiaAPI(token=API_TOKEN)

reponse = api.ChatNubonyxia(modele, prompt)
```

2. Chat depuis un environnement sans proxy

```py
from olympiabhub import OlympiaAPI

api = OlympiaAPI(token=API_TOKEN)

reponse = api.Chat(modele, prompt)
```
