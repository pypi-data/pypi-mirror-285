# Olympiabhub

OlympiaBHub est une librairie Python pour interagir avec l'API Olympia depuis Nubonyxia.

## Installation

Vous pouvez installer la librairie via pip :

```sh
pip install olympiabhub
```

## Exemple d'utilisation

```py
from olympiabhub import OlympiaAPI, ChatNubonyxia

api = OlympiaAPI(token=API_TOKEN)

reponse = api.ChatNubonyxia(modele, prompt)
```
