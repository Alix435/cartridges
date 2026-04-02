from flask import Flask, render_template
from  other.config_html import key

app = Flask(__name__)
app.secret_key = key

@app.route('/')
def home_page():
    return render_template('home_page.html')

@app.route('/cartridge')
def cartridge():
    return render_template('cartridge.html')

@app.route('/act')
def act():
    return render_template('act.html')

@app.route("/user")
def new_user():
    return render_template('new_user.html')

if __name__ == "__main__":
    app.run(host= '127.0.0.1', port=5000, debug= True)