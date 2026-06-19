# 🚀 Vetra Backend

Backend service for **Vetra** — real-time chat application built with FastAPI, WebSockets, MySQL and Docker.

---

## 🧠 Tech Stack

- Python 3.12+
- FastAPI
- WebSockets
- SQLAlchemy (Async)
- MySQL
- Docker / Docker Compose
- Pydantic
- JWT Authentication

---

## 📦 Features

- JWT authentication
- Real-time messaging via WebSockets
- User system
- Chat rooms
- Message persistence
- Async architecture (FastAPI)
- Dockerized environment

---

## 🏗 Project Structure

```
app/
 ├── api/
 ├── core/
 ├── db/
 ├── models/
 ├── services/
 ├── main.py

docker-compose.yml
.env
```

---

## ⚙️ Setup (Development)

### 1. Clone project

```bash
git clone https://github.com/FFG2077/Vetra.git
cd Vetra
```

### 2. Create .env
```
DATABASE_URL=mysql+aiomysql://user:password@db:3306/vetra
JWT_SECRET_KEY=super_secret_key
DEBUG=false

MYSQL_ROOT_PASSWORD=root_password
MYSQL_DATABASE=vetra
MYSQL_USER=user
MYSQL_PASSWORD=password
```

### 3. Run with Docker
docker compose up --build -d

### 4. API available at:
http://localhost:8000
http://localhost:8000/docs

### 🔌 WebSocket available at:
ws://localhost:8000/ws/{chat_uuid}

---

## 🐳 Docker Services

### MySQL
- Port: 3306
- Volume: db_data

### Backend
- Port: 8000
- Reload: enabled (dev mode)

---

## 📌 Status:
- Alpha version — actively in development

## 📌 Notes
- WebSockets are used for real-time communication
- Database runs inside Docker container
- Ensure ports 8000 and 3306 are free
- Environment variables are required via `.env`

## 🔐 Security
- Never commit `.env`
- Do not expose MySQL root credentials in production
- Use separate DB user for backend (recommended)
