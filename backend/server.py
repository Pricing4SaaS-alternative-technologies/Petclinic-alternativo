import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS


# Obtén la ruta absoluta del archivo server.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Sube un nivel para salir de backend/
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Construye la ruta absoluta hacia la carpeta dist del frontend
dist_dir = os.path.join(parent_dir, 'frontend', 'dist')
static_dir = os.path.join(dist_dir, 'static')

app = Flask(__name__,
            static_folder = static_dir,
            template_folder = dist_dir)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/v1.0/mensaje')
def create_task():
    return jsonify('Hola mundo desde Flask')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def dender_vue(path):
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)