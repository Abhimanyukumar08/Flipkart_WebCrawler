from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)



app = Flask(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['GET','POST'])
def index():
    if request.method=='POST':
        try:
            word = request.form['content']
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br'
            }

            req = requests.get(flipkart_url, headers=headers)
            flipkart_html = bs(req.content, 'html.parser')
            bigbox  = flipkart_html.find_all("div", {"class":"cPHDOP col-12-12"})
            del bigbox[0:2]
            # box = bigbox[1]
            reviews = []
            for i in range(1,5):
                
                product_link = "https://www.flipkart.com" + bigbox[i].div.div.div.a['href']
                product_req = requests.get(product_link, headers=headers)
                product_req.encoding='utf-8'
                prod_con = bs(product_req.content, 'html.parser')
                comment_box = prod_con.find_all('div',{"class":"RcXBOT"})
                
                
                for comment in comment_box:
                    try:
                        p_name = comment.div.div.find_all('p',{"class":"_2NsDsF AwS1CA"})[0].text
                    except:
                        p_name = "Unknown"
                        logging.info("name")
                    
                    try:
                        rating = comment.div.div.find_all('div',{"class":"XQDdHH Ga3i8K"})[0].text
                    except:
                        rating = "No rating"
                        logging.info("rating")
                        
                    try:
                        comm_title = comment.div.div.find_all('p',{"class":"z9E0IG"})[0].text
                    except:
                        comm_title = "No comment heading"
                        logging.info("comment header")
                    
                    try:
                        comment_data = comment.div.div.find_all('div',{"class":""})[0].text
                        tag = comment_data.split("READ MORE")[0]
                    except:
                        tag = "No comments"
                        logging.info("Comment tag")
                        
                    comm_dict = {
                        "Product":word.upper(),
                        "Person Name": p_name,
                        "Rating" : rating,
                        "Title": comm_title,
                        "Description" : tag
                    }
                    reviews.append(comm_dict)
            logging.info("log my final result {}".format(reviews))
            
            client = pymongo.MongoClient("mongodb+srv://klabhi048:user1234@cluster0.ou961.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            db =client['scrapper_eng_file']
            coll_pw_eng = db['Reviews']
            coll_pw_eng.insert_many(reviews)
            
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
            
        except Exception as e:
            logging.info(e)
    else:
        return render_template("index.html")





if __name__=="__main__":
    app.run(debug=True)