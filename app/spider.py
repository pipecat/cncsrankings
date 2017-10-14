import requests
from bs4 import BeautifulSoup
import re
import json

class AuthorHandler():

    def __init__(self, author, ee):
        

        self.author = author
        self.ee = ee
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.3; Nexus 7 Build/JSS15Q) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        self.info = {}
        print 'Parsing ......'

        try:
            self.res = requests.get(self.ee, headers=self.headers, timeout=8)
            print 'status_code:', self.res.status_code
        except:
            print "Can't connect this url..."

    def IEEEParser(self):
        parttern = re.compile('metadata=(.*?)};')
        json_string = re.findall(parttern, self.res.text)[0]
        json_string += '}'
        data_dict = json.loads(json_string)
        try:
            authors = data_dict['authors']
        except:
            pass
        for i in authors:
            if i['name'] == self.author:
                self.info = i

    def ACMParser(self):
        bsobj = BeautifulSoup(self.res.text, 'lxml')
        author_list = bsobj.select('#divmain > table:nth-of-type(1) > tr > td > table:nth-of-type(2) > tr')
        for i in author_list:
            data = {}
            data['name'] = i.select('td')[1].text.strip()
            data['affiliation'] = i.select('td')[2].text.strip()
            if data['name'] == self.author:
                self.info = data

    def SpringerParser(self):
        '''
        Remember that there is always a ',' before every affiliation in $author_info
        '''
        author_info = {}
        author_info['name'] = self.author
        bsobj = BeautifulSoup(self.res.text, 'lxml')
        authors = bsobj.select('.authors-affiliations__name')
        index_list = []
        for i in authors:
            if i.text.strip().replace(u'\xa0', u' ') == self.author:
                author_info = i.parent
                index_list = author_info.select('[data-affiliation]')
        for i in range(len(index_list)):
            index_list[i] = index_list[i].text.strip()

        affiliations = bsobj.select('.affiliation')
        for i in affiliations:
            num = i.select('.affiliation__count')[0].text.split('.')[0]
            if num in index_list:
                try:
                    author_info['affiliation'] += ',' + i.select('.affiliation__item')[0].text.strip()
                except KeyError:
                    author_info['affiliation'] = ',' + i.select('.affiliation__item')[0].text.strip()
        self.info = author_info

    def SciencedirectParser(self):
        author_info = {}
        author_info['name'] = self.author
        bsobj = BeautifulSoup(self.res.text, 'lxml')

        affiliation_info = {}
        affiliations = bsobj.select('[class="affiliation authAffil"] > li')
        for affiliation in affiliations:
            index = i.select('sup')[0].text.strip()
            affiliation_info[index] = i.select('span')[0].text.strip()
        author_info = {}
        authors = bsobj.select('[class="authorGroup noCollab svAuthor"] > li')
        for author in authors:
            name =author.select('a')[0].text.strip()
            if name == self.author:
                indexes = author.select('sup')
                for index in indexes:
                    index = index.text.strip()
                    if index in affiliation_info:
                        try:
                            author_info['affiliation'] += ',' + affiliation_info[index]
                        except KeyError:
                            author_info['affiliation'] = ',' + affiliation_info[index]
        self.info = author_info


    def parse_self(self):
        domain = []
        try:
            domain = self.res.url.split('/')[2].split('.')
        except:
            pass
        if 'ieee' in domain:
            self.IEEEParser()
            print self.info
            return
        if 'acm' in domain:
            self.ACMParser()
            print self.info
            return
        if 'springer' in domain:
            self.SpringerParser()
            print self.info
            return
        if 'sciencedirect' in domain:
            self.SciencedirectParser()
            print self.info
            return
        print "Can't parse this url now..."