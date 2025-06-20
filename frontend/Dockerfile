# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy only package files first to leverage caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Then copy source files
COPY . .

# Build the app
RUN npm run build

# Start the app
EXPOSE 3000
CMD ["npm", "start"]
