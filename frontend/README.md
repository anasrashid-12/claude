# Shopify AI Image Processing App - Frontend

This is the frontend application for the Shopify AI Image Processing App, built with Next.js and Shopify's Polaris design system.

## Features

- 🛠️ Built with Next.js 14 and TypeScript
- 🎨 Shopify Polaris design system integration
- 🔒 Secure authentication with Shopify OAuth
- 📸 AI-powered image processing capabilities
- 📊 Real-time processing status and statistics
- 🔄 Background task management
- 📱 Responsive design for all devices

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm 9.x or later
- A Shopify Partner account
- A Shopify development store

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Copy the environment template:
   ```bash
   cp src/env.local.template .env.local
   ```
4. Fill in your environment variables in `.env.local`

### Development

```bash
# Start development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format

# Run tests
npm run test

# Build for production
npm run build

# Analyze bundle
npm run analyze
```

## Project Structure

```
frontend/
├── src/
│   ├── app/           # Next.js 14 app directory
│   ├── components/    # Reusable components
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Core utilities and API clients
│   ├── types/         # TypeScript type definitions
│   ├── utils/         # Helper functions
│   └── config/        # Configuration files
├── public/           # Static assets
└── tests/           # Test files
```

## Testing

- Unit tests with Jest and React Testing Library
- Integration tests for critical user flows
- Coverage thresholds set to 70%

## Performance

- Bundle analysis with @next/bundle-analyzer
- Image optimization with next/image
- Code splitting and lazy loading
- Efficient caching strategies

## Best Practices

- TypeScript for type safety
- ESLint for code quality
- Prettier for consistent formatting
- Husky for pre-commit hooks
- SWR for data fetching
- React Query for server state management

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
