
class Config:
    """Base config."""
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SECRET_KEY = 'secretkey'


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/CurangelDB?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    auth_plugin = 'mysql_native_password'

    ''' MYSQL_DATABASE_USER = 'username'
    MYSQL_DATABASE_PASSWORD = 'password'
    MYSQL_DATABASE_HOST = 'localhost'
    MYSQL_DATABASE_DB = 'Usuarios'
    '''


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
