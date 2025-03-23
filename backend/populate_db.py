from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    
    db.create_all()

    # Leer y ejecutar las sentencias SQL desde data.sql
    with open('data.sql', 'r', encoding='utf-8') as f:
        sql_commands = f.read()
        with db.engine.begin() as connection:
            connection.execute(text(sql_commands))
