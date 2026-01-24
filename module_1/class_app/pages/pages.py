from flask import render_template, Blueprint

bp = Blueprint("pages", __name__, template_folder = "templates")

@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/about')
def about():
    return "The ABOUT page"

@bp.route('/contact')
def contact():
    return "For more information, contact Joo Hyun!"