# syntax=docker/dockerfile:1

# ============================================
# Stage 1: Dependencies - Install all dependencies
# ============================================
FROM node:18-alpine AS deps

# Install libc6-compat for compatibility with some npm packages
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files for dependency installation
# Copying package files separately enables better layer caching
COPY package.json package-lock.json* ./

# Install dependencies with clean install
# npm ci provides faster, more reliable, reproducible builds
RUN npm ci

# ============================================
# Stage 2: Builder - Build the application
# ============================================
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source code
COPY . .

# Set build-time environment variables
# These are needed for the Next.js build process
ENV NEXT_TELEMETRY_DISABLED=1

# Build the Next.js application
# This creates optimized production build in .next directory
RUN npm run build

# ============================================
# Stage 3: Development - Development environment
# ============================================
FROM node:18-alpine AS development

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies (including devDependencies)
RUN npm install

# Copy application files
COPY . .

# Expose development port
EXPOSE 3000

# Set environment to development
ENV NODE_ENV=development

# Start development server with hot reload
CMD ["npm", "run", "dev"]

# ============================================
# Stage 4: Production - Optimized runtime image
# ============================================
FROM node:18-alpine AS production

WORKDIR /app

# Create non-root user (node user already exists in node:alpine)
# Set proper ownership for application files
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Set environment to production
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Copy package files and install production dependencies only
COPY package.json package-lock.json* ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application from builder stage
# Next.js outputs: .next directory contains the production build
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

# If using Next.js standalone output, uncomment these lines:
# COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
# COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user for security
USER nextjs

# Expose production port
EXPOSE 3000

# Configure health check
# Checks if Next.js server is responding
# interval: Check every 30 seconds
# timeout: Wait up to 10 seconds for response
# retries: Mark unhealthy after 3 consecutive failures
# start-period: Give app 30 seconds to start
HEALTHCHECK --start-period=30s --interval=30s --timeout=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start production server
CMD ["npm", "start"]
