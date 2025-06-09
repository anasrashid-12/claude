#!/bin/bash

# Install dependencies
npm install

# Create .env.local from template if it doesn't exist
if [ ! -f .env.local ]; then
  cp .env.local.template .env.local
  echo "Created .env.local from template"
fi

# Create necessary directories
mkdir -p components
mkdir -p hooks
mkdir -p app/login

echo "Frontend setup completed successfully!" 