from flask import Flask, jsonify
from routes.signup import signup_bp
from routes.login import login_bp
from routes.admin import admin_bp
from routes.home import home_bp
from routes.cabinet import cabinet_bp
from routes.auth import auth_bp
from routes.logout import logout_bp
from database.db import init_db, close_db, get_user_by_id
from database.db_init import create_test_data
from datetime import datetime, date
import os
import atexit
from flask_swagger_ui import get_swaggerui_blueprint
import json
import yaml

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # Change this to a secure key in production

# Swagger UI configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Hospital Management API"
    }
)

app.register_blueprint(swaggerui_blueprint)

# Create static folder if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# Read swagger.yaml and convert it to JSON
with open('swagger.yaml', 'r') as yaml_file:
    swagger_spec = yaml.safe_load(yaml_file)

# Write as swagger.json for the UI to use
with open('static/swagger.json', 'w') as json_file:
    json.dump(swagger_spec, json_file)

# Add custom filters
@app.template_filter('datetime')
def format_datetime(value):
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None
    if isinstance(value, datetime):
        return value.date()
    return value

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(login_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cabinet_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(logout_bp)

# Initialize database with test data on startup
def initialize_database():
    with app.app_context():
        if os.path.exists('instance/hospital.db'):
            print("Removing existing database...")
            os.remove('instance/hospital.db')
        
        print("Initializing fresh database...")
        init_db()
        
        print("Creating test data...")
        create_test_data()
        
        # Verify database structure
        from database.db import verify_db_structure
        print("Verifying database structure...")
        verify_db_structure()

# Clean up database on shutdown
def cleanup_database():
    if os.path.exists('instance/hospital.db'):
        os.remove('instance/hospital.db')

# Register startup and shutdown handlers
initialize_database()
atexit.register(cleanup_database)

# Register database close function
app.teardown_appcontext(close_db)

@app.context_processor
def utility_processor():
    return dict(get_user_by_id=get_user_by_id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
