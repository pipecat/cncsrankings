import requests
from bs4 import BeautifulSoup
import re
import json
import random

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

class AuthorHandler():

    def __init__(self, author, ee):
        

        self.author = author
        self.ee = ee
        self.headers = {
            'User-Agent': random.choice(USER_AGENTS)
        }
        self.info = {}
        print 'Parsing ......'

        try:
            self.res = requests.get(self.ee, headers=self.headers, timeout=8)
            print 'status_code:', self.res.status_code
        except:
            print self.ee
            print "Can't connect this url..."

    def IEEEParser(self):
        parttern = re.compile('metadata=(.*?)};')
        try:
            json_string = re.findall(parttern, self.res.text)[0]
        except:
            return
        json_string += '}'
        data_dict = json.loads(json_string)
        authors = {}
        try:
            authors = data_dict['authors']
        except:
            pass
        for i in authors:
            try:
                if i['name'] == self.author:
                    self.info = i
            except:
                pass

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
        author_info['affiliation'] = ''
        bsobj = BeautifulSoup(self.res.text, 'lxml')
        authors = bsobj.select('.authors-affiliations__name')
        index_list = []
        for i in authors:
            if i.text.strip().replace(u'\xa0', u' ').replace(u'-', u'') == self.author:
                author_information = i.parent
                index_list = author_information.select('[data-affiliation]')
        for i in range(len(index_list)):
            index_list[i] = index_list[i].text.strip()

        affiliations = bsobj.select('.affiliation')
        '''
        for i in affiliations:
            num = i.select('.affiliation__count')[0].text.split('.')[0]
            if num in index_list:
                try:
                    author_info['affiliation'] += ',' + i.select('.affiliation__item')[0].text.strip()
                except KeyError:
                    author_info['affiliation'] = ',' + i.select('.affiliation__item')[0].text.strip()
        '''
        for affiliation in affiliations:
            if affiliation.text[0] in index_list:
                author_info['affiliation'] += affiliation.text
        self.info = author_info

    def AAAIParser(self):
        url = self.url
        url = url.replace('http://', 'https://')
        url = url + '/0'
        url = url.replace('paper/view', 'rt/bio')
        res = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(res.text, 'lxml')
        author_info = {}
        result = soup.findAll('em')
        for i in result:
            if i.text == self.author:
                author_info['affiliation'] = i.parent.contents[3].strip()
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



class No_Request_AuthorHandler():
    '''
    Content parser of response
    '''

    def __init__(self, work, res):
        self.author = work.alias
        self.ee = work.ee
        self.res = res
        self.info = {}
        print 'Parsing ......'

    def IEEEParser(self):
        parttern = re.compile('metadata=(.*?)};')
        try:
            json_string = re.findall(parttern, self.res.text)[0]
        except:
            return
        json_string += '}'
        data_dict = json.loads(json_string)
        authors = {}
        try:
            authors = data_dict['authors']
        except:
            pass
        for i in authors:
            try:
                if i['name'] == self.author:
                    self.info = i
            except:
                pass


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
        author_info['affiliation'] = ''
        bsobj = BeautifulSoup(self.res.text, 'lxml')
        authors = bsobj.select('.authors-affiliations__name')
        index_list = []
        for i in authors:
            if i.text.strip().replace(u'\xa0', u' ').replace(u'-', u'') == self.author:
                author_information = i.parent
                index_list = author_information.select('[data-affiliation]')
        for i in range(len(index_list)):
            index_list[i] = index_list[i].text.strip()

        affiliations = bsobj.select('.affiliation')
        '''
        for i in affiliations:
            num = i.select('.affiliation__count')[0].text.split('.')[0]
            if num in index_list:
                try:
                    author_info['affiliation'] += ',' + i.select('.affiliation__item')[0].text.strip()
                except KeyError:
                    author_info['affiliation'] = ',' + i.select('.affiliation__item')[0].text.strip()
        '''
        for affiliation in affiliations:
            if affiliation.text[0] in index_list:
                author_info['affiliation'] += affiliation.text
        self.info = author_info

    def AAAIParser(self):
        url = self.url
        url = url.replace('http://', 'https://')
        url = url + '/0'
        url = url.replace('paper/view', 'rt/bio')
        res = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(res.text, 'lxml')
        author_info = {}
        result = soup.findAll('em')
        for i in result:
            if i.text == self.author:
                author_info['affiliation'] = i.parent.contents[3].strip()
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
