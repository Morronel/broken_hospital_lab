from flask import Flask
import os
import json

def create_app():
    app = Flask(__name__)
    # ... other configurations ...

    from routes.home import home_bp
    from routes.auth import auth_bp
    from routes.login import login_bp
    from routes.signup import signup_bp
    from routes.admin import admin_bp
    from routes.cabinet import cabinet_bp
    from routes.swagger import swaggerui_blueprint

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cabinet_bp)
    app.register_blueprint(swaggerui_blueprint)

    # Create static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')

    # Write swagger.json
    with open('static/swagger.json', 'w') as f:
        json.dump(swagger_spec, f)

    return app

# Your Swagger specification
swagger_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "Hospital Management API",
        "description": "API documentation for Hospital Management System",
        "version": "1.0.0"
    },
    "servers": [
        {
            "url": "http://127.0.0.1:5000",
            "description": "Local development server"
        }
    ],
    # ... rest of your Swagger specification ...
} 