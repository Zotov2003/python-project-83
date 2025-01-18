import os
from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def hello_world():
    """Обработчик для корневого URL."""
    return 'Привет, мир!'

if __name__ == '__main__':
    app.run(debug=True)