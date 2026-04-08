# Fitness-AI-APP
# 🚀 Fitness AI App - Deployment Guide

Complete guide to deploy the Fitness AI application on a different host/server.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment Options](#cloud-deployment-options)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **pip** - Python package manager (comes with Python)
- **Git** - [Download](https://git-scm.com/downloads)

### Optional (for production)
- **Nginx** - Web server/reverse proxy
- **PostgreSQL** - Production database
- **Docker** - Containerization (optional)

---

## Local Development Setup

### Step 1: Clone/Copy the Project

```bash
# If using Git
git clone <repository-url>
cd fitness-ai-app

# Or simply copy the project folder to your new location
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8486
```

The backend will be available at: `http://localhost:8486`

### Step 3: Frontend Setup

The frontend is a static HTML application. You have two options:

**Option A: Direct File Access**
- Simply open `frontend/dashboard.html` in your web browser
- Update the API URL in the file if needed (line 750):
  ```javascript
  const API_URL = 'http://localhost:8486';
  ```

**Option B: Using a Web Server (Recommended)**
```bash
# Navigate to frontend directory
cd frontend

# Using Python's built-in server
python -m http.server 8080

# Or using Node.js http-server (if installed)
npx http-server -p 8080
```

Then open: `http://localhost:8080/dashboard.html`

---

## Production Deployment

### Option 1: Traditional Server Deployment (Linux)

#### 1. Prepare the Server

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and required tools
sudo apt install python3 python3-pip python3-venv nginx -y

# Install PostgreSQL (optional, for production database)
sudo apt install postgresql postgresql-contrib -y
```

#### 2. Deploy the Application

```bash
# Create application directory
sudo mkdir -p /var/www/fitness-ai
cd /var/www/fitness-ai

# Copy your project files here
# You can use scp, rsync, or git clone

# Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service for backend
sudo nano /etc/systemd/system/fitness-ai.service
```

**fitness-ai.service content:**
```ini
[Unit]
Description=Fitness AI Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/fitness-ai/backend
Environment="PATH=/var/www/fitness-ai/backend/venv/bin"
ExecStart=/var/www/fitness-ai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8486
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable fitness-ai
sudo systemctl start fitness-ai
sudo systemctl status fitness-ai
```

#### 3. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/fitness-ai
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # Frontend
    location / {
        root /var/www/fitness-ai/frontend;
        index dashboard.html;
        try_files $uri $uri/ /dashboard.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8486/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/fitness-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Update Frontend API URL

Edit `frontend/dashboard.html` (line 750):
```javascript
const API_URL = 'http://your-domain.com/api';  // Or your server IP
```

#### 5. Set Up SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

### Option 2: Docker Deployment

#### 1. Create Dockerfile for Backend

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8486

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8486"]
```

#### 2. Create docker-compose.yml

Create `docker-compose.yml` in project root:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8486:8486"
    volumes:
      - ./backend:/app
      - ./backend/fitness_ai.db:/app/fitness_ai.db
    environment:
      - DATABASE_URL=sqlite:///./fitness_ai.db
    restart: unless-stopped

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
    restart: unless-stopped
```

#### 3. Create nginx.conf

```nginx
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        index dashboard.html;
        try_files $uri $uri/ /dashboard.html;
    }
    
    location /api/ {
        proxy_pass http://backend:8486/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. Deploy with Docker

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## Cloud Deployment Options

### AWS EC2

1. Launch an EC2 instance (Ubuntu 20.04 LTS recommended)
2. Configure security groups (allow ports 80, 443, 8486)
3. SSH into the instance
4. Follow the "Traditional Server Deployment" steps above

### Heroku

1. Install Heroku CLI
2. Create `Procfile` in backend directory:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Deploy:
   ```bash
   heroku create fitness-ai-app
   git push heroku main
   ```

### DigitalOcean

1. Create a Droplet (Ubuntu)
2. Follow the "Traditional Server Deployment" steps
3. Use DigitalOcean's App Platform for easier deployment

### Vercel (Frontend Only)

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy frontend:
   ```bash
   cd frontend
   vercel
   ```
3. Update API_URL to point to your backend

---

## Configuration

### Environment Variables

Create `backend/.env`:
```env
# Database
DATABASE_URL=sqlite:///./fitness_ai.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/fitness_ai

# API Settings
API_HOST=0.0.0.0
API_PORT=8486

# CORS (add your frontend domain)
ALLOWED_ORIGINS=http://localhost:8080,https://your-domain.com
```

### Frontend Configuration

Update `frontend/dashboard.html`:
```javascript
// Line 750 - Update API URL
const API_URL = 'http://your-server-ip:8486';
// Or with domain and reverse proxy:
const API_URL = 'https://your-domain.com/api';
```

### Database Migration (SQLite to PostgreSQL)

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE fitness_ai;
CREATE USER fitness_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fitness_ai TO fitness_user;
\q

# Update .env
DATABASE_URL=postgresql://fitness_user:your_password@localhost/fitness_ai

# Restart application
sudo systemctl restart fitness-ai
```

---

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Find process using port 8486
sudo lsof -i :8486
# Kill the process
sudo kill -9 <PID>
```

**Database connection errors:**
```bash
# Check if database file exists
ls -la backend/fitness_ai.db

# Check permissions
sudo chown -R www-data:www-data /var/www/fitness-ai
```

**Module not found errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**CORS errors:**
- Update CORS settings in `backend/app/main.py`
- Add your frontend domain to `allow_origins`

**API connection failed:**
- Check if backend is running: `curl http://localhost:8486/health`
- Verify API_URL in frontend code
- Check firewall settings

### Service Issues

**Check service status:**
```bash
sudo systemctl status fitness-ai
sudo journalctl -u fitness-ai -f
```

**Restart services:**
```bash
sudo systemctl restart fitness-ai
sudo systemctl restart nginx
```

---

## Quick Start Checklist

- [ ] Install Python 3.8+
- [ ] Clone/copy project to new location
- [ ] Install backend dependencies
- [ ] Update API URL in frontend
- [ ] Run backend server
- [ ] Access frontend in browser
- [ ] Test registration and login
- [ ] Create profile and test features

---

## Security Recommendations

1. **Use HTTPS** - Always use SSL certificates in production
2. **Environment Variables** - Never commit `.env` files
3. **Database** - Use PostgreSQL in production, not SQLite
4. **Firewall** - Configure firewall to allow only necessary ports
5. **Updates** - Keep all dependencies updated
6. **Backups** - Regular database backups
7. **Authentication** - Implement JWT tokens for production

---

## Support

For deployment issues:
1. Check logs: `sudo journalctl -u fitness-ai -f`
2. Verify all services are running
3. Check firewall and security group settings
4. Ensure all dependencies are installed

---

**Happy Deploying! 🚀**
