import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = 'csrankings_secret_key'
	CSRANKINGS_WORKS_PER_PAGE = 2000000
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	USE_X_SENDFILE = False

	@staticmethod
	def init_app(app):
		pass



class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
			'sqlite:///' + os.path.join(basedir, 'data.sqlite')



class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
			'sqlite:///' + os.path.join(basedir, 'data.sqlite')



class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCT_DATABASE_URI') or \
			'sqlite:///' + os.path.join(basedir, 'data.sqlite')



config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'producton': ProductionConfig,

	'default': DevelopmentConfig,
}