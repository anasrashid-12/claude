# Maxflow Image App - Project Summary

## ✅ Project Overview

Maxflow Image App is a Shopify app that allows merchants to upload product images, process them using AI (e.g., background removal, optimization), and view the processed results. It integrates with Shopify OAuth, Supabase (PostgreSQL), a FastAPI backend, a Next.js frontend, Redis, Celery, and a Dockerized AI microservice.

---

## 📦 Project Structure

```
shopify-ai-image-app/
├── backend/            # FastAPI backend with Celery + Supabase
├── frontend/           # Next.js 15 frontend with Tailwind + Polaris
├── ai-service/         # Dockerized AI microservice (FastAPI)
├── supabase/           # Supabase DB schema + config
├── docker-compose.yml  # Multi-container orchestration
├── .env                # Environment variables
```

---

## 🔐 Shopify OAuth Integration

- Implemented `/auth/install` and `/auth/callback` in backend
- Saves access tokens securely to Supabase
- Uses secure cookies for session management
- Frontend reads shop session via `/api/me` route

---

## 🧠 Backend (FastAPI)

- `main.py` bootstraps API
- Routers: `auth`, `upload_router`, `image_router`, `me`
- Connected to Supabase to log images and settings
- `/upload`: handles image uploads (via AI service)
- `/image/process`: queues image for processing (Redis + Celery)
- `/image/{id}`: fetches processing status
- `/image/supabase/get-images`: fetches all images per shop
- `/me`: returns shop info via session cookie

### ✅ Celery Queue

- Queues image jobs for background processing
- Worker pulls tasks from Redis
- Calls AI service (`http://ai-service:8001/process`)
- Updates Supabase records when done

---

## 🤖 AI Service (Dockerized FastAPI)

- Accepts image uploads at `/upload`
- Processes image tasks at `/process` (background removal, etc.)
- Exposed on `http://localhost:8001`
- Communicates with backend via REST

---

## 💻 Frontend (Next.js 15)

- Built with App Router, TailwindCSS, Polaris UI

### Pages

- `/login`: Shopify store input and OAuth start
- `/dashboard`: Protected layout with gallery, upload, and settings
- `/upload`: Drag-and-drop upload with preview + processing
- `/queue`: Real-time image processing status via polling
- `/settings`: Save per-shop preferences to Supabase

### Components

- `ImageGallery`, `ImageCard`, `UploadForm`, `UploadSection`, `ProtectedLayout`

### API Integration

- Connected to backend using `fetch` and `axios`
- Uses `/me` to validate session and shop context

---

## ⚙️ Supabase

- Tables: `images`, `settings`, `shops`
- CRUD operations via Supabase JS client and REST API
- Anonymous access for frontend (readonly), service role key for backend

---

## 🐳 Docker & Local Dev

- Dockerized backend, AI service, Celery worker, Redis
- `docker-compose up` boots full stack
- Volumes used for file persistence in `uploads/`
- `.env` controls service URLs and Supabase keys

---

## ✅ Completed Features

-

---

## 🧪 Tested Locally

- ✅ Upload flow works end-to-end
- ✅ Queue and processed images display correctly
- ✅ Session and shop info persist securely
- ✅ Settings save and apply per-shop

---

## 🚀 Next Steps (Optional)

- Deployment to Vercel (frontend) and Fly.io / Railway (backend)
- Add Webhook for app uninstall (cleanup Supabase)
- Add billing API integration for monetization

---

This project is now **production-ready and testable locally via Docker Compose**.

> ✅ Let me know if you need a Supabase SQL schema or production deployment assistance!

