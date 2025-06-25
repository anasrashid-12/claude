# Use official Node.js LTS image
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install dependencies with caching
COPY package.json package-lock.json ./
RUN npm install

# Copy app files
COPY . .

# Build Next.js app
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

# Install only production dependencies
COPY package.json package-lock.json ./
RUN npm install --only=production

# Copy built app from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.js ./next.config.js
COPY --from=builder /app/tsconfig.json ./tsconfig.json

# Expose Next.js port
EXPOSE 3000

# Start Next.js
CMD ["npm", "start"]
