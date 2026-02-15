"""Create the applicants table for local use and CI."""

import os

import psycopg

from src.load_data import create_table


def main():
    database_url = os.getenv("DATABASE_URL", "dbname=gradcafe")
    conn = psycopg.connect(database_url)
    try:
        create_table(conn)
    finally:
        conn.close()


if __name__ == "__main__":  # pragma: no cover
    main()
