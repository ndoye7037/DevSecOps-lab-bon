from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

#  VULNÉRABILITÉ 1 : Clé secrète codée en dur ⚠️
SECRET_KEY = 'super_secret_123'

@app.route('/')
def index():
    return '<h1>Bienvenue sur le lab DevSecOps !</h1>'

@app.route('/search')
def search():
    #  VULNÉRABILITÉ 2 : Injection SQL ⚠️
    query = request.args.get('q', '')
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    # NE JAMAIS FAIRE ÇA en vrai !
    cursor.execute(f"SELECT * FROM users WHERE name = '{query}'")
    return str(cursor.fetchall())

@app.route('/greet')
def greet():
    #  VULNÉRABILITÉ 3 : XSS (Cross-Site Scripting) ⚠️
    name = request.args.get('name', 'World')
    return render_template_string(f'<h1>Hello {name}!</h1>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)