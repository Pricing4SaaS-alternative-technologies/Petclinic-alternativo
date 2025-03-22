import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from app import create_app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
