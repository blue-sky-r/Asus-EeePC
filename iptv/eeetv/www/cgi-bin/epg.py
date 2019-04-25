#!/usr/bin/python
# -*- coding: utf-8 -*-

# EPG module
#
# gets EPG by web scrapping
#

import requests
import datetime
import re
import sqlite3
import sys
import json
import os

__VERSION__ = "2019.04.25"

__ABOUT__ = "= EPG cli module ver. %s for mpv wifi remote contoller =" % (__VERSION__)

# absolute dir to this file
#
ADIR = os.path.abspath(os.path.dirname(__file__))

# relative path from this file
#
DBFILE = '%s/../tmp/epg.db' % ADIR

CACHE = {
    'active': True,
    'dir': '%s/../tmp/www-cache' % ADIR,
    'filename': '%(dir)s/%(dtime)s-%(key)s.html'
}

# preconfigured file locations
#
__FLOC__ = "= db: %s = cache: %s =" % (DBFILE, CACHE['dir'])

CFG = {
    # name
    'tv-program.sk': {
        # user-agent
        'ua': 'Mozilla/5.0 (Tablet; rv:26.0) Gecko/26.0 Firefox/26.0',
        # urls
        'timetable': 'https://tv-program.sk',
        'detail':    'https://tv-program.sk/popisy.phtml'
    }
}

GENRE = {
    0: '',
    1: 'Film',
    2: 'Seriál',
    3: 'Pre deti',
    4: 'Erotika',
    5: 'Spravodajstvo',
    6: 'Dokument',
    7: 'Ostatné'
}

# https://en.wikipedia.org/wiki/Block_Elements
PROGRESS = u'░█'    #.encode('utf8')
#PROGRESS = '_#'

DBG = 0

