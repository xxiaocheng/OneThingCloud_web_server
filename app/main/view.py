from flask import render_template

from .import main


@main.route('/',methods=['GET','POST'])
def index():
    return render_template('main/index.html')