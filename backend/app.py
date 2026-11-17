import os
from pathlib import Path
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS

from backend.config import config_by_name, Config
from backend.database.db_manager import DatabaseManager
from backend.services.embedding_service import EmbeddingService
from backend.services.gemini_service import GeminiService
from backend.services.rag_service import RAGService
from backend.services.notification_service import NotificationService

from backend.routes.auth_routes import auth_bp
from backend.routes.chat_routes import chat_bp
from backend.routes.ticket_routes import ticket_bp
from backend.routes.agent_routes import agent_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.knowledge_routes import knowledge_bp
from backend.routes.faq_routes import faq_bp
from backend.routes.notification_routes import notification_bp

def create_app(config_name="development"):
    project_root = Path(__file__).resolve().parent.parent
    templates_dir = project_root / "frontend" / "templates"
    static_dir = project_root / "frontend" / "static"

    app = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir),
        static_url_path="/static"
    )

    # Load configuration
    cfg = config_by_name.get(config_name, Config)
    app.config.from_object(cfg)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload directory exists
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    # Initialize Services
    db_manager = DatabaseManager(app.config)
    embedding_service = EmbeddingService(
        api_key=app.config.get("GEMINI_API_KEY", ""),
        model_name=app.config.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    )
    gemini_service = GeminiService(
        api_key=app.config.get("GEMINI_API_KEY", ""),
        model=app.config.get("GEMINI_MODEL", "gemini-1.5-flash")
    )
    rag_service = RAGService(
        db_manager=db_manager,
        embedding_service=embedding_service,
        gemini_service=gemini_service
    )
    notification_service = NotificationService(db_manager=db_manager)

    # Store in app context
    app.config["DB_MANAGER"] = db_manager
    app.config["EMBEDDING_SERVICE"] = embedding_service
    app.config["GEMINI_SERVICE"] = gemini_service
    app.config["RAG_SERVICE"] = rag_service
    app.config["NOTIFICATION_SERVICE"] = notification_service

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(ticket_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(faq_bp)
    app.register_blueprint(notification_bp)

    # Frontend Page Routes (All 12 pages)
    @app.route("/")
    @app.route("/index.html")
    def page_index():
        return render_template("index.html")

    @app.route("/register.html")
    def page_register():
        return render_template("register.html")

    @app.route("/login.html")
    def page_login():
        return render_template("login.html")

    @app.route("/customer_dashboard.html")
    def page_customer_dashboard():
        return render_template("customer_dashboard.html")

    @app.route("/chat.html")
    def page_chat():
        return render_template("chat.html")

    @app.route("/customer_tickets.html")
    def page_customer_tickets():
        return render_template("customer_tickets.html")

    @app.route("/agent_dashboard.html")
    def page_agent_dashboard():
        return render_template("agent_dashboard.html")

    @app.route("/agent_ticket_details.html")
    def page_agent_ticket_details():
        return render_template("agent_ticket_details.html")

    @app.route("/admin_dashboard.html")
    def page_admin_dashboard():
        return render_template("admin_dashboard.html")

    @app.route("/knowledge_base.html")
    def page_knowledge_base():
        return render_template("knowledge_base.html")

    @app.route("/faq_management.html")
    def page_faq_management():
        return render_template("faq_management.html")

    @app.route("/profile.html")
    def page_profile():
        return render_template("profile.html")

    # API Health & Status Endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "AI-Powered Customer Support Agent",
            "database_mode": "supabase" if app.config["DB_MANAGER"].is_supabase else "local_sqlite",
            "gemini_active": bool(app.config.get("GEMINI_API_KEY"))
        }), 200

    # Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found", "message": "The requested resource could not be found."}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500

    return app
