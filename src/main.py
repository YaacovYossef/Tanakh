from flask import Flask, render_template, request, jsonify
import sqlite3
from routes.tanakh import tanakh_bp

app = Flask(__name__, static_folder='static', template_folder='static')
app.register_blueprint(tanakh_bp, url_prefix='/api/tanakh')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
