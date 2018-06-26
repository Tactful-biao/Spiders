from flask import Flask, request, render_template
from wtforms import Form, StringField, validators
from bs4 import BeautifulSoup
import pymysql
import re
from config import host, user, password, port, db, charset
import requests

movies = Flask(__name__)

class Movies:
    def __init__(self):
        self.db = pymysql.connect(host=host, user=user, password=password, port=port, db=db, charset=charset)
        self.cursor = self.db.cursor()
        self.juge = 'SELECT * FROM keyword WHERE id=%s'
        self.sql_kwd = 'INSERT INTO keyword(id, num) VALUES (%s, 1)'
        self.sql_movie = 'INSERT INTO movie(title, seed, size, addtime, kwd) VALUES (%s, %s, %s, %s, %s)'
        self.update = 'UPDATE keyword SET num = %s WHERE id = %s'
        self.select = 'SELECT * FROM movie WHERE kwd=%s'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Host': 'btdb.to',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }

    def movie(self, keyword):
        url = 'http://btdb.to/q/' + keyword + '/' + '1' + '?sort=popular'
        html = requests.get(url, headers=self.headers).content
        soup = BeautifulSoup(html, 'lxml')
        li = soup.find('ul', attrs={'class': 'search-ret-list'}).findAll('li', attrs={'class': 'search-ret-item'})
        self.cursor.execute(self.sql_kwd, keyword)
        for i in li:
            title = i.find('a')['title']
            size = i.find('div', attrs={'class': 'item-meta-info'}).find('span').getText()
            time = i.find('div', attrs={'class': 'item-meta-info'}).find_all('span')[2].getText()
            link = i.find('div', attrs={'class': 'item-meta-info'}).find('a')['href']
            link = link.replace(re.search('&.*', link).group(), '')
            self.cursor.execute(self.sql_movie, (title, link, size, time, keyword))
            self.db.commit()

    def movie3(self, keyword):
        url3 = 'https://m.zhongziso.com/list/' + str(keyword) + '/1'
        headers = {
            'accept-language': 'zh-CN,zh;q=0.8',
            'Host': 'm.zhongziso.com',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0",
            'Referer': "https://m.zhongziso.com/",
        }
        html = requests.get(url3, headers=headers).content
        soup = BeautifulSoup(html, 'lxml')
        con = soup.find(class_='panel-body')
        for ul in con.find_all('ul'):
            title = ul.find(class_='list-group-item').getText()
            size = ul.find(class_='text-size').getText()
            time = ul.find(class_='text-time').getText()
            link = ul.find(class_='btn btn-success')['href']
            self.cursor.execute(self.sql_movie, (title, link, size, time, keyword))
            self.db.commit()

class SearchForm(Form):
    search = StringField('search', [validators.DataRequired()])

@movies.route('/', methods=['GET', 'POST'])
def searcher():
    form = SearchForm(request.form)
    movie = Movies()
    if request.method == 'POST':
        keyword = form.search.data
        if movie.cursor.execute(movie.juge, keyword):
            weight = movie.cursor.fetchall()[0][1] + 1
            try:
                movie.cursor.execute(movie.update, (weight, keyword))
                movie.db.commit()
            except:
                movie.db.rollback()
        else:
            movie.movie(keyword)
            movie.movie3(keyword)
        le = movie.cursor.execute(movie.select, keyword)
        movie.db.close()
        return render_template('result.html', data=movie.cursor.fetchall(), kwd=keyword, length=le, form=form)
    return render_template('index.html', form=form)

if __name__ == '__main__':
    movies.run()