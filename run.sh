#!/bin/bash

# Start the Flask backend
echo "Starting Flask backend..."
cd web_app/backend
python app.py &
BACKEND_PID=$!

# Start the React frontend
echo "Starting React frontend..."
cd ../frontend
npm install
npm start &
FRONTEND_PID=$!

# Function to handle script termination
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

# Keep the script running
wait 