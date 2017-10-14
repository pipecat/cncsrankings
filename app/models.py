#-*- coding:utf-8 -*-
import hashlib
import requests
from time import sleep
from flask import current_app, request, url_for
from xml_parser import parse_xml
from .spider import AuthorHandler
from . import db



class Work(db.Model):
	__tablename__ = 'works'
	id = db.Column(db.Integer, primary_key=True)
	year = db.Column(db.Integer)
	key = db.Column(db.String(128), unique=True, index=True)
	alias = db.Column(db.String(128))
	type = db.Column(db.String(128))
	title = db.Column(db.String(128))
	institute = db.Column(db.String(128))
	adjusted_count = db.Column(db.Float)
	ee = db.Column(db.String(128))
	booktitle = db.Column(db.String(128))
	real_url = db.Column(db.String(128))
	keyword = db.Column(db.String(128))
	matched = db.Column(db.Boolean, default=False)


	def __init__(self, **kwargs):
		super(Work, self).__init__(**kwargs)
		self.real_url = ''
		pass


	@staticmethod
	def generate_works():
		pass

	def to_json(self):
		if self.matched:
			json_post = {
				'id': self.id,
				'title': self.title,
				'author': self.alias,
				'institue': self.institute,
				'key': self.key,
				'type': self.type,
				'year': self.year,
				'adjusted_count': self.adjusted_count,
				'booktitle': self.booktitle,
				'ee': self.ee,
				'matched': self.matched
			}
		else:
			json_post = {
				'id': self.id,
				'matched': self.matched
			}
		return json_post

	@staticmethod
	def from_json():
		pass

	@staticmethod
	def generate_works():
		parse_xml.parse_xml()

	@staticmethod
	def generate_real_url():
		works = Work.query.all()
		headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'
		}
		error_index = [673, 989, 1436, 1927, 2161, 2190,2638, 3023, 3026, 3033, 3665, 3880, 4430, 5340 ,6691, 9605, 9613, 2141, 9898, 9942, 10074, 10182, 10626, 10627, 10628, 10629, 10820, 10927, 11131, 11189, 11190, 11598, 11649, 11758]
		for work in works:
			if works.index(work) > 11500:
				print works.index(work), ' '
				if works.index(work) in error_index:
					continue
				if work.real_url == '' and work.ee != '':
					res = requests.get(work.ee, headers = headers, timeout=5)
					if res.status_code == 200:
						work.real_url = res.url
						print work.id, 'success', work.real_url
						#sleep(3)
					else:
						print work.id, 'error  ', res.status_code
				else:
					print work.real_url
				db.session.add(work)
		db.session.commit()

	@staticmethod
	def generate_matched():
		works = Work.query.all()
		for work in works:
			if not work.matched and works.index(work) > 10000:
				if 'acm' in work.real_url or 'ieee' in work.real_url:
					print works.index(work), ' '
					print work.real_url
					handler = AuthorHandler(work.alias, work.real_url)
					handler.parse_self()
					try:
						affiliation = handler.info['affiliation'].lower()
					except:
						continue
					keywords_list = work.keyword.split('/')
					for keywords in keywords_list:
						temp = 1
						keywords = keywords.split(':')
						for keyword in keywords:
							if keyword not in affiliation:
								temp = 0
						if temp == 1:
							work.matched = True
							print '-----------success!!!!!!!!------------'
							print keywords, affiliation, work.matched
							db.session.add(work)
							db.session.commit()
							break
					sleep(2)
		



class MatchedWork(Work):
	
	def is_matched():
		return self.matched

def Generate_all():
	Work.generate_works()
	Work.generate_real_url()
	Work.generate_matched()
	print 'End...'