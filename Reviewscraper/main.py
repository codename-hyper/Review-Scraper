from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as bs
import pymongo

ws = Flask('__name__')


@ws.route('/', methods=['GET'])
@cross_origin()
def homepage():
    return render_template('homepage.html')


@ws.route('/scrap', methods=['GET', 'POST'])
@cross_origin()
def scrap():
    if request.method == 'POST':
        global reviews
        try:
            searchstring = request.form['wst'].replace("", " ")
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            database = client['WebScraper']
            ratings = database[searchstring].find({})
            if ratings.count() > 0:
                return render_template('results.html', rev=ratings)
            else:
                searchstring = request.form['wst'].replace(" ", "")
                uclient = uReq('https://www.flipkart.com/search?q=' + searchstring)
                webpage = uclient.read()
                uclient.close()
                soup = bs(webpage, 'html.parser')
                phones = soup.find_all('div', {'class': 'bhgxx2 col-12-12'})
                del phones[0:3]
                for phone in phones[0:1]:
                    phone_url = 'https://www.flipkart.com' + phone.div.div.div.a['href']
                    phone_url_req = requests.get(phone_url)
                    soup_phone = bs(phone_url_req.text, 'html.parser')
                    comment_boxes = soup_phone.find_all('div', {'class': '_3nrCtb'})
                    table = database[searchstring]
                    reviews = []
                    for comments in comment_boxes:
                        try:
                            rating = comments.find('div', {'class': 'hGSR34 E_uFuv'}).text
                        except:
                            rating = 'no rating'

                        try:
                            rating_text = comments.find('p', {'class': '_2xg6Ul'}).text
                        except:
                            rating_text = 'no rating header'

                        try:
                            comment = comments.find('div', {'class': 'qwjRop'}).text
                        except:
                            comment = 'no comment'
                        try:
                            customer = comments.find('p', {'class': '_3LYOAd _3sxSiS'}).text
                        except:
                            customer = 'no name'
                        my_dict = {'product': searchstring, 'rating': rating, 'rating_text': rating_text,
                                   'comment': comment,
                                   'customer': customer}
                        table.insert_one(my_dict)
                        reviews.append(my_dict)
                return render_template('results.html', rev=reviews)
        except:
            return 'somthing is wrong'
    else:
        return render_template('homepage.html')


if __name__ == '__main__':
    ws.run(port=8000, debug=True)
else:
    print('ERROR')