# mega cookie
# |STV1:|STV2:|DISCOVERY:|DISCOVERYS:|FASHIONTV:|OCKO:|RETRO:|SPEKTRUM:|VIAHISTORY:|AXN:|AXNCRIME:|AXNSCIFI:|BARRANDOVFAMILY:|BARRANDOVPLUS:|CNN:|BBCWORLD:|COOLTV:|CT24:|DISCOVERYID:|FILMEUROPE:|NONSTOPKINO:|FILMBOXEXTRA:|FILMBOXFAMILY:|HBO:|HBO2:|HBO3:|KINOBARRANDOV:|KINOSVET:|NATIONALG:|ANIMAL:|SMICHOV:|OCKOGOLD:|PRIMALOVE:|PRIMAPLUS:|TVDEKO:|TA3:|TLC:|TVBARRANDOV:|TVLUX:|TVPAPRIKA:|TV8:|VIAEXPLORER:|VIANATURE:|WAU:|-|DAJTO:|DOMA:|MARKIZA:|-|JOJ:|JOJPLUS:|JOJFAMILY:|JOJCINEMA:|FILM+:|FILMBOX:|CSFILM:|CINEMAX2:|CINEMAX:|MGM:|-|CT1:|CT2:|NOVA:|FANDA:|TELKA:|NOVACINEMA:|PRIMA:|PRIMACOOL:|PRIMAZOOM:|PRIMAMAX:|
# playlist title -> tvid
# awk -F, '/#EXTINF:/ {print $2}'  tv.m3u8
# awk -F, '/#EXTINF:/ {printf "\x27%s\x27: \x27%s\x27,\n",$2,$2}'  tv.m3u8
# default title == tvid so it can be omitted
TITLE2TVID = {
    'Dajto': 'DAJTO',
    'Doma': 'DOMA',
    'Joj Family': 'JOJFAMILY',
    'Joj': 'JOJ',
    'Joj+': 'JOJPLUS',
    'Markíza': 'MARKIZA',
    'STV1': 'STV1',
    'STV2': 'STV2',
    'STV3': 'STV3',
    'STV4': 'STV4',
    'TA3': 'TA3',
    #'TV Hronka': 'TV Hronka',
    'Joj Cinema': 'JOJCINEMA',
    'Wau': 'WAU',
    'Lux': 'TVLUX',
    'Osem': 'TV8',
    'ČT1': 'CT1',
    'ČT2': 'CT2',
    'ČT24': 'CT24',
    'Spektrum': 'SPEKTRUM',
    'Via History': 'VIAHISTORY',
    #'History HD': 'History HD',
    'Discovery': 'DISCOVERY',
    'Science': 'DISCOVERYS',
    #'Ceskoslovensko HD': 'Ceskoslovensko HD',
    'CS Film': 'CSFILM',
    'Film+': 'FILM+',
    'Prima': 'PRIMA',
    'Prima Cool': 'PRIMACOOL',
    'Prima Zoom': 'PRIMAZOOM',
    'Prima Max': 'PRIMAMAX',
    'FilmBox': 'FILMBOX',
    'FilmBox Extra': 'FILMBOXEXTRA',
    'FilmBox Family': 'FILMBOXFAMILY',
    'FilmBox+': 'NONSTOPKINO',
    'Film EU': 'FILMEUROPE',
    'Nova': 'NOVA',
    'Nova Action': 'FANDA',
    'Nova Gold': 'TELKA',
    'Nova Cinema': 'NOVACINEMA',
    'amc': 'MGM',
    'Cinemax': 'CINEMAX',
    'Cinemax 2': 'CINEMAX2',
    'HBO': 'HBO',
    'HBO 2': 'HBO2',
    'HBO 3': 'HBO3',
    'Kino svet': 'KINOSVET',
    'Fashion TV': 'FASHIONTV',
    'Elektrik TV': 'Elektrik TV',
    #'TV Paprika': 'TVPAPRIKA',
    #'TV Raj': 'TV Raj',
    'Očko Gold': 'OCKOGOLD',
    'Retro': 'RETRO',
    # zatial neaktivne
    'AXN': 'AXN',
    'AXN W': 'AXNCRIME',
    'AXN B': 'AXNSCIFI',
    'Brdv.Family': 'BARRANDOVFAMILY',
    'Brdv+': 'BARRANDOVPLUS',
    'Brdv. Kino': 'KINOBARRANDOV',
    'TV Barrandov': 'TVBARRANDOV',
    'Investigation': 'DISCOVERYID',
    'CNN': 'CNN',
    'BBC': 'BBCWORLD',
    'Cool TV': 'COOLTV',
    'Nat.Geo.': 'NATIONALG',
    'Animal': 'ANIMAL',
    'Smichov': 'SMICHOV',
    'Prima Love': 'PRIMALOVE',
    'Prima Plus': 'PRIMAPLUS',
    'tv deko': 'TVDEKO',
    'TLC': 'TLC',
    'Via.Explore': 'VIAEXPLORER',
    'Via.Nature': 'VIANATURE',
}

# process only channels
# CHN = ['stv1', 'stv2']
CHN = TITLE2TVID.values()

# Suppress warnings: InsecurePlatformWarning, SNIMissingWarning
# https://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package
# fix: pip install requests urllib3 pyOpenSSL --force --upgrade; pip install pyOpenSSL==16.2.0
#import requests.packages.urllib3
#requests.packages.urllib3.disable_warnings()

def dbg(level, msg):
    """ debug output """
    if level > DBG: return
    print "DBG:",msg


