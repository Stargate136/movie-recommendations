# Movie-recommendations

## Instructions for use
- clone the repository with this command :
    ```git clone https://github.com/Stargate136/movie-recommendations.git```
- create a virtual environment with this command :
    ```python -m venv venv```
- activate the virtual environment with this command :
    - Windows : ```venv/Scripts/activate.bat```
    - Mac / Linux : ```source venv/bin/activate```
- install requirements with this command :
    ```pip install requirements.txt```
- generate a secret key with this commands :
    ```
    python manage.py shell
    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())
    ```
- create a file ".env" in "src":
    ```
    SECRET_KEY=your_secret_key
    DEBUG=True
    ALOWED_HOSTS=127.0.0.1
    ```
- run a server with the command :
    ```python manage.py runserver```


## TODO
- écrire les tests unitaires
- fixer bug pour les enfants / adolescents

### Step 1 : Build a web app using Django without Machine Learning

### Step 2 : Integrate the Machine learning model in the web app

