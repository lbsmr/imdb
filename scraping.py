import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

request = requests.get('https://www.imdb.com/chart/top/?ref_=nv_mv_250')
soup = bs(request.content,features="lxml")

titles = []
links = []
years = []
ratings = []

table = soup.find(class_ = 'chart full-width')
table_rows = table.find_all('tr')

for index,row in enumerate(table_rows):
    if index == 0:
        continue
    title = row.find(class_ = 'titleColumn').find('a').get_text()
    link = row.find(class_ = 'titleColumn').find('a', href = True)['href']
    year = row.find(class_ = 'titleColumn').find('span').get_text().replace('(','').replace(')','')
    rating = row.find(class_ = 'imdbRating').find('strong').get_text()
    titles.append(title)
    links.append(link)
    years.append(year)
    ratings.append(rating)
    print(index)

zippedList = list(zip(titles,years,ratings))
df = pd.DataFrame(zippedList, columns = ['title','year','rating'])

directors = []
lengths = []
genres = []
crews = []
votes = []

for index,link in enumerate(links):
    request = requests.get('https://www.imdb.com' + link)
    soup = bs(request.content,features="lxml")
    director = soup.find(class_ = 'ipc-metadata-list-item__list-content-item').get_text()
    length = soup.find_all(class_ = 'ipc-inline-list__item')[5].get_text()
    genre_tags = soup.find_all(class_ = 'sc-16ede01-3 bYNgQ ipc-chip ipc-chip--on-baseAlt')
    crew = soup.find(class_ = 'ipc-sub-grid ipc-sub-grid--page-span-2 ipc-sub-grid--wraps-at-above-l ipc-sub-grid--4-unit-at-s ipc-shoveler__grid')
    total_votes = soup.find(class_ = 'sc-7ab21ed2-3 dPVcnq').get_text()
    genre_list = []
    full_cast = []
    for g in genre_tags:
        genre = g.find(class_ = 'ipc-chip__text').get_text()
        genre_list.append(genre)
    for c in crew:
        n = c.find(class_ = 'sc-36c36dd0-1 QSQgP')
        full_cast.append(n.get_text())
    directors.append(director)
    lengths.append(length)
    genres.append(', '.join(genre_list))
    crews.append(', '.join(full_cast))
    votes.append(total_votes)
    print(index)

df['director'] = directors
df['length'] = lengths
df['genres'] = genres
df['crew'] = crews
df['votes'] = votes

df.to_csv('./top_250.csv')