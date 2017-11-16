#-*- coding:utf-8 -*-
import csv
import sqlite3
import xml
from xml.sax import ContentHandler
from xml.sax import parseString

aliases = set()

institute_dict = {}

keyword_dict = {}

with open('./alias-name.csv', 'r') as f:
    f_csv = csv.reader(f)
    headers = next(f_csv)
    line = 0
    error_lines = []
    for row in f_csv:
        line += 1
        if len(row) != 4:
            error_lines.append(line)
            continue
        aliases.add(unicode(row[0]))  # 添加入aliases
        institute_dict[unicode(row[0])] = row[2].decode('utf-8')
        keyword_dict[unicode(row[0])] = row[3].decode('utf-8')
        #print row[0].decode('ascii').encode('utf-8')
    for _line in error_lines:
        print('第' + str(_line) + '行出错了！')
    f.close()


def find_institute(_alias):
    return institute_dict[_alias]

def find_keyword(_alias):
    return keyword_dict[_alias]

def check_workinfo(work):
    if work.get('key') and work.get('title') and work.get('year') and work.get('author'):
        return True
    else:
        return False

class WorkHandler(ContentHandler):

    def __init__(self):
        self.cur_tag = ''
        self.work = {}
        self.is_required = False
        self.in_queto = False

    def startElement(self, name, attrs):
        self.in_queto = True
        self.cur_tag = name
        if name == 'inproceedings':
            self.is_required = True
            self.work = {}
            self.work['type'] = name
            self.work['key'] = attrs.get('key')
            self.work['author'] = set()
            self.work['ee'] = ''
            self.work['booktitle'] = ''
        if name == 'article':
            self.work = {}
            self.work['key'] = attrs.get('key')
            self.work['type'] = name
            self.work['author'] = set()
            self.work['ee'] = ''
            self.work['booktitle'] = ''
            key = attrs.get('key')
            
            if 'journals' in key:
                self.is_required = True
                #print self.work['key']

    def endElement(self, name):
        self.in_queto = False
        if name == 'inproceedings' or name == 'article':
            if self.is_required and check_workinfo(self.work):
                _aliases = list(self.work['author'].intersection(aliases))
                _key = self.work['key']
                _type = self.work['type']
                _title = self.work['title']
                _year = self.work['year']
                _ee = self.work['ee']
                try:
                    _booktitle = self.work['booktitle']
                except:
                    _booktitle = ''
                _adjustedcount = 1.0 / len(self.work['author'])
                for _alias in _aliases:
                    _institute = find_institute(_alias)
                    _keyword = find_keyword(_alias)
                    insert_work(_key, _alias, _type, _title,
                                _year, _institute, _adjustedcount, _ee, _booktitle, _keyword)
            self.is_required = False

    def characters(self, content):
        if self.in_queto and self.is_required:
            if self.cur_tag == 'title' or self.cur_tag == 'year' or self.cur_tag == 'ee' or self.cur_tag == 'booktitle':
                self.work[self.cur_tag] = content
            elif self.cur_tag == 'author':
                self.work[self.cur_tag].add(content)


def insert_work(_key, _alias, _type, _title, _year, _institute, _adjustedcount, _ee, _booktitle, _keyword):
    '''
    global ADD_COUNT
    global UPDATE_COUNT
    # 插入数据，如果插入不成功调用更新
    try:
        conn.execute(
            "INSERT INTO WORKS (KEY, ALIAS, TYPE, TITLE, YEAR, INSTITUTE, ADJUSTED_COUNT) VALUES (?,?,?,?,?,?,?)", (_key, _alias, _type, _title, _year, _institute, _adjustedcount))
        print('插入成功！')
    except sqlite3.IntegrityError as e:
        ADD_COUNT -= 1
        UPDATE_COUNT += 1
        conn.execute(
            "UPDATE WORKS SET ALIAS=(?), TYPE=(?), TITLE=(?), YEAR=(?), INSTITUTE=(?), ADJUSTED_COUNT=(?) WHERE KEY=(?)", (_alias, _type, _title, _year, _institute, _adjustedcount, _key))
        print('更新成功！')
    '''
    from ..models import Work
    from .. import db
    w = Work.query.filter_by(key=_key).first()
    if w is None:
        work = Work(
            id = Work.query.count()+1,
            year = _year,
            key = _key,
            alias = _alias,
            type = _type,
            title = _title,
            institute = _institute,
            adjusted_count = _adjustedcount,
            ee = _ee,
            booktitle = _booktitle,
            keyword = _keyword
           )
        db.session.add(work)
    else:
        w.year = _year
        w.alias = _alias
        w.type = _type
        w.title = _title
        w.institute = _institute
        w.adjusted_count = _adjustedcount
        w.ee = _ee
        w.booktitle = _booktitle
        w.keyword = _keyword
        db.session.add(w)
    db.session.commit()
    # 输出结果
    '''
    print '|alias:         | ' + _alias 
    print '|type:          | ' + _type 
    print '|title:         | ' + _title 
    print '|year:          | ' + _year 
    print '|institute:     | ' + _institute 
    print '|adjustedcount: | ' + str(_adjustedcount)
    print '|ee:            | ' + _ee
    print '|booktitle:     | ' + _booktitle
    print '---'
    '''

def parse_xml():
    print 'parsing xml document...'
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = WorkHandler()
    parser.setContentHandler(Handler)
    parser.parse('dblp.xml')
    print 'finish parsing...'



if __name__ == '__main__':
    parse_xml()