# NOT USED right now
class hdatetime:
    """ human readable date-time format """

    # internal format
    _format_ = '%Y%m%d%H%M'

    # internal (integer) value in format _format_
    _val_ = None

    def __init__(self, format=None):
        """ init - optional format """
        if format:
            self._format_ = format

    def from_datetime(self, dt):
        """ set value from datetime dt """
        self._val_ = int(dt.strftime(self._format_))
        return self

    def from_str(self, str, strformat=None):
        """ set value from date-time string with optional format strformat """
        dt = datetime.datetime.strptime(str, strformat if strformat else self._format_)
        return self.from_datetime(dt)

    def from_int(self, idt, idtformat=None):
        """ set value from integer dt with optional format idtformat """
        if idtformat:
            idt = self.from_str("%s" % idt, idtformat)
        self._val_ = idt
        return self

    def from_unixtime(self, unixtime):
        """ set value from unixtime """
        dt = datetime.datetime.fromtimestamp(unixtime)
        return self.from_datetime(dt)

    def to_datetime(self):
        """ get datetime object """
        dt = datetime.datetime.strptime("%s" % self._val_, self._format_)
        return dt

    def to_str(self, format=None):
        """ get string with optional format """
        dt = self.to_datetime()
        str = dt.strftime(format if format else self._format_)
        return str

    def to_int(self, format=None):
        """ get integer with optional format """
        return int(self.to_str(format))

    def to_unixtime(self):
        """ get unixtime """
        dt = self.to_datetime()
        sec = int(dt.strftime("%s"))
        return sec

    def rectify(self, yymdhm):
        """ init from possible invalid format like hours over 24 """
        dt = datetime.datetime(year=int(yymdhm[:4]), month=int(yymdhm[4:6]), day=int(yymdhm[6:8]))
        # add time to date
        dt += datetime.timedelta(hours=int(yymdhm[8:10]), minutes=int(yymdhm[10:12]))
        #
        return self.from_datetime(dt)


class FileCache:

    text = None

    def __init__(self, cfg, dtime):
        self.active = cfg.get('active', True)
        self.dir = cfg.get('dir','/tmp')
        self.filename = cfg.get('filename', '%(dtime)s-%(key)s.html')
        self.dtime = dtime
        self.text = None
        #

    def makedir(self, dir):
        """ try to make storage directory """
        try:
            os.makedirs(dir)
        except OSError as e:
            dbg(1, 'FileCache.store() makedirs(%s) error %d - %s' % (dir, e.errno, e.strerror))

    def store(self, key, val):
        """ store """
        if not self.active: return
        # try to make storage directory
        self.makedir(self.dir)
        path = self.filename % { 'dir': self.dir, 'dtime': self.dtime, 'key': key }
        with open(path, 'w') as f:
            f.write(val.encode('utf8'))
        dbg(4, 'cache.store(key=%s) wrote file:%s' % (key, path))
        return self

    def load(self, key):
        """ load """
        if not self.active: return
        path = self.filename % {'dir': self.dir, 'dtime': self.dtime, 'key': key }
        try:
            with open(path, 'r') as f:
                self.text = f.read().decode('utf8')
            dbg(4, 'cache.load(key=%s) loaded file:%s' % (key,path))
            return self
        except:
            dbg(4, 'cache.load(key=%s) missing file:%s' % (key, path))
            self.text = None

    def remove(self, key='*'):
        """ clear all matching keys """
        path = self.filename % {'dir': self.dir, 'dtime': self.dtime, 'key': key}
        if os.path.exists(path):
            os.unlink(path)
            dbg(4, 'cache.remove(key=%s) ok file:%s' % (key, path))
        return self


