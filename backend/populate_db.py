from app import create_app
from app import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with open('data.sql', 'r', encoding='utf-8') as f:
        sql_commands = f.read()
        # Ejecuta las consultas SQL dentro de un contexto de transacción
        with db.engine.begin() as connection:
            connection.execute(text(sql_commands))