#-*- coding:utf-8 -*-
import hashlib
import requests
import grequests
import json
import random
import time
from itertools import islice
from time import sleep
from flask import current_app, request, url_for
from xml_parser import parse_xml, new_xml_parser
from .spider import AuthorHandler, No_Request_AuthorHandler, USER_AGENTS
from . import db



class Work(db.Model):
	__tablename__ = 'works'
	id = db.Column(db.Integer, primary_key=True)
	year = db.Column(db.Integer)
	key = db.Column(db.String(128), index=True)
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
		for work in works:
			if works.index(work) > 12138:
				print works.index(work), ' '
				if work.real_url == '' and work.ee != '':
					try:
						res = requests.get(work.ee, headers = headers, timeout=5)
						if res.status_code == 200:
							work.real_url = res.url
							print work.id, 'success', work.real_url
							#sleep(2)
						else:
							print work.id, 'error  ', res.status_code
						db.session.add(work)
						db.session.commit()
					except:
						pass
				else:
					print work.real_url


	@staticmethod
	def async_generate_matched():
		'''headers = {
			'User-Agent': 'Mozilla/5.0 (Linux; Android 4.3; Nexus 7 Build/JSS15Q) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
		}
		'''

		works = Work.query.all()
		works_iter = islice(works, 170000, None)
		while True:
			try:
				temp_works = []
				reqs = []
				for i in range(0,100):
					itering_work = next(works_iter)
					temp_works.append(itering_work)
					reqs.append(grequests.get(itering_work.ee, timeout=20, headers={'User-Agent':random.choice(USER_AGENTS)}))
				print 'Try to make works {}-{}...'.format(temp_works[0].id, temp_works[-1].id)
				start = time.time()
				results = grequests.map(reqs)
				length = len(reqs)
				#Lost remake
				for i in range(length):
					if results[i] is None or results[i].status_code != 200:
						
						try:
							results[i] = request.get(temp_works[i].ee, headers={'User-Agent':random.choice(USER_AGENTS)}, timeout=5)
						except:
								pass
						
						print 'Work:{} losted, ee:{}'.format(temp_works[i].id, temp_works[i].ee)
						#print results[i].status_code, results[i].url
				#Start parse
				end = time.time()
				for i in range(length):
					if temp_works[i] is None or (temp_works[i].real_url != '' and 'jsyd' not in temp_works[i].real_url):
						continue
					if results[i] is None:
						continue
					handler = No_Request_AuthorHandler(temp_works[i], results[i])
					id = temp_works[i].id 
					work = Work.query.filter_by(id=id).first()
					print work.id, work.alias, handler.res.url
					db.session.add(work)
					if not work.matched and work.id > 14078:
						handler.parse_self()
						work.real_url = handler.res.url
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
								break
				print 'Requested works {}-{}, costed {}s.'.format(temp_works[0].id, temp_works[-1].id, end-start)


			except StopIteration:
				print 'End'
				break
			db.session.commit()

	@staticmethod
	def async_generate_acm():
		'''headers = {
			'User-Agent': 'Mozilla/5.0 (Linux; Android 4.3; Nexus 7 Build/JSS15Q) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
		}
		'''

		works = Work.query.all()
		acm_works = []
		for work in works:
			if 'acm' in work.ee:
				acm_works.append(Work.query.filter_by(id=work.id).first())
		works_iter = islice(acm_works, 0, None)
		while True:
			try:
				temp_works = []
				reqs = []
				for i in range(0,100):
					itering_work = next(works_iter)
					temp_works.append(itering_work)
					reqs.append(grequests.get(itering_work.ee, timeout=20, headers={'User-Agent':random.choice(USER_AGENTS)}))
				print 'Try to make works {}-{}...'.format(temp_works[0].id, temp_works[-1].id)
				start = time.time()
				results = grequests.map(reqs)
				length = len(reqs)
				#Lost remake
				for i in range(length):
					if results[i] is None or results[i].status_code != 200:
						
						try:
							results[i] = request.get(temp_works[i].ee, headers={'User-Agent':random.choice(USER_AGENTS)}, timeout=5)
						except:
								pass
						try:
							print 'Work:{} losted, status:{}, ee:{}'.format(temp_works[i].id,results[i].status_code, temp_works[i].ee)
						except AttributeError:
							print 'Work:{} losted, status:None, ee:{}'.format(temp_works[i].id, temp_works[i].ee)
						#print results[i].status_code, results[i].url
				#Start parse
				end = time.time()
				for i in range(length):
					if temp_works[i] is None or (temp_works[i].real_url != '' and 'jsyd' not in temp_works[i].real_url):
						continue
					if results[i] is None:
						continue
					handler = No_Request_AuthorHandler(temp_works[i], results[i])
					id = temp_works[i].id 
					work = Work.query.filter_by(id=id).first()
					print work.id, work.alias, handler.res.url
					db.session.add(work)
					if not work.matched and work.id > 14078:
						handler.parse_self()
						print handler.info
						work.real_url = handler.res.url
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
								break
				print 'Requested works {}-{}, costed {}s.'.format(temp_works[0].id, temp_works[-1].id, end-start)


			except StopIteration:
				print 'End'
				break
			db.session.commit()

	@staticmethod
	def generate_matched():
		works = Work.query.all()

		with open('app/proxy.json', 'r') as f:
			data = json.loads(f.read())
		data = data['result']
		index = random.randint(1,len(data))
		proxy = data[index]['ip:port']
		proxies = {
			'http':proxy
		}
		print proxy


		for work in works:
			if not work.matched and works.index(work) > 14078:
				if 'acm' in work.real_url or 'ieee' in work.real_url or 'aaai' in work.real_url:
					print works.index(work), ' '
					print work.real_url
					handler = AuthorHandler(work.alias, work.real_url, proxies)
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
					sleep(3)

	@staticmethod
	def generate_matched_acm():
		works = Work.query.all()
		acm_works = []
		for work in works:
			if 'acm' in work.ee:
				acm_works.append(Work.query.filter_by(id=work.id).first())


		for work in acm_works:
			if not work.matched and works.index(work) > 0:
				#if 'acm' in work.real_url or 'ieee' in work.real_url or 'aaai' in work.real_url:
				print works.index(work), ' '
				print work.real_url
				handler = AuthorHandler(work.alias, work.ee)
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
	@staticmethod
	def generate_matched_TaoLi():
		works = Work.query.all()
		TaoLi_works = []
		for work in works:
			if 'Tao Li' in work.alias:
				TaoLi_works.append(Work.query.filter_by(id=work.id).first())


		for work in TaoLi_works:
			if not work.matched and works.index(work) > 0:
				#if 'acm' in work.real_url or 'ieee' in work.real_url or 'aaai' in work.real_url:
				print works.index(work), ' '
				handler = AuthorHandler(work.alias, work.ee)
				handler.parse_self()
				try:
					work.real_url = handler.res.url
					print handler.res.url
				except:
					print 'no ee...'
					continue
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
	@staticmethod
	def generate_taoli0001():
		new_xml_parser.parse_xml()
		generate_matched_TaoLi()
				


	@staticmethod
	def generate_json():
		works = Work.query.all()
		result = {}
		result['prev'] = None
		result['next'] = None
		posts = []
		with open('app/filters.json', 'r') as f:
			filters = json.loads(f.read())

		for work in works:
			keys = work.key.split('/')
			filter = keys[0] + '/' + keys[1]
			if work.matched and filter in filters:
				posts.append({
						'id': work.id,
						'title': work.title,
						'author': work.alias,
						'institue': work.institute,
						'key': work.key,
						'type': work.type,
						'year': work.year,
						'adjusted_count': work.adjusted_count,
						'booktitle': work.booktitle,
						'ee': work.ee,
						'matched': work.matched
					})
		result['posts'] = posts
		result['count'] = len(posts)
		with open('app/static/works.json', 'w') as f:
			f.write(json.dumps(result))



class MatchedWork(Work):
	
	def is_matched():
		return self.matched

def Generate_all():
	Work.generate_works()
	Work.generate_real_url()
	Work.generate_matched()
	print 'End...'