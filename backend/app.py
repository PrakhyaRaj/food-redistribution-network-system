from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError

from backend.config import Config 

# Import your global extensions from extensions.py
from backend.extensions import db, migrate, jwt, socketio

from backend.mongodb import init_mongo
from backend.validation import ValidationError, handle_validation_error

def create_app(config_object=None):
    app = Flask(__name__)

    app.config.from_object(Config) 
    print("Using database:", app.config["SQLALCHEMY_DATABASE_URI"])

    # ============================
    # CORS
    # ============================
    CORS(
        app,
        origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8080",
            "http://127.0.0.1:8080"
        ],
        supports_credentials=True,
        allow_headers=["*"],  # Allow all headers
        methods=["*"],  # Allow all methods
        expose_headers=["*"]  # Expose all headers
    )

    # ============================
    # Flask & JWT Config
    # ============================
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'change-this-secret')
    # app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
    # app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
    # app.config['JWT_BLOCKLIST'] = set()  # in-memory token blocklist

    # ============================
    # Initialize Extensions
    # ============================
    db.init_app(app)
    migrate.init_app(app, db, directory="backend/migrations")  # points to backend/migrations
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

    # ============================
    # Socket.IO CORS handling
    # ============================
    @socketio.on('connect')
    def handle_connect():
        print('🔌 Client attempting to connect')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('🔌 Client disconnected')
    
    # ============================
    # Import Socket.IO handlers after socketio is initialized
    # ============================
    from backend import sockets  # Import socket handlers after socketio is initialized

    # init_mongo(app)
    # Temporarily disable MongoDB
    try:
        init_mongo(app)
    except Exception as e:
        print(f"⚠️ MongoDB initialization failed: {e}")
        print("⚠️ Continuing without MongoDB features...")
        app.mongodb = None

    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin:
            response.headers.set('Access-Control-Allow-Origin', origin)
        else:
            response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        response.headers.set('Access-Control-Allow-Headers', '*')
        response.headers.set('Access-Control-Allow-Methods', '*')
        return response

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({"status": "preflight"})
            origin = request.headers.get('Origin')
            if origin:
                response.headers.set('Access-Control-Allow-Origin', origin)
            response.headers.set('Access-Control-Allow-Credentials', 'true')
            response.headers.set('Access-Control-Allow-Headers', '*')
            response.headers.set('Access-Control-Allow-Methods', '*')
            return response
    
    # ============================
    # Blueprints
    # ============================
    with app.app_context():
        from backend.auth import auth_bp
        from backend.routes.food_routes import food_bp
        from backend.routes.feedback_routes import feedback_bp
        from backend.routes.user_routes import user_bp
        from backend.routes.request_routes import request_bp
        from backend.routes.transaction_routes import transaction_bp
        from backend.routes.food_images_routes import food_images_bp
        from backend.routes.analytics_routes import analytics_bp
        from backend.routes.route_routes import route_bp
        from backend.routes.notes_routes import notes_bp
        from backend.routes.mongodb_routes import mongodb_bp
        from backend.routes.admin_routes import admin_bp
        # from backend.routes.logs_routes import logs_bp

        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(food_bp)
        app.register_blueprint(feedback_bp, url_prefix="/feedback")
        app.register_blueprint(user_bp, url_prefix="/profile")
        app.register_blueprint(request_bp)
        app.register_blueprint(transaction_bp)
        app.register_blueprint(food_images_bp)
        app.register_blueprint(analytics_bp)
        app.register_blueprint(route_bp)
        app.register_blueprint(notes_bp)
        app.register_blueprint(mongodb_bp)
        app.register_blueprint(admin_bp)
        # app.register_blueprint(logs_bp)
    from backend.routes.logs_routes import logs_bp
    app.register_blueprint(logs_bp)

    # ============================
    # JWT Token Blocklist
    # ============================
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        blocklist = app.config.get("JWT_BLOCKLIST", set())
        return jti in blocklist

    # ============================
    # Socket.IO Handlers
    # ============================
    from backend import sockets  # @socketio.on handlers

    # ============================
    # ValidationError Handling
    # ============================
    @app.errorhandler(ValidationError)
    def validation_handler(error):
        return handle_validation_error(error)

    # ============================
    # Standard Error Handlers
    # ============================
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": "Bad request - invalid input data"}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"success": False, "error": "Unauthorized - authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"success": False, "error": "Forbidden - insufficient permissions"}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"success": False, "error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        db.session.rollback()
        app.logger.error(f"Database error: {str(error)}")
        return jsonify({"success": False, "error": "Database operation failed"}), 500

    # ============================
    # Debug Routes
    # ============================
    @app.route("/debug/routes")
    def debug_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "path": str(rule)
            })
        return jsonify(routes)

    @app.route('/debug/websocket')
    def debug_websocket():
        return jsonify({
            "websocket_enabled": True,
            "message": "WebSocket server is running",
            "endpoint": "ws://127.0.0.1:5000"
        })

    @app.route('/debug/send-test-notification/<int:user_id>', methods=['POST'])
    def send_test_notification(user_id):
        try:
            from backend.notifications import NotificationService
            test_data = {
                'type': 'test',
                'title': 'Test Notification',
                'message': f'This is a test notification for user {user_id}',
                'timestamp': '2024-01-01T00:00:00'
            }
            socketio.emit('notification', test_data, room=f"user_{user_id}")
            return jsonify({
                "success": True,
                "message": f"Test notification sent to user {user_id}"
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/debug-cors')
    def debug_cors():
        return jsonify({
            "message": "CORS test successful",
            "allowed_origins": ["http://localhost:8080", "http://127.0.0.1:8080"]
        })
    
    @app.route('/debug/postgres-check')
    def debug_postgres_check():
        try:
            from backend.models import User, Role
            from sqlalchemy import text
        
            # Test basic connection
            db_version = db.session.execute(text("SELECT version();")).fetchone()[0]
            current_db = db.session.execute(text("SELECT current_database();")).fetchone()[0]
        
            # Test table access
            user_count = User.query.count()
            role_count = Role.query.count()
        
            return jsonify({
                "success": True,
                "message": "PostgreSQL connection successful!",
                "database": current_db,
                "postgres_version": db_version,
                "users_count": user_count,
                "roles_count": role_count
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"PostgreSQL connection failed: {str(e)}"
            }), 500

    @app.route('/debug/users')
    def debug_users():
        try:
            from backend.models import User
            users = User.query.all()
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.user_id,
                    'email': user.email,
                    'name': user.name,
                    'roles': [r.role_name for r in user.roles]
                })
            return jsonify({
                "success": True,
                "users": user_list,
                "count": len(users)
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return app

# ============================
# Run App
# ============================
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Food Redistribution Network with WebSocket support...")
    print("📡 WebSocket server running on: http://127.0.0.1:5000")
    socketio.run(app, debug=True, port=5000, host='127.0.0.1', allow_unsafe_werkzeug=True)
