import psycopg
import os

"""
Simple DB helper functions.
DO NOT execute database queries at import time.
"""

def get_conn():
    db_url = os.getenv("DATABASE_URL", "dbname=gradcafe")
    return psycopg.connect(db_url)