class ScrapWWW:

    def __init__(self, cfg):
        self.cfg = cfg

    def data_lst_dict(self, dtime, channels):
        """ get list of dict as data scrapped from www """
        # get www time-table
        html = self.get_html_timetable(self.cfg.get('timetable'), dtime, channels, self.cfg.get('ua'))
        tt = self.parse_timetable_js(html)
        # details
        html = self.get_html_details(self.cfg.get('detail'), dtime, channels, self.cfg.get('ua'))
        dd = self.parse_details_js(html)
        # rectify
        epg_lst = self.rectify_dict2lst(tt, dd)
        # return
        return epg_lst

    def get_html_timetable(self, www, ymd, channels, useragent='IE'):
        """ get html page with tv program from local cache or from remote server """
        dbg(3, 'get_html_timetable(www=%s, ymd=%s, channels=%s)' % (www,ymd,channels))
        key = 'timetab'
        cache = FileCache(CACHE, dtime=ymd)
        r = cache.load(key)
        if not r:
            headers = {
                'user-agent': useragent
            }
            cookies = {
                'tvprogramy2': '|%s:|' % ':|'.join([n.upper() for n in channels])
            }
            # wget --no-cookies --header "Cookie: tvprogramy2=|DISCOVERYS:|" -O - https://tv-program.sk/
            r = requests.get(www, headers=headers, cookies=cookies)
            #r.encoding = r.apparent_encoding
            r.encoding = 'windows-1250'
            # cache
            cache.store(key, r.text)
        return r

    def parse_timetable_js(self, html):
        """ parse corresponding raw javascript code to python dictionaries """
        js = False
        # f['DISCOVERYS_1']='6';
        # cas['DISCOVERYS_1']="05:12";casdo['DISCOVERYS_1']="06:00";
        # n['DISCOVERYS_1']="Jak funguje vesmír 5: Záhada 9. planety 1";
        # t['DISCOVERYS_1']="1";
        # w['DISCOVERYS_1']="20190406/jakfungujevesmirzahadaplanety";
        f, cas, casdo, n, t, w = {}, {}, {}, {}, {}, {}
        for line in html.text.splitlines():
            line = line.strip()
            if js and line.upper() == '</SCRIPT>':
                js = False
            if js and line.startswith("f['") and line.endswith('";'):
                dbg(9, 'parse_timetable_js() js code:%s' % line.encode('utf-8'))
                eval(compile(line, 'javascript', 'single'))
            if line.upper() == '<SCRIPT>':
                js = True
        return {
            'genre': f,
            'start': cas,
            'end': casdo,
            'title': n,
            't': t,
            'w': w
        }

    def get_html_details(self, www, ymd, channels, useragent='IE'):
        """ program item details for date and channel """
        key = 'details'
        cache = FileCache(CACHE, dtime=ymd)
        r = cache.load(key)
        if not r:
            headers = {
                'user-agent': useragent
            }
            data = {
                'D': ymd,
                'P': '|%s:|' % ':|'.join([n.upper() for n in channels])
            }
            # wget -O - "https://tv-program.sk/popisy.phtml?D=20190330&P=|MGM:|"
            r = requests.get(www, params=data, headers=headers)
            #r.encoding = r.apparent_encoding
            r.encoding = 'windows-1250'
            # cache
            cache.store(key, r.text)
        return r

    def parse_details_js(self, html):
        """ parse corresponding raw javascript code to python dictionaries """
        # p['STV1_1']=" MP (Slovensk� republika) <BR>Re�lna d��ka: 40 min�t<BR>Rok vydania: 2019<BR>"
        p = {}
        for line in html.text.splitlines():
            line = line.strip()
            # process only lines p['.....";
            if line.startswith("p['") and line.endswith('";'):
                for subline in line.replace(';p',';\np').splitlines():
                    dbg(9, 'parse_details_js() js code:%s' % subline.encode('utf-8'))
                    eval(compile(subline, 'javascript', 'single'))
        return p

    def adjust_datetime2int(self, ymdhm):
        """ adjust datetimestr if time is over midnight (over 24) """
        # cas['STV1_29']="24:10";casdo['STV1_29']="25:00";
        d  = datetime.datetime(year=int(ymdhm[:4]), month=int(ymdhm[4:6]), day=int(ymdhm[6:8]))
        # add time to date
        d += datetime.timedelta(hours=int(ymdhm[8:10]), minutes=int(ymdhm[10:12]))
        # to string -> to int
        i = int(d.strftime('%Y%m%d%H%M'))
        return i

    def html_decode(self, html):
        """ decode html entities"""
        return html.replace('&quot;', "'")

    def rectify_dict2lst(self, d, detail):
        """ process/rectify dictionary values """
        result = []
        for k,v in d['start'].items():
            date, titlepacked = d['w'][k].split('/')
            start_dt = self.adjust_datetime2int(date + d['start'][k].replace(':',''))
            end_dt   = self.adjust_datetime2int(date + d['end'][k].replace(':', ''))
            title = d['title'][k]
            genre = int(d['genre'][k])
            tvid, _ = k.split('_')
            # details
            detail_stars, detail_year, detail_country, detail_desc = '', '', '', ''
            for txt in detail[k].split('<BR>'):
                m = re.match('Hrajú:(.+)', txt)
                if m:
                    detail_stars = m.group(1).strip()
                    continue
                m = re.match('Rok vydania: (\d+)', txt)
                if m:
                    detail_year = int(m.group(1))
                    continue
                m = re.search('^(.+)\(([^)]+)\)\s*$',txt)
                if m:
                    detail_country = m.group(2).strip()
                    detail_desc    = m.group(1).strip()
                if not detail_desc:
                    detail_desc = txt.strip()
            #
            item = {
                'tvid': tvid,
                'start_dt': start_dt,
                'end_dt': end_dt,
                'title': self.html_decode(title.decode('utf8')),
                'genre': genre,
                'desc': detail_desc.decode('utf8'),
                'year': detail_year,
                'stars': detail_stars.decode('utf8'),
                'country': detail_country.decode('utf8')
            }
            dbg(9, 'rectify_dict2lst() added item:%s' % item)
            result.append(item)
        #
        return result


