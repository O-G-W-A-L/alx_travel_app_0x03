# Travel App Backend API

## Technical Overview

### Core Components
- **Models**  
  - `Listing`: Property listings with pricing, location, amenities (PostgreSQL JSON field)
  - `Booking`: Reservation system with date validation constraints  
  - `Review`: Rating system with 1-5 star validation

## Setup
### Project Structure
```
alx_travel_app_0x00/
├── alx_travel_app/
│   ├── settings.py
│   └── ...
├── listings/
│   ├── models.py
│   ├── serializers.py
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed.py
│   └── ...
└── manage.py
```
### setup
```bash
# 1. Initialize database
python manage.py migrate

# 2. Seed test data (creates 10 listings, 20 bookings, 15 reviews)
python manage.py seed --test

# 3. Run development server
python manage.py runserver
```
API Endpoints
Endpoint	Method	Auth Required	Description
/api/listings/	GET	No	Paginated listings (100/page)
/api/listings/{id}/	GET	No	Detailed listing view
/api/bookings/	POST	JWT	Create new booking
Testing
```bash

# Run all tests with coverage
pytest --cov=listings --cov-report=html

# Specific test type
pytest listings/tests/unit/test_models.py -v
```
Production Notes

    Environment Variables required:
    

    DJANGO_SECRET_KEY=your-secret-key
    DATABASE_URL=postgres://user:pass@host:port/db
    REDIS_URL=redis://cache:6379/0
