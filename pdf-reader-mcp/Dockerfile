# Stage 1: Build the application
FROM node:lts-alpine AS builder
WORKDIR /app

# Copy package files
# Using package-lock.json ensures reproducible installs
COPY package.json pnpm-lock.yaml ./

# Install ALL dependencies (including dev for build), ignore scripts for now
RUN npm install -g pnpm

RUN pnpm install --frozen-lockfile

# Copy the rest of the application source code
# This includes tsconfig.json and the src directory
COPY . .

# Build the TypeScript project
RUN ls -la
RUN ./node_modules/.bin/tsc -p tsconfig.json
# The build script already includes chmod +x for the output

# Remove development dependencies after build
RUN pnpm prune --prod --ignore-scripts

# Stage 2: Create the final lightweight image
FROM node:lts-alpine
WORKDIR /app

# Create a non-root user and group for security
# Running as non-root is a good practice
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy built artifacts and production dependencies from the builder stage
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
# Copy package.json for metadata, might be useful for inspection
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

# Switch to the non-root user
USER appuser

# Command to run the server using the built output
# This will start the MCP server listening on stdio
CMD ["node", "dist/index.js"]