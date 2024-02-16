#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 19:44:30 2024

@author: qinxiangyuan
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
db = SQLAlchemy()
def initialize_database(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:XXXXXX@localhost:5432/finance-calculator-pgdatabase'
    db.init_app(app)
    with app.app_context():
        try:
            result = db.session.execute(text('SELECT version()'))
            print("Database connection successful!")
            print(result.fetchone())
        except Exception as e:
            print(f"Error connecting to the database: {e}")