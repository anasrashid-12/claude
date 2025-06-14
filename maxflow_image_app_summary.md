# Maxflow Image App - Project Summary

A Shopify app that allows merchants to upload and process images using AI services like background removal and enhancement.

---

## ✅ Project Overview

**Tech Stack:**

- **Frontend:** Next.js (App Router), Shopify Polaris
- **Backend:** FastAPI (Python), Docker
- **Database:** Supabase
- **AI Service:** FastAPI microservice
- **Queue System:** Celery + Redis
- **Auth:** Shopify OAuth
- **Dev Tunnel:** Shopify CLI + Ngrok

---

## 🏗️ Project Structure

```
shopify-ai-image-app/
├── frontend/         → Next.js 13+ with App Router & Polaris
├── backend/          → FastAPI backend for logic & routing
├── ai-service/       → FastAPI AI microservice
├── supabase/         → DB schema & config
├── .env              → Env config
├── docker-compose.yml → Runs all services in containers
```

---

## ✅ Frontend (Next.js)

- Shopify App Bridge integration
- OAuth Redirect on `/login?shop=...` → FastAPI
- Dashboard Page:
  - Upload image (Dropzone UI)
  - Image gallery
  - Processing queue
  - Background removal trigger button
- Fetch API integration with backend

---

## ✅ Backend (FastAPI)

- `/auth/install` → Shopify OAuth handling
- `/upload` → Image upload handler
- `/shopify/...` → Webhooks and shop-specific logic
- Supabase integration to store:
  - Tenants
  - Uploaded images
  - Processing jobs
- Dockerized + CORS setup

---

## ✅ AI Service (FastAPI)

- `/process-image` endpoint for:
  - Background removal
  - Resize
  - Optimization
  - Enhancement
- Built-in `ImageProcessor` class
- Docker containerized
- Celery + Redis for async queue

---

## ✅ Queue System (Celery + Redis)

- FastAPI submits task
- Celery worker processes image
- Updates Supabase on completion

---

## ✅ Currently Working

- Shopify app install via OAuth
- Dev tunnel using Shopify CLI (Ngrok)
- Image upload and redirect to AI
- Docker services running smoothly
- Supabase database linked
- Shopify app loading

---

## ⚠️ Pending / Bugs

-

---

Let me know if you want an architecture diagram or final deployment checklist!

