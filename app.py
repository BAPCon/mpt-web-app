from flask import Flask, jsonify, request, render_template
import boto3
import json
import wptio
import random

app = Flask(__name__)

@app.route('/')
def home():
    """
    A homepage route to check if our Flask app is running.
    """
    hiker = {
        "person_name": "Benjamin Perkins",
        "date": "12/01/2023",
        "location": "Stuart, Florida",
        "details": "Lorem ipsum bullshit yada yada...",
        "google_maps_coords": "20.00, 20.00"
    }
    return render_template('index.html', data=hiker)
    
@app.route('/hiker/<string:person_name>')
def hiker_profile(person_name):
    return render_template('person.html', data=person_name)
    
@app.route('/api/hiker/<string:person_name>')
def get_person_html(person_name):
    person = wptio.scan_items_by_person(person_name)
    '''return render_template('index.html', data = {
        'html': open('templates/mapless_cards.html','r').read()
    })'''
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
                'location': article['gpt']['location']
            })
        )
        if lat == 0:
            lat = article['geo']['lat_lng']['lat']
            lng = article['geo']['lat_lng']['lng']
        
    
    html_list.extend([lat, lng])
    
    return jsonify(html_list);
        
        
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")