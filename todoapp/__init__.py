from flask import Flask
import logging
import os


def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from todoapp.config import config
    app.config.from_object(config[config_name])
    
    from todoapp.extensions import db, migrate, login_manager, limiter
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    from todoapp.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from todoapp.routes.main import main
    from todoapp.routes.auth import auth
    from todoapp.routes.api import api
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')
    
    if not app.debug and not app.testing:
        init_logging(app)
    
    return app


def init_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/todolist.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('TodoList startup')
