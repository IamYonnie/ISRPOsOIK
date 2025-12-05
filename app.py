# MIT License

import os
import logging
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from config import config
from models import db
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['development']))
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprint
    from routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize background tasks scheduler
    if config_name != 'testing':
        from background_tasks import start_scheduler
        start_scheduler(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {error}')
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Frontend routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/projects')
    def projects():
        return render_template('projects.html')
    
    @app.route('/project/<int:project_id>')
    def project_detail(project_id):
        return render_template('project.html', project_id=project_id)
    
    logger.info(f'Application created with config: {config_name}')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
