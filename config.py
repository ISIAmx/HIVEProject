
import os
basedir = os.path.abspath(os.path.dirname(__file_))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


'''
class Config:
    """Base config."""
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SECRET_KEY = 'secretkey'
'''
'''
class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/CurangelDB?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    auth_plugin = 'mysql_native_password'

    MYSQL_DATABASE_USER = 'username'
    MYSQL_DATABASE_PASSWORD = 'password'
    MYSQL_DATABASE_HOST = 'localhost'
    MYSQL_DATABASE_DB = 'Usuarios'
'''

'''
class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
'''
