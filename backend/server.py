import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from app import create_app


app = create_app()
CORS(app, 
     origins=["http://localhost:8080"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

if __name__ == '__main__':
    app.run(debug=True)