class DB:

    def __init__(self, dbfile):
        """ init """
        # touch file if does not exist
        if not os.path.exists(dbfile): open(dbfile, 'a').close()
        # connect
        self.dbh = sqlite3.connect(dbfile)
        self.dbh.row_factory = sqlite3.Row
        self.cur = self.dbh.cursor()

    def create(self, drop=False):
        """ create EPG table (optional drop) """
        if drop:
            self.cur.execute('drop table EPG')
        #
        sql = ( 'create table if not exists EPG '
                '('
                'tvid text, '
                'start_dt text, '
                'end_dt text, '
                'genre integer, '
                'title text, '
                'year integer, '
                'desc text, '
                'stars text, '
                'country text,'
                'primary key(tvid, start_dt)'
                ')'
        )
        self.cur.execute(sql)

    def purge(self, days):
        """ purge everything older than days """
        sql_tpl = ('delete from EPG '
                   'where '
                   'start_dt < strftime(\'%(format)s\', \'now\', \'-%(days)d days\')'
                   )
        # offset = 0:
        sql_par = {
            'format': '%Y%m%d0000',
            'days': int(days)
        }
        # construct sql
        sql = sql_tpl % sql_par
        #
        dbg(5, "DB.purge() SQL(%s)" % sql)
        #
        self.cur.execute(sql)

    def put(self, data):
        sql = ( 'insert or ignore into EPG '
                '(tvid, start_dt, end_dt, genre, title, year, desc, stars, country) '
                'values '
                '(:tvid, :start_dt, :end_dt, :genre, :title, :year, :desc, :stars, :country )'
        )
        dbg(5, "DB.put() SQL(%s) PAR(%s)" % (sql, data))
        self.cur.execute(sql, data)

    def get(self, tvid, dtime, offset=0):
        sql_tpl = ( 'select * from EPG '
                    'where '
                        'tvid=:tvid and %(dtime)s '
                    'order by start_dt %(order)s '
                    'limit 1 offset %(offset)d'
        )
        # offset = 0:
        sql_par = {
            'order': 'ASC',
            'offset': 0,
            'dtime': 'start_dt <= :dtime and :dtime < end_dt'
        }
        if offset > 0:
            sql_par = {
                'order': 'ASC',
                'offset': offset-1,
                'dtime': 'start_dt > :dtime'
            }
        if offset < 0:
            sql_par = {
                'order': 'DESC',
                'offset': abs(offset)-1,
                'dtime': 'end_dt < :dtime'
            }
        # sql placeholders
        data = {
            'tvid': tvid,
            'dtime': int(dtime)
        }
        # construct sql
        sql = sql_tpl % sql_par
        #
        dbg(5, "DB.get() SQL(%s) PAR(%s)" % (sql, data))
        #
        self.cur.execute(sql, data)
        r = self.cur.fetchone()
        #return dict( [ (self.cur.description[i][0], v) for i,v in enumerate(r) ] ) if r else {}
        return dict(r)

    def get_list(self, tvid, dtime, limit, offset=0):
        sql = ( 'select tvid, start_dt, title from EPG '
                'where '
                   'tvid=:tvid and start_dt > :dtime '
                'order by start_dt ASC '
                'limit :limit offset :offset'
        )
        # sql placeholders
        data = {
            'tvid':   tvid,
            'dtime':  int(dtime),
            'limit':  limit,
            'offset': offset
        }
        #
        dbg(5, "DB.get_list() SQL(%s) PAR(%s)" % (sql, data))
        #
        self.cur.execute(sql, data)
        r = self.cur.fetchall()
        return [ dict(row) for row in r ]

    def transaction(self, action):
        """ https://stackoverflow.com/questions/9773200/python-sqlite3-cannot-commit-no-transaction-is-active """
        if action.lower() == 'commit':
            self.dbh.commit()
        elif action.lower() == 'rollback':
            self.dbh.rollback()
        # begin transaction is automatic
        return

    def close(self):
        self.cur.close()
        self.dbh.commit()
        self.dbh.close()


