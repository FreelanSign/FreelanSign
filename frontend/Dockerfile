# frontend/Dockerfile
FROM node:22-alpine AS base

WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts

# Target development
FROM base AS development
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# Target production
FROM base AS production
COPY . .
RUN npm run build

FROM nginx:alpine AS production-server
COPY --from=production /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
