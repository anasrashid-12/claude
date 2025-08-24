# 🧠 MaxFlow AI Image App - Frontend

A modern, production-ready Shopify app for AI-powered image processing built with Next.js 15, TypeScript, and Tailwind CSS.

## 🚀 Features

- **AI Image Processing**: Remove backgrounds, upscale, and optimize images
- **Shopify Integration**: Seamless integration with Shopify Admin
- **Real-time Updates**: Live status updates via Supabase realtime
- **Credit System**: Pay-per-use credit management
- **Dark/Light Mode**: Beautiful responsive UI with theme switching
- **Batch Upload**: Upload multiple images simultaneously
- **Progress Tracking**: Real-time upload and processing progress
- **Gallery View**: Browse and download processed images
- **Settings Management**: Customize app preferences and avatar

## 🛠️ Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shopify Polaris + Custom Components
- **State Management**: React Context + SWR
- **Real-time**: Supabase Realtime
- **Authentication**: Shopify App Bridge
- **Error Monitoring**: Sentry
- **Deployment**: Railway

## 📋 Prerequisites

Before you begin, ensure you have:

- Node.js 18+ installed
- npm or yarn package manager
- Shopify Partner account
- Supabase project
- Railway account (for deployment)

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── dashboard/         # Dashboard pages
│   │   ├── auth/             # Authentication pages
│   │   └── api/              # API routes
│   ├── components/           # Reusable UI components
│   ├── hooks/               # Custom React hooks
│   └── utils/               # Utility functions
├── public/                  # Static assets
├── utils/                   # Shared utilities
└── Dockerfile              # Docker configuration
```

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd shopify-ai-image-app/frontend

# Install dependencies
npm install
```

### 2. Environment Setup

Create a `.env.local` file in the frontend directory:

```env
# Shopify Configuration
NEXT_PUBLIC_SHOPIFY_API_KEY=your_shopify_api_key

# Backend Configuration
NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Frontend URL (for production)
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend.railway.app

# JWT Secret (for session management)
JWT_SECRET=your_jwt_secret_key
```

### 3. Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### 4. Build and Test

```bash
# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint
```

## �� Railway Deployment

For detailed deployment instructions, see the main [DEPLOYMENT.md](../DEPLOYMENT.md).

### Quick Deployment Overview

1. **Create Railway Project**:
   - Go to [Railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - **Important**: Select the `frontend` directory as the source

2. **Configure Environment Variables**:
   ```env
   # Shopify Configuration
   NEXT_PUBLIC_SHOPIFY_API_KEY=your_shopify_api_key
   
   # Backend URL (from backend deployment)
   NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app
   
   # Supabase Configuration
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   
   # Frontend URL (Railway will provide this)
   NEXT_PUBLIC_FRONTEND_URL=https://your-frontend.railway.app
   
   # JWT Secret (same as backend)
   JWT_SECRET=your_jwt_secret_key
   ```

3. **Deploy**:
   - Railway will automatically detect Next.js
   - Click "Deploy Now"
   - Wait for build and deployment to complete

## 🔧 Configuration

### Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_SHOPIFY_API_KEY` | Your Shopify app's API key | ✅ |
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | ✅ |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | ✅ |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | ✅ |
| `NEXT_PUBLIC_FRONTEND_URL` | Frontend URL for redirects | ✅ |
| `JWT_SECRET` | Secret for JWT token signing | ✅ |

### Shopify App Configuration

1. **Required Scopes**:
   - `write_products`
   - `write_script_tags`
   - `read_products`

2. **App Bridge Configuration**:
   - API Key: Your Shopify app's API key
   - Host: Automatically provided by Shopify

## 🧪 Testing

```bash
# Run linting
npm run lint

# Type checking
npx tsc --noEmit

# Build test
npm run build
```

## 📦 Build & Deployment

### Local Build

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start
```

### Docker Build

```bash
# Build Docker image
docker build -t maxflow-frontend .

# Run container
docker run -p 3000:3000 maxflow-frontend
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check all environment variables are set
   - Verify Node.js version (18+)
   - Clear `.next` cache: `rm -rf .next`

2. **Authentication Issues**:
   - Verify Shopify app configuration
   - Check redirect URLs in Partner Dashboard
   - Ensure backend is accessible

3. **Real-time Not Working**:
   - Verify Supabase configuration
   - Check network connectivity
   - Review browser console for errors

4. **Upload Failures**:
   - Check file size limits (5MB)
   - Verify backend is running
   - Check credit balance

### Debug Mode

Enable debug logging by setting:
```env
NODE_ENV=development
```

## 📚 API Reference

### Key Endpoints

- `POST /upload` - Upload images
- `GET /images/{image_id}` - Get image status
- `GET /images` - List all images for shop
- `GET /credits/me` - Get user's credit balance
- `POST /credits/checkout` - Purchase credits

### Authentication

All API calls require session cookies set by the backend authentication flow.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and main [DEPLOYMENT.md](../DEPLOYMENT.md)
- **Issues**: Create an issue in the GitHub repository
- **Shopify Support**: [Shopify Developer Documentation](https://shopify.dev/)

## 🔄 Updates

To update the deployed app:

1. Push changes to your GitHub repository
2. Railway will automatically redeploy
3. Monitor the deployment logs for any issues

---

**Built with ❤️ using Next.js, TypeScript, and Shopify App Bridge**
