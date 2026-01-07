#!/bin/bash

echo "==================================="
echo "Attendify Setup Script"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your database credentials"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p data/student_faces
mkdir -p data/temp
mkdir -p models

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your PostgreSQL credentials"
echo "2. Create PostgreSQL database: createdb attendify_db"
echo "3. Initialize database: python -c 'from database import init_db; init_db()'"
echo "4. Run the application: python app.py"
echo ""
