import os.path

import flask
from celery import Celery
from flask import flash, redirect, request, url_for, send_file
from flask_wtf import Form
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

import Check_Vid_ArticleRank.run_check as article_scraper
from Check_Vid_ArticleRank.search_lib.tools import check_contains_columns

if not os.path.exists("uploads"):
    os.mkdir("uploads")

flask_app = flask.Flask(__name__)
flask_app.config['SECRET_KEY'] = "knehruiwbefjkklqwhieh12123"

# Configure the redis server
flask_app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
flask_app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
flask_app.config['UPLOAD_FOLDER'] = "uploads"

# creates a Celery object
celery = Celery(flask_app.name, broker=flask_app.config['CELERY_BROKER_URL'])
celery.conf.update(flask_app.config)


class FileUploadForm(Form):
    file = FileField("Excel File", validators=[DataRequired()])
    submit = SubmitField("Submit")


@flask_app.route("/", methods=["GET"])
def home():
    upload_form = FileUploadForm()
    if request.method == "GET":
        return flask.render_template('index.html', form=upload_form)


@flask_app.route("/upload", methods=["GET", "POST"])
def upload():
    upload_form = FileUploadForm()
    if request.method == "POST":
        f = request.files['excel_file']
        extension = os.path.splitext(os.path.basename(f.filename))[-1]
        if extension in (".csv", ".xlsx"):
            flash("File uploaded!")
            __file = os.path.join("uploads", secure_filename(f.filename))
            res = check_contains_columns(__file)
            if not res:
                flash("File must have a column named 'Title' containing all titles to be searched.")
                return redirect(url_for("home"))
            f.save(__file)

            # run the background logic on this
            async_result = process_file.delay(__file)
            path = async_result.get()
            return send_file(path, as_attachment=True)
        else:
            flash("Unsupported extension, please upload file with extension: .csv or .xlsx")
    return redirect(url_for("home"))


@celery.task()
def process_file(file_name):
    """
    Celery task function to run process in background

    :param file_name: uploaded file name (after secure_file)
    :return:
    """
    print(f"Received file: {file_name}")
    return article_scraper.driver(file_name)


if __name__ == '__main__':
    flask_app.run("localhost", 8000)
