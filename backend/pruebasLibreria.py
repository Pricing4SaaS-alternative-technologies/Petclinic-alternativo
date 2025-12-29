import uuid
import tempfile
import os

from app import create_app


def main():
    app = create_app()

    # Entramos en el contexto de la app (para current_app, etc.)
    with app.app_context():
        space_client = app.space_client

        # --- 1) Función async para probar add_service + get_service ---
        async def _test_add_service():
            unique_id = uuid.uuid4().hex[:8]
            service_name = f"Test_{unique_id}"

            yaml = f"""saasName: {service_name}
syntaxVersion: "3.0"
version: "1.0.0"
createdAt: "2025-01-01"
currency: USD
features:
  basic:
    description: Test
    valueType: BOOLEAN
    defaultValue: true
    type: DOMAIN
"""

            temp_path = None
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
                f.write(yaml)
                temp_path = f.name

            try:
                await space_client.service_context.add_service(temp_path)
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
            print(f"Servicio añadido: {service_name}")


        async def _test_get_service():
            service = await space_client.service_context.get_service("Test_02b2ae07")
            print(f"Servicio obtenido: {service}")
            
            
        # --- 2) Usar el cliente a través de app.run_async (como en Flask) ---
        connected = app.run_async(space_client.is_connected_to_space())
        print("Conectado a Space:", connected)

        app.run_async(_test_add_service())
        app.run_async(_test_get_service())
        
        # Después del apagado, la sesión debería estar cerrada
        if hasattr(space_client, "_session") and space_client._session is not None:
            print("Sesión cerrada?:", space_client._session.closed)


if __name__ == "__main__":
    main()