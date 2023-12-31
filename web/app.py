from flask import Flask, jsonify, request, render_template
import boto3
import json
import wpt_io as wptio
import random

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/map')
def map_page():
    people = wptio.get_people()
    return render_template('map_page.html')
    
@app.route('/api/markers')
def get_markers():
    markers = wptio.get_markers()
    return jsonify(markers)
    
@app.route("/api/get_people")
def get_people():
    people = wptio.get_items()
    return jsonify(people)
    
@app.route('/hiker/<string:person_name>')
def hiker_profile(person_name):
    return render_template('person.html', data=person_name)
    
@app.route('/api/hiker/<string:person_name>')
def get_person_html(person_name):
    person = wptio.scan_items_by_person(person_name)
    articles = wptio.sort_articles(person);
    html_list = []
    lat = 0;
    lng = 0;
    for article in articles:
        
        html_list.append(
            render_template('mapless_cards.html' if len(html_list) > 0 else 'first_card.html', data={
                "date": article['date_formatted'],
                "lat": article['geo']['lat_lng']['lat'],
                "lng": article['geo']['lat_lng']['lng'],
                'person_name': article['gpt']['person'],
                'details': article['gpt']['details'],
                'location': article['gpt']['location'],
                'thumbnail': article['thumbnail']
            })
        )
        if lat == 0:
            lat = article['geo']['lat_lng']['lat']
            lng = article['geo']['lat_lng']['lng']
        
    
    html_list.extend([lat, lng])
    
    return jsonify(html_list);
        
        
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")