
import csv
import time
import sqlite3
import xml
from xml.sax import ContentHandler
from xml.sax import parseString

start = time.time()

conn = sqlite3.connect('./njupt-rankings.db')
cursor = conn.cursor()

# 获取所有的alias 用set存储

aliases = set()

with open('./alias-name.csv', 'r') as f:
    f_csv = csv.reader(f)
    headers = next(f_csv)
    line = 0
    error_lines = []
    for row in f_csv:
        line += 1
        if len(row) != 3:
            error_lines.append(line)
            continue
        aliases.add(row[0])  # 添加入aliases
    for _line in error_lines:
        print('第' + str(_line) + '行出错了！')
    f.close()

# WORKS是全部的作品，type标记类型(article, proceedings, inproceedings)
# 将来可能用area标记领域 暂时没考虑
try:
    print('正在创建WORKS表...')
    conn.execute('''CREATE TABLE WORKS (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        KEY CHAR(50) UNIQUE NOT NULL,
        ALIAS CHAR(50) NOT NULL,
        TYPE CHAR(20) NOT NULL,
        TITLE CHAR(150) NOT NULL,
        YEAR INTEGER NOT NULL,
        INSTITUTE CHAR(100) NOT NULL,
        ADJUSTED_COUNT REAL NOT NULL
    );''')
    conn.commit()
    print('创建成功！')
except sqlite3.DatabaseError:
    print('已跳过！')

print('---')

# 统计添加和更新的数据个数
ADD_COUNT = 0

UPDATE_COUNT = 0


def insert_work(_key, _alias, _type, _title, _year, _institute, _adjustedcount):
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
    # 输出结果
    print('|alias:         | ' + _alias)
    print('|type:          | ' + _type)
    print('|title:         | ' + _title)
    print('|year:          | ' + _year)
    print('|institute:     | ' + _institute)
    print('|adjustedcount: | ' + str(_adjustedcount))
    print('---')
    ADD_COUNT += 1
    conn.commit()


def find_institute(_alias):
    cursor.execute(
        "SELECT INSTITUTE FROM ALIAS_NAME WHERE ALIAS=(?)", (_alias,))
    _institute = cursor.fetchone()
    if not _institute:
        return None
    else:
        return _institute[0]


def check_workinfo(work):
    if work.get('key') and work.get('title') and work.get('year') and work.get('author'):
        return True
    else:
        return False


err_alias = []


class WorkHandler(ContentHandler):

    def __init__(self):
        self.cur_tag = ''
        self.work = {}
        self.is_required = False
        self.in_queto = False

    def startElement(self, name, attrs):
        self.in_queto = True
        self.cur_tag = name
        if name == 'article' or name == 'inproceedings' or name == 'proceedings':
            self.is_required = True
            self.work = {}
            self.work['type'] = name
            self.work['key'] = attrs.get('key')
            self.work['author'] = set()

    def endElement(self, name):
        self.in_queto = False
        if name == 'article' or name == 'inproceedings' or name == 'proceedings':
            if self.is_required and check_workinfo(self.work):
                _aliases = list(self.work['author'].intersection(aliases))
                _key = self.work['key']
                _type = self.work['type']
                _title = self.work['title']
                _year = self.work['year']
                _adjustedcount = 1.0 / len(self.work['author'])
                for _alias in _aliases:
                    _institute = find_institue(_alias)
                    insert_work(_key, _alias, _type, _title,
                                _year, _institute, _adjustedcount)
            self.is_required = False

    def characters(self, content):
        if self.in_queto and self.is_required:
            if self.cur_tag == 'title' or self.cur_tag == 'year':
                self.work[self.cur_tag] = content
            elif self.cur_tag == 'author':
                self.work[self.cur_tag].add(content)


if __name__ == '__main__':
    print('正在解析xml文档...')
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = WorkHandler()
    parser.setContentHandler(Handler)
    parser.parse('dblp.xml')
    # 结束时间
    end = time.time()
    conn.close()

    tot = end - start

    # 输出用时和操作结果
    print('总计用时 %dh %dm %ds' % (tot / 3600, (tot % 3600) / 60, tot % 60))
    print('添加: ' + str(ADD_COUNT))
    print('更新: ' + str(UPDATE_COUNT))

    if len(err_alias):
        print('错误的alias：')
        for alias in err_alias:
            print(alias)
