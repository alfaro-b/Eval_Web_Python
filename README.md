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

### Vérification des types avec mypy

Le projet utilise mypy et django-stubs pour vérifier les types Python.

La configuration se trouve dans `mypy.ini`.

Pour lancer la vérification :
````
python -m mypy skillsApp
````

## Technologies

Python, Django 5.2, SQLite, HTML, CSS
