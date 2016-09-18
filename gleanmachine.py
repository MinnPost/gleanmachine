from flask import Flask, render_template
from newspaper import Article
import json

app = Flask(__name__)

#for development purposes
urls = ['http://www.twincities.com/2016/09/18/chris-coleman-mn-governor/',
        'http://www.startribune.com/minnesota-poll-clinton-keeps-lead-but-trump-gains/393840031/',
        'http://www.mprnews.org/story/2016/09/18/st-cloud-mall-stabbings',
        'http://www.startribune.com/st-cloud-mall-closed-until-monday-is-crime-scene-after-stabbings/393872071/']

#load news source dict from json so it's easy(er) to update
fp = open('./news_sources.json','r')
publications = json.load(fp)
fp.close()

def parse_article(url):
    article = Article(url)

    publication = "PUBLICATION"
    for pub in publications:
        if pub in url:
            publication = publications[pub]

    article.download()
    article.parse()

    title = article.title

    extracted_authors = article.authors
    authors_singular = False
    if len(extracted_authors) == 2:
        authors = " and ".join(extracted_authors)
    if len(extracted_authors) > 2:
        authors = ", ".join(extracted_authors[i] for i in range(len(extracted_authors)-1))
        authors += " and " + extracted_authors[-1]
    else:
        authors = extracted_authors[0]
        authors_singular = True

    article_fulltext = article.text
    article_paragraphs = article_fulltext.split("\n\n")
    if len(article_paragraphs) > 4:
        summary = " … ".join(article_paragraphs[0:4])
    else:
        summary = article_fulltext.replace("\n\n"," … ")

    return {
                "url": url,
                "publication": publication,
                "title": title,
                "authors": authors,
                "authors_singular": authors_singular,
                "summary": summary
            }

@app.route('/build')
def build_glean():

    #todo -- grab the URLs from redis
    url_list = urls

    gleanings = []

    for url in url_list:
        gleanings.append(parse_article(url))

    #todo: clear redis cache of urls

    return render_template('glean.html', gleanings=gleanings)

@app.route('/add-url')
def add_url():
    #todo: store the urls in redis
    pass

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
