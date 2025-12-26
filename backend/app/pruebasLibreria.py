from app_SpacePyCl.routes.config import SpaceClient
import asyncio
import tempfile
import uuid
import os


TEST_SPACE_URL = "http://localhost:5403"
API_KEY = "57ab59b541bafc971b7588a192661ed01e3e354a9f1464f868e28a4b66931b01"

client = SpaceClient(TEST_SPACE_URL, API_KEY)

async def test_get_service(space_client):
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
    type: DOMAIN"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml)
            temp_path = f.name
        try:
            await space_client.service_context.add_service(temp_path)
            service = await space_client.service_context.get_service(service_name)
            
        finally:
            None
        #await space_client.close()
        print(f"Servicio obtenido: {service}")


async def prueba(client):
    connected = await client.is_connected_to_space()

    print("Conectado a Space:", connected)
    await test_get_service(client)
    
    # await client.close()

asyncio.new_event_loop().run_until_complete(prueba(client))
# print("Conectado a Space:", asyncio.new_event_loop().run_until_complete(client.is_connected_to_space()))
print("se ha ejectuado:", asyncio.new_event_loop().run_until_complete(prueba(client)))