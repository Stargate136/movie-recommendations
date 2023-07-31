# Movie-recommendations

## Installation
- clone the repository with this command :
    ```git clone https://github.com/Stargate136/movie-recommendations.git```
- create a virtual environment with this command :
    ```python -m venv venv```
- activate the virtual environment with this command :
    - Windows : ```venv/Scripts/activate.bat```
    - Mac / Linux : ```source venv/bin/activate```
- install requirements with this command :
    ```pip install -r requirements.txt```
- generate a secret key with these commands :
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
