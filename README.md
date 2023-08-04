# Movie-recommendations

## Installation
- clone the repository with this command :
    ```git clone https://github.com/Stargate136/movie-recommendations.git```
- enter into the directory `movie-recommendations` with this command :
    ```cd movie-recommendations```
- create a virtual environment with this command :
    ```python -m venv venv```
- activate the virtual environment with this command :
    - Windows : 
        ```
        cd venv/Scripts
        activate.bat
        cd ../..
      ```
    - Mac / Linux : ```source venv/bin/activate```
- install requirements with this command :
    ```pip install -r requirements.txt```
- generate a secret key with these commands :
    ```
    cd src
    python manage.py shell
    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())
    ```
    copy the secret key
    ```exit()```
- create a file ".env" in "src" containing these lines:
    ```
    SECRET_KEY="your_secret_key"
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1
    ```
- create the database with this command :
    ```python manage.py migrate```
- run a server with the command :
    ```python manage.py runserver```

## Use
- activate the virtual environment with this command :
    - Windows : 
        ```
        cd venv/Scripts
        activate.bat
        cd ../..
      ```
    - Mac / Linux : ```source venv/bin/activate```
- run a server with the command :
    ```python manage.py runserver```