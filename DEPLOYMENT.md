# 🚀 Railway Deployment Guide

This guide will walk you through deploying your MaxFlow AI Image App to Railway with **4 separate services**:

1. **Frontend** (Next.js)
2. **Backend API** (FastAPI) 
3. **Celery Worker** (Background tasks)
4. **Redis** (Message broker)

## 📋 Prerequisites

- GitHub repository with your code
- Railway account ([sign up here](https://railway.app))
- Shopify Partner account
- Supabase project
- MakeIt3D API key

## 🔧 Step 1: Prepare Your Environment Variables

Before deployment, gather all your environment variables:

### Frontend Variables
```env
NEXT_PUBLIC_SHOPIFY_API_KEY=your_shopify_api_key
NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend.railway.app
JWT_SECRET=your_jwt_secret_key
```

### Backend Variables
```env
BACKEND_URL=https://your-backend.railway.app
FRONTEND_URL=https://your-frontend.railway.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=makeit3d-public
REDIS_URL=redis://your-redis.railway.app:6379
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-api-secret
SHOPIFY_SCOPES=read_products,write_products
SHOPIFY_API_VERSION=2025-07
JWT_SECRET=your-super-secure-jwt-secret
MAKEIT3D_API_KEY=your-makeit3d-api-key
CREDITS_CURRENCY=USD
SANDBOX_MODE=false
RL_BURST_LIMIT=10
RL_BURST_WINDOW=1
RL_SUST_LIMIT=60
RL_SUST_WINDOW=60
SENTRY_DSN=your-sentry-dsn
```

### Celery Variables
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=makeit3d-public
REDIS_URL=redis://your-redis.railway.app:6379
MAKEIT3D_API_KEY=your-makeit3d-api-key
SENTRY_DSN=your-sentry-dsn
```

## 🚀 Step 2: Deploy Redis

### 2.1 Create Redis Service

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Add Service" → "Redis"
4. Railway will automatically provision a Redis instance
5. **Note the generated Redis URL** (e.g., `redis://your-redis.railway.app:6379`)

## 🖥️ Step 3: Deploy Backend API

### 3.1 Create Backend Project

1. In the same Railway project, click "Add Service"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. **Important**: Select the `backend` directory as the source

### 3.2 Configure Backend Environment

1. In your Railway project, go to "Variables" tab
2. Add all backend environment variables listed above
3. **Important**: Set `REDIS_URL` to your Redis URL from Step 2
4. Make sure to use the same `JWT_SECRET` for both backend and frontend

### 3.3 Deploy Backend

1. Railway will automatically detect it's a Python FastAPI app
2. Click "Deploy Now"
3. Wait for deployment to complete
4. **Note the generated URL** (e.g., `https://your-backend.railway.app`)

## 🔄 Step 4: Deploy Celery Worker

### 4.1 Create Celery Service

1. In the same Railway project, click "Add Service"
2. Select "Deploy from GitHub repo"
3. Choose the same repository
4. **Important**: Select the `backend` directory as the source

### 4.2 Configure Celery Environment

1. In the Variables tab, add all Celery environment variables listed above
2. **Important**: Set `REDIS_URL` to your Redis URL from Step 2

### 4.3 Configure Celery Build Settings

Railway should automatically detect Python, but verify these settings:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `celery -A app.celery_app:celery_app worker --loglevel=info -Q image_queue,polling_queue`

### 4.4 Deploy Celery

1. Click "Deploy Now"
2. Wait for deployment to complete
3. Verify the Celery worker is running by checking logs

## 🎨 Step 5: Deploy Frontend

### 5.1 Create Frontend Project

1. Create a **new** Railway project
2. Select "Deploy from GitHub repo"
3. Choose the same repository
4. **Important**: Select the `frontend` directory as the source

### 5.2 Configure Frontend Environment

1. In the Variables tab, add all frontend environment variables listed above
2. **Important**: Set `NEXT_PUBLIC_BACKEND_URL` to your backend URL from Step 3
3. Set `NEXT_PUBLIC_FRONTEND_URL` to your frontend URL (Railway will provide this)

### 5.3 Configure Build Settings

Railway should automatically detect Next.js, but verify these settings:

- **Build Command**: `npm run build`
- **Start Command**: `npm start`
- **Output Directory**: `.next`

### 5.4 Deploy Frontend

1. Click "Deploy Now"
2. Wait for build and deployment to complete
3. **Note the generated URL** (e.g., `https://your-frontend.railway.app`)

## 🔗 Step 6: Configure Shopify App

### 6.1 Update App URLs

1. Go to your [Shopify Partner Dashboard](https://partners.shopify.com)
2. Navigate to your app
3. Go to "App Setup" → "App URLs"
4. Update the following:

```
App URL: https://your-frontend.railway.app
Allowed redirection URLs:
- https://your-frontend.railway.app/auth/callback
- https://your-frontend.railway.app/auth/toplevel
```

### 6.2 Configure Webhooks

1. In your app settings, go to "Webhooks"
2. Add webhook endpoints pointing to your backend:
   - URL: `https://your-backend.railway.app/webhooks/shopify`
   - Events: Select the events you need

## ✅ Step 7: Test Your Deployment

### 7.1 Test Frontend
1. Visit your frontend URL
2. Verify the page loads without errors
3. Check browser console for any issues

### 7.2 Test Authentication
1. Try installing the app on a test Shopify store
2. Verify the OAuth flow works
3. Check that you can access the dashboard

### 7.3 Test Features
1. Upload an image
2. Verify processing works
3. Check real-time updates
4. Test credit system

### 7.4 Test Background Tasks
1. Upload an image that requires processing
2. Check Celery worker logs to ensure tasks are being processed
3. Verify the image status updates in real-time

## 🔍 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check Railway logs for:
- Missing environment variables
- Node.js/Python version issues
- Build command errors
- Dependency installation failures
```

#### Authentication Issues
- Verify Shopify app URLs are correct
- Check redirect URLs in Partner Dashboard
- Ensure backend is accessible from frontend
- Verify JWT_SECRET is the same across services

#### Celery Tasks Not Processing
- Ensure Celery worker is running
- Check Redis connection
- Verify queue names match (`image_queue`, `polling_queue`)
- Check Celery worker logs for errors

#### Real-time Not Working
- Verify Supabase configuration
- Check network connectivity
- Review browser console for errors
- Ensure Supabase realtime is enabled

#### Redis Connection Issues
- Verify Redis URL is correct
- Check Redis service is running
- Ensure Redis URL is accessible from both backend and Celery

### Debug Commands

```bash
# Check Railway logs for each service
railway logs --service frontend
railway logs --service backend
railway logs --service celery
railway logs --service redis

# View environment variables
railway variables

# Restart deployment
railway up

# Check service status
railway status
```

### Service-Specific Debugging

#### Frontend Issues
```bash
# Check build logs
railway logs --service frontend

# Verify environment variables
railway variables --service frontend
```

#### Backend Issues
```bash
# Check API logs
railway logs --service backend

# Test health endpoint
curl https://your-backend.railway.app/health
```

#### Celery Issues
```bash
# Check Celery worker logs
railway logs --service celery

# Verify Celery is processing tasks
# Look for messages like "Received task: app.tasks.image_tasks.submit_job_task"
```

#### Redis Issues
```bash
# Check Redis logs
railway logs --service redis

# Test Redis connection
# The backend and Celery services should show successful Redis connections
```

## 🔄 Updating Your App

### Automatic Updates
1. Push changes to your GitHub repository
2. Railway will automatically redeploy all services
3. Monitor deployment logs for each service

### Manual Updates
1. Go to your Railway project
2. Click "Deploy" on the service you want to update
3. Check logs for any issues

### Service-Specific Updates
- **Frontend**: Updates automatically when you push to GitHub
- **Backend**: Updates automatically when you push to GitHub
- **Celery**: Updates automatically when you push to GitHub
- **Redis**: Managed by Railway, no manual updates needed

## 📊 Monitoring

### Railway Dashboard
- Monitor resource usage for all services
- Check deployment status
- View logs and errors
- Monitor service health

### Service Monitoring
- **Frontend**: Monitor Next.js build and runtime logs
- **Backend**: Monitor FastAPI logs and performance
- **Celery**: Monitor task processing and queue status
- **Redis**: Monitor memory usage and connection status

### Sentry Integration
- Your app includes Sentry for error monitoring
- Check your Sentry dashboard for production errors
- Monitor performance metrics

## 🆘 Support

If you encounter issues:

1. **Check Railway Logs**: Look for error messages in each service
2. **Verify Environment Variables**: Ensure all required variables are set
3. **Test Locally**: Try running the app locally first
4. **Railway Support**: [Railway Documentation](https://docs.railway.app)
5. **GitHub Issues**: Create an issue in your repository

## 🎉 Success!

Once deployed successfully, your app will be available at:
- **Frontend**: `https://your-frontend.railway.app`
- **Backend**: `https://your-backend.railway.app`
- **Celery Worker**: Running in background
- **Redis**: Managed by Railway

Your Shopify app is now ready for production use! 🚀

### Final Checklist

- [ ] All 4 services are deployed and running
- [ ] Environment variables are correctly set
- [ ] Shopify app URLs are updated
- [ ] Webhooks are configured
- [ ] Authentication flow works
- [ ] Image upload and processing works
- [ ] Real-time updates are working
- [ ] Credit system is functional
- [ ] Error monitoring is set up
- [ ] All services are healthy in Railway dashboard
