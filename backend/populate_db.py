from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # 1) Leemos todo el SQL
    raw_sql = open('data.sql', encoding='utf-8').read()

    # 2) Eliminamos líneas de comentario que empiecen por --
    lines = [
        line for line in raw_sql.splitlines()
        if not line.strip().startswith('--')
    ]
    cleaned_sql = '\n'.join(lines)

    # 3) Partimos en cada ';' y ejecutamos una a una
    for stmt in cleaned_sql.split(';'):
        stmt = stmt.strip()
        if not stmt:
            continue
        # text() sólo admite una sentencia a la vez
        db.session.execute(text(stmt))

    # 4) Confirmamos
    db.session.commit()
    print("Datos cargados correctamente.")
