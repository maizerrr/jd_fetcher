from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import logging
import os

from extensions import db

def create_app():
    # Configure logging
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create and configure the app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-flash-messages')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    

    # Register routes
    with app.app_context():
        # Import models first to avoid circular dependencies
        from models import Job
        
        # Register routes after models
        from routes import register_routes
        register_routes(app)
        
        # Create database tables
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)