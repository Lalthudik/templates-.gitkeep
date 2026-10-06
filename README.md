# JMJ Enterprise — Public Deployment Package

Python/Flask e-commerce starter prepared for public hosting.

## Local run
1. Create a virtual environment.
2. `pip install -r requirements.txt`
3. Set `SECRET_KEY` and `ADMIN_PASSWORD` environment variables.
4. `python app.py`
5. Open `http://127.0.0.1:5000`

## Render
Use the included `render.yaml`, or configure:
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --workers 2 --timeout 120`
- Health check: `/health`

Required environment variables:
- `SECRET_KEY` — long random secret
- `ADMIN_PASSWORD` — strong admin password
- `COOKIE_SECURE=1` — keep enabled on HTTPS hosting

## Important commercial-launch limitations
- UPI/Card/Net Banking are currently placeholders; no real payment is collected until a gateway is integrated.
- SQLite on a free Render web service is not persistent. Use managed PostgreSQL or paid persistent storage for real orders.
- Product catalogue and stock are currently hard-coded sample data.


STAGING STATUS
- Local SECRET_KEY fallback added so the app can start without manually setting SECRET_KEY for local testing.
- Render can still provide SECRET_KEY through its environment configuration.
- Responsive CSS is included for desktop, tablet and mobile layouts.
- Before production launch, replace SQLite with PostgreSQL and integrate a real payment gateway.
