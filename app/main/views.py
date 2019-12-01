from flask import render_template
from . import main
from ..models import User


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/user/<nickname>')
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    return render_template('user.html', user=user)

