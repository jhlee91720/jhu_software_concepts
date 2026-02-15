# Module 4: Pytest and Sphinx

## Setup

```bash
cd module_4
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set DB connection:

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gradcafe
```

Create schema:

```bash
python src/create_table.py
```

Run app:

```bash
flask --app src/flask_app.py run
```

Run tests:

```bash
pytest -m "web or buttons or analysis or db or integration"
```
