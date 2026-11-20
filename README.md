# SkillsExchange

Application web développé avec Python, Django et SQLite dans le cadre d'une évaluation.

## Présentation

SkillsExchange permet aux utilisateurs d'échanger leurs compétences et s'entraider.

## Fonctionnalités
- Consultation des compétences et des échanges confirmés.
- Authentification des utilisateurs.
- Sélection des compétences proposées.
- Création de demandes d'aide avec plusieurs créneaux.
- Recherche d'activités selon les compétences.
- Proposition d'aide sur un créneau disponible.
- Tableau de bord des demandes et rendez-vous.

## Installation

Cloner le dépot et accéder au projet
````
git clone https://github.com/alfaro-b/Eval_Web_Python.git
cd EvalWebPython
````

Créer et activer l'environnement virtuel (Windows) :
````
py -m venv .venv
.\.venv\Scripts\Activate.ps1
````

Installer les dépendances
````
pip install -r requirements.txt 
````

Préparer la base de données et lancer le serveur
````
python manage.py migrate  
python manage.py runserver
````

## Technologies

Python, Django 5.2, SQLite, HTML, CSS
