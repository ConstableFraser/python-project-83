from flask import Flask, render_template
from dotenv import dotenv_values

app = Flask(__name__)

config = dotenv_values(".env")


@app.route('/', methods=['GET'])
def start():
    return render_template('index.html')
