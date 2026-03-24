#!/bin/bash
# If you cant run this do: chmod +x run.sh

#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Make migrations
echo "Making migrations..."
python manage.py makemigrations

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Run server
echo "Starting Django server..."
python manage.py runserver