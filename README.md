# Código Fuente

Repositorio de código donde se almacenará el trabajo realizado en frontend a lo largo de los sprints para el correcto desarrollo del proyecto.


## 1. Configurar SPACE

1. Desde tu IDE (Visual Studio Code, por ejemplo), clona el repositorio:
   ```bash
   git clone https://github.com/Alex-GF/space.git
   ```

2. Accede al directorio del proyecto:
   ```bash
   cd space
   ```

3. Levanta la aplicación con Docker:
   ```bash
   docker-compose up -d
   ```

Este comando levantará automáticamente:
- MongoDB
- Redis
- API del backend
- Cliente frontend
- Nginx (proxy inverso)

4. Abre tu navegador en [http://localhost:5403](http://localhost:5403) e inicia sesión con:

   - **Usuario:** `admin`
   - **Contraseña:** `space4all`

> Una vez dentro, podrás gestionar los planes de precios y encontrar tu **API_KEY** en la sección `Access Control`.

---

## 2. Ejecutar el backend

Con SPACE ya funcionando:

1. Clona el repositorio del proyecto:
   ```bash
   git clone https://github.com/Pricing4SaaS-alternative-technologies/Petclinic-alternativo.git
   ```

2. Copia el archivo de configuración de ejemplo:
   ```bash
   cp config.py.example config.py
   ```

3. Edita `config.py` y completa los valores de:
   - `SQLALCHEMY_DATABASE_URI`
   - `SECRET_KEY`
   - `SPACE_API_KEY`

4. Accede al directorio del backend:
   ```bash
   cd backend
   ```

5. Crea y activa un entorno virtual:
   ```bash
   # Crear entorno
   python -m venv venv

    # Activar entorno
   .\venv\Scripts\activate

   ```

6. Instala las dependencias:
   ```bash
   pip install -r requirements.txt --upgrade
   pip install app-SpacePyCl
   ```

7. Rellena la base de datos con datos de ejemplo:
   ```bash
   python populate_db.py
   ```

8. Lanza el servidor:
   ```bash
   python server.py
   ```

   El backend estará disponible en el puerto **5000**

---

## 3. Ejecutar el frontend

Con SPACE funcionando:

1. Abre el archivo `main.js` y asigna tu `apiKey` (obtenida desde el panel de SPACE).

2. Ve al directorio del frontend:
   ```bash
   cd frontend
   ```

3. Instala las dependencias necesarias:
   ```bash
   npm install
   npm i @npm_team/space-vue-client
   ```

4. Arranca el entorno de desarrollo:
   ```bash
   npm run dev
   ```

   El frontend estará corriendo en [http://localhost:8080](http://localhost:8080)

---