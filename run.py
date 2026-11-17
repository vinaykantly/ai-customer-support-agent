import os
from backend.app import create_app

env_name = os.getenv("FLASK_ENV", "development")
app = create_app(env_name)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    
    print("=" * 70)
    print("  AI-POWERED CUSTOMER SUPPORT AGENT - ENTERPRISE EDITION")
    print("=" * 70)
    print(f"  Server running at: http://{host}:{port}")
    print("  Available Demo Credentials (1-Click Login available on login page):")
    print("    - Admin:    admin@company.com        / Admin@123")
    print("    - Agent:    agent.rajesh@company.com / Agent@123")
    print("    - Customer: customer@example.com     / Customer@123")
    print("=" * 70)
    
    app.run(host=host, port=port, debug=True)