class Epg:

    def load(self, cfgname, dtime, channels, drop=False):
        """ load database from web """
        dbg(4, "Epg.load(cfgname=%s, dtime=%s, channels=%s)" % (cfgname, dtime, channels))
        # get data from www
        www = ScrapWWW(CFG[cfgname])

        # store to the database
        local_db = DB(DBFILE)
        local_db.create(drop)

        local_db.transaction('begin')
        for epg in www.data_lst_dict(dtime, channels):
            local_db.put(epg)
        local_db.transaction('commit')

        # a = local_db.get('STV0', '201904101959')
        local_db.close()

    def purge(self, days):
        """ purge epg entries older than days days """
        local_db = DB(DBFILE)
        local_db.purge(days)
        local_db.close()

    def get(self, tvid, dtime, offset=0, barsize=25, format='json'):
        """ get eg for dtime and tvid with offset in format """
        # local database
        local_db = DB(DBFILE)
        epg = local_db.get(tvid, dtime, offset)
        # add progress bar
        if epg: epg['bar'] = self.progress_bar(epg['start_dt'], epg['end_dt'], dtime, barsize)
        if format == 'json':
            print(json.dumps(epg, ensure_ascii=True, encoding="utf-8"))
        else:
            print(epg)
        local_db.close()

    def get_list(self, tvid, dtime, limit, offset=0, format='json'):
        """ get epg list for tvid starting after time  dtime limit to limit """
        # local database
        local_db = DB(DBFILE)
        epg = local_db.get_list(tvid, dtime, limit, offset)
        if format == 'json':
            print(json.dumps(epg, ensure_ascii=True, encoding="utf-8"))
        else:
            print(epg)
        local_db.close()

    def progress_bar(self, start_dt, end_dt, now_dt, sizex=25):
        """ semigraphic progress bar val=0..1 sizex= width in characters """
        start_time = datetime.datetime.strptime(start_dt, '%Y%m%d%H%M')
        end_time   = datetime.datetime.strptime(end_dt, '%Y%m%d%H%M')
        now_time   = datetime.datetime.strptime("%s" % now_dt, '%Y%m%d%H%M')
        # sanity check - now_time is within start_time and end_time
        val = (now_time - start_time).total_seconds() / (end_time - start_time).total_seconds()
        # limit min/max for already ended / not started yet
        val = max(min(val, 1), 0)
        # val = 0 ... 1.0
        n = int(round(sizex * val))
        # dbg
        dbg(5, "progress_bar() VAR: val(%.2f) sizex(%d) n(%s)" % (val, sizex, n))
        # construct string
        return PROGRESS[1] * n + PROGRESS[0] * (sizex-n)

    def remove_dia(self, s):
        """ remove diacritics """
        #tx = {
        #    'dia':   u'ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝßàáâãäåçèéêëìíîïñòóôõöùúûüýÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽž',
        #    'ascii':  'AAAAAACEEEEIIIINOOOOOUUUUYsaaaaaaceeeeiiiinooooouuuuyyAaAaAaCcCcCcCcDdDdEeEeEeEeEeGgGgGgGgHhHhIiIiIiIiIiKkkLlLlLlLlLlNnNnNnNnNOoOoOoRrRrRrSsSsSsSsTtTtTtUuUuUuUuUuUuWwYyYZzZzZz',
        #}
        return ''.join([ c for c in s if ord(c) < 128 ])

    def title_2_tvid(self, title, casesensitive=False):
        """ channel/playlist title -> epg tvid """
        # not fount -> capitalize title and remove spaces
        default = self.remove_dia(title.upper().replace(' ',''))
        # remove diacritics
        #default = unicodedata.normalize('NFKD', default).encode('ASCII', 'ignore')
        if casesensitive:
            return TITLE2TVID.get(title, default)
        # case insensitive search
        for key,val in TITLE2TVID.items():
            if key.lower() == title.lower():
                return val
        # not fount -> capitalize title and remove spaces
        return default

