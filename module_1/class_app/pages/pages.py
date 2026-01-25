from flask import render_template, Blueprint

bp = Blueprint("pages", __name__, template_folder = "templates")

@bp.route('/')
def home():
    return render_template('home.html', active_page='home', title='HOME')

@bp.route('/project')
def project():
    return render_template('project.html', active_page='project', title='PROJECT')

@bp.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact', title='CONTACT')