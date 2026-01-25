from flask import Flask
from pages import pages


def create_app():
    app = Flask(__name__) # Flask constructor
    app.register_blueprint(pages.bp)
    return app


if __name__=='__main__':
    # Run the application
    app = create_app()
    app.run(host = '0.0.0.0', port = 8080)
    
    