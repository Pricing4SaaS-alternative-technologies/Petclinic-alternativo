from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # 1) Leemos el SQL original
    raw_sql = open('data.sql', encoding='utf-8').read()

    # 2) Eliminamos líneas de comentario que empiecen por --
    lines = [
        line for line in raw_sql.splitlines()
        if not line.strip().startswith('--')
    ]
    cleaned_sql = '\n'.join(lines)

    # 3) Añadimos desactivación de claves foráneas al inicio y reactivación al final
    cleaned_sql = (
        "SET FOREIGN_KEY_CHECKS=0;\n" +
        cleaned_sql +
        "\nSET FOREIGN_KEY_CHECKS=1;"
    )

    # 4) Ejecutamos cada sentencia separada por ';'
    for i, stmt in enumerate(cleaned_sql.split(';')):
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            db.session.execute(text(stmt))
        except Exception as e:
            print(f"\n Error en la sentencia #{i + 1}:\n{stmt}\n→ {e}\n")

    # 5) Confirmamos la transacción
    try:
        db.session.commit()
        print("\n Datos cargados correctamente.")
    except Exception as e:
        print(f"\n Error al hacer commit:\n→ {e}")
        db.session.rollback()
