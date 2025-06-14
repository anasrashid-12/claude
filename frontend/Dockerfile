# Step 1: Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy dependencies and install
COPY package.json package-lock.json ./
RUN npm install

# Copy entire project
COPY . .

# Build the Next.js app
RUN npm run build

# Step 2: Production stage
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install production dependencies only
COPY package.json package-lock.json ./
RUN npm install --omit=dev

# Copy the build from builder
COPY --from=builder /app/.next .next
COPY --from=builder /app/public public
COPY --from=builder /app/next.config.js .
COPY --from=builder /app/styles styles
COPY --from=builder /app/app app
COPY --from=builder /app/components components

# Expose port
EXPOSE 3000

# Start the Next.js app
CMD ["npm", "run", "start"]
