from flask import Flask, jsonify, request, render_template
import boto3
import wptio

app = Flask(__name__)

@app.route('/')
def home():
    """
    A homepage route to check if our Flask app is running.
    """
    return render_template('index.html')
    
@app.route('/hiker/<string:hiker_key>')
def hiker_profile(hiker_key):
    hiker = wptio.get_person(hiker_key)
    return render_template('hiker.html', hiker=hiker)
        
    
@app.route('/get_hikers/<int:amount>')
def get_hikers(amount):
    _html = []
    hikers = wptio._get_hikers(amount)
    for hiker in hikers:
        _html.append(render_template('titlecard.html', hiker=hiker))
    return jsonify(_html)
        
        
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")