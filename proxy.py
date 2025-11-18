import httpx
from flask import Flask, request, Response, jsonify, render_template_string, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import logging
from models import db, User, Story

# Configurar un registro básico para ver la actividad y los errores
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Configuración de Flask-Login
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fic_worker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Crear un cliente HTTPX persistente para reutilizar conexiones
client = httpx.Client()

@app.route('/', methods=['GET', 'POST'])
def proxy_root():
    """
    Esta función maneja solicitudes a la raíz '/' devolviendo un mensaje de estado.
    """
    if current_user.is_authenticated:
        return jsonify({
            "message": "Proxy server running",
            "user": current_user.username,
            "usage": "Use /v1beta/... paths for API calls"
        })
    return jsonify({"message": "Proxy server running", "usage": "Use /v1beta/... paths for API calls"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({"success": True, "message": "Logged in successfully"})
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head><title>Login - Fic Worker</title></head>
    <body>
        <h1>Login</h1>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        <p><a href="/signup">Don't have an account? Sign up</a></p>
    </body>
    </html>
    ''')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({"success": False, "message": "Username already exists"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "Email already exists"}), 400

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return jsonify({"success": True, "message": "Account created successfully"})

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head><title>Sign Up - Fic Worker</title></head>
    <body>
        <h1>Sign Up</h1>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="email" name="email" placeholder="Email" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Sign Up</button>
        </form>
        <p><a href="/login">Already have an account? Login</a></p>
    </body>
    </html>
    ''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('proxy_root'))

@app.route('/api/user/keys', methods=['GET', 'POST'])
@login_required
def manage_api_keys():
    if request.method == 'POST':
        keys = request.json.get('keys', [])
        current_user.set_api_keys(keys)
        db.session.commit()
        return jsonify({"success": True, "message": "API keys updated"})
    return jsonify({"keys": current_user.get_api_keys()})

@app.route('/api/stories', methods=['GET', 'POST'])
@login_required
def manage_stories():
    if request.method == 'POST':
        data = request.json
        story = Story(
            title=data.get('title'),
            content=data.get('content'),
            user_id=current_user.id
        )
        db.session.add(story)
        db.session.commit()
        return jsonify({"success": True, "story_id": story.id})

    stories = Story.query.filter_by(user_id=current_user.id).order_by(Story.updated_at.desc()).all()
    return jsonify([{
        "id": s.id,
        "title": s.title,
        "content": s.content[:200] + "..." if len(s.content) > 200 else s.content,
        "created_at": s.created_at.isoformat(),
        "updated_at": s.updated_at.isoformat()
    } for s in stories])

@app.route('/api/stories/<int:story_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_story(story_id):
    story = Story.query.filter_by(id=story_id, user_id=current_user.id).first_or_404()

    if request.method == 'DELETE':
        db.session.delete(story)
        db.session.commit()
        return jsonify({"success": True})

    if request.method == 'PUT':
        data = request.json
        story.title = data.get('title', story.title)
        story.content = data.get('content', story.content)
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({
        "id": story.id,
        "title": story.title,
        "content": story.content,
        "created_at": story.created_at.isoformat(),
        "updated_at": story.updated_at.isoformat()
    })

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
    with app.app_context():
        db.create_all()
    # Ejecutar la aplicación en el puerto 8080, accesible desde cualquier IP
    app.run(host='0.0.0.0', port=8080)
