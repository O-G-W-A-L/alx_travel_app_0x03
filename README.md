# alx_travel_app

A Django‑based travel listings API with MySQL, Swagger docs, CORS support, and Celery integration.

## Features
- REST API using Django REST Framework  
- MySQL backend (configured via environment variables)  
- Interactive API docs at `/swagger/` (drf‑yasg)  
- Cross‑origin support with django‑cors‑headers  
- Async task queue with Celery & RabbitMQ  

## Quick Start

1. **Clone & enter repo**  
   ```bash
   https://github.com/O-G-W-A-L/alx_travel_app_0x00.git
   cd alx_travel_app
   ```
    Install dependencies
 ```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
 ```
Migrate & run
```bash
    python manage.py migrate
    python manage.py runserver

    Explore API docs
    Open your browser at http://localhost:8000/swagger/
```
Running Celery
```bash
Start a Celery worker for background tasks:

celery -A alx_travel_app worker --loglevel=info
```