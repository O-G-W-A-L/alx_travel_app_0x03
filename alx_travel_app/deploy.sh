#!/bin/bash

# === CONFIGURE ===
APP_NAME="listings"
PROJECT_NAME="alx_travel_app"

echo "🚀 Starting Django + Celery + RabbitMQ deployment to Heroku..."

# === CHECK REQUIREMENTS ===
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not installed. Install it from https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# === STEP 1: Install required Python packages ===
echo "📦 Installing required Python packages..."
pip install gunicorn psycopg2-binary dj-database-url python-decouple whitenoise celery cloudamqp drf-yasg django-cors-headers

# === STEP 2: Create Procfile if not exists ===
if [ ! -f "Procfile" ]; then
cat <<EOF > Procfile
web: gunicorn ${PROJECT_NAME}.wsgi
worker: celery -A ${PROJECT_NAME} worker --loglevel=info
EOF
echo "✅ Created Procfile"
fi

# === STEP 3: Create runtime.txt for Python version ===
if [ ! -f "runtime.txt" ]; then
PYTHON_VERSION=$(python3 -c 'import platform; print(platform.python_version())' | cut -d. -f1-2)
echo "python-${PYTHON_VERSION}" > runtime.txt
echo "✅ Created runtime.txt (Python ${PYTHON_VERSION})"
fi

# === STEP 4: Collect static files ===
echo "🗂️ Collecting static files..."
python manage.py collectstatic --noinput

# === STEP 5: Create Heroku app ===
echo "🌐 Creating Heroku app: ${APP_NAME}"
heroku create ${APP_NAME}

# === STEP 6: Add CloudAMQP (RabbitMQ) ===
echo "🐇 Adding free CloudAMQP (RabbitMQ)..."
heroku addons:create cloudamqp:lemur --app ${APP_NAME}

# === STEP 7: Add free Postgres DB ===
echo "🗄️ Adding free Postgres DB..."
heroku addons:create heroku-postgresql:hobby-dev --app ${APP_NAME}

# === STEP 8: Push code to Heroku ===
echo "⬆️ Pushing code to Heroku..."
git add .
git commit -m "Deploy Django + Celery + RabbitMQ to Heroku" || echo "No changes to commit"
git push heroku main

# === STEP 9: Run migrations ===
echo "⚙️ Running Django migrations..."
heroku run python manage.py migrate --app ${APP_NAME}

# === STEP 10: Scale Web + Worker ===
echo "📈 Scaling web and worker dynos..."
heroku ps:scale web=1 worker=1 --app ${APP_NAME}

# === STEP 11: Show CloudAMQP & DB URLs ===
echo "🔗 Fetching config vars..."
heroku config --app ${APP_NAME}

echo "✅ Deployment complete!"
echo "🌐 Visit your app at: https://${APP_NAME}.herokuapp.com"
echo "📜 Swagger docs should be at: https://${APP_NAME}.herokuapp.com/swagger/"
