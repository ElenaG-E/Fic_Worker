import httpx
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import logging

# Configurar un registro básico para ver la actividad y los errores
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Crear un cliente HTTPX persistente para reutilizar conexiones
client = httpx.Client()

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_root():
    """
    Esta función maneja solicitudes a la raíz '/' devolviendo un mensaje de estado.
    """
    return jsonify({"message": "Proxy server running", "usage": "Use /v1beta/... paths for API calls"})

@app.route('/<path:path>', methods=['POST', 'GET'])
def proxy(path):
    if not path.startswith('v1beta/'):
        logging.warning(f"Ignoring request for invalid path: {path}")
        return jsonify({"error": "Not a valid API path"}), 404

    logging.info(f"Proxying request for path: {path}")
    
    api_key = request.headers.get('x-goog-api-key')
    if not api_key:
        return jsonify({"error": "API key required"}), 400

    try:
        # Definir la URL de la API de Google y los headers
        google_api_url = f'https://generativelanguage.googleapis.com/{path}'
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': api_key
        }

        # Realizar la solicitud a la API de Google de forma directa (sin streaming)
        response = client.request(
            method=request.method,
            url=google_api_url,
            params=request.args.to_dict(),
            headers=headers,
            content=request.get_data(),
            timeout=300.0
        )

        logging.info(f"Respuesta de la API de Google: {response.status_code}")

        # Devolver la respuesta completa (contenido, estado, encabezados) al cliente original.
        # Esto es más robusto y evita errores de streaming con respuestas de error.
        return Response(response.content, status=response.status_code, headers=dict(response.headers))

    except httpx.RequestError as e:
        logging.error(f"Error de conexión al intentar contactar con la API de Google: {e}")
        return jsonify({"error": "Error de conexión con el servidor proxy", "details": str(e)}), 502 # 502 Bad Gateway
    except Exception as e:
        logging.error(f"Ha ocurrido un error inesperado en el proxy: {e}")
        return jsonify({"error": "Error interno del servidor proxy", "details": str(e)}), 500

if __name__ == '__main__':
    # Ejecutar la aplicación en el puerto 8080, accesible desde cualquier IP
    app.run(host='0.0.0.0', port=8080)