_usage_ = """
%s

%s [-dbg 10] [-drop] [-tvid STV1] -load cfg-name

%s [-dbg 10] [-purge 7d] [-tvid STV1] -load cfg-name

%s [-dbg 10] -title STV1 [-dtime 201931122355] [-offset -5] [-bar 30] -epg

%s [-dbg 10] -title STV1 [-dtime 201931122355] -epg-list 10

%s
""" % (__ABOUT__, sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0],   __FLOC__)

def usage():
    """ show usage """
    if len(sys.argv) > 1: return
    print _usage_
    sys.exit(1)

if __name__ == '__main__':

    # defaults
    #
    yymd, hhmm = datetime.datetime.now().strftime('%Y%m%d %H%M').split()
    dtime, offset, barsize = '%s%s' % (yymd, hhmm), 0, 25
    tvid, channels = None, []
    drop = False

    usage()

    epg = Epg()

    # parse
    #
    arg = iter(sys.argv[1:])
    for par in arg:

        # verbose / debug
        if par in ['-dbg', '-debug', '-v', '-verbose']:
            DBG = int(next(arg))
            dbg(5, "VAR: DEFAULTS yymd(%s) hhmm(%s) dtime(%s) offset(%d) barsize(%d)" % (yymd, hhmm, dtime, offset, barsize))
            continue

        # purge old data from db
        if par in ['-p', '-purge']:
            # extract only number from next parameter like: -7 days, 7d, ...
            days = re.findall('\d+', next(arg))[0]
            dbg(5, "VAR: days(%s)" % days)
            epg.purge(days)
            continue

        # drop/init db table
        if par in ['-drop', '-init']:
            drop = True
            continue

        # datetime
        if par in ['-d', '-ymdhm', '-date', '-dtime']:
            dtime = next(arg)
            yymd, hhmm = dtime[:8], dtime[9:]
            if not hhmm: hhmm = '0000'
            dbg(5, "VAR: yymd(%s) hhmm(%s) dtime(%s)" % (yymd, hhmm, dtime))
            continue

        # load
        if par in ['-l', '-load']:
            cfgname = next(arg)
            # no channels specified so retrieve all
            if not channels: channels = CHN
            epg.load(cfgname, yymd, channels, drop)
            continue

        # channel id
        if par in ['-i', '-id', '-tvid']:
            tvid = next(arg).upper()
            channels.append(tvid)
            continue

        # playlist title
        if par in ['-t', '-title']:
            title = next(arg)
            tvid = epg.title_2_tvid(title)
            channels.append(tvid)
            continue

        # progress-bar size
        if par in ['-b', '-bar']:
            barsize = int(next(arg))
            continue

        # offset
        if par in ['-o', '-offset']:
            offset = int(next(arg))
            continue

        # epg
        if par in ['-e', '-epg']:
            dbg(5, "VAR: tvid(%s) dtime(%s) offset(%d) barsize(%d)" % (tvid, dtime, offset, barsize))
            epg.get(tvid, dtime, offset, barsize)
            continue

        # epg-list
        if par in ['-t', '-epg-list']:
            limit = int(next(arg))
            dbg(5, "VAR: tvid(%s) dtime(%s) limit(%d) offset(%d)" % (tvid, dtime, limit, offset))
            epg.get_list(tvid, dtime, limit, offset)
            continue
    #

