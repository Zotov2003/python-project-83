import os

from cloudinit.templater import render_template
from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)