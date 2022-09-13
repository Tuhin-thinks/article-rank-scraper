## Flask Article Scraper Application

### How to run applcation?

```bash
sudo apt install python-celery-common
sudo apt install redis
```
### Install the requirements
```bash
pip install -r requirements.txt
```
### Run the flask app

```bash
export FLASK_DEBUG=1
export FLASK_APP=FlaskUploader.py
flask run
```
### On another terminal run the following command (to start the celery worker)

```bash
celery -A FlaskUploader worker -E
```

## TODO:
- Add support for .xlsx file type.
