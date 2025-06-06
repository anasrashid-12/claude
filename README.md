# Shopify AI Image App

A Shopify application that uses AI to process and enhance product images.

## Project Structure

```
├── frontend/           # Next.js frontend application
├── backend/           # FastAPI backend application
├── docs/             # Documentation
└── Requirements/     # Project requirements and specifications
```

## Prerequisites

- Node.js 18.x or later
- Python 3.8 or later
- Shopify Partner account
- ngrok for local development

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shopify-ai-image-app.git
cd shopify-ai-image-app
```

2. Install dependencies:
```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

3. Set up environment variables:
   - Copy `.env.example` to `.env.local`
   - Fill in your Shopify API credentials and other required variables

4. Start the development servers:
```bash
# Start frontend
npm run dev

# Start backend (in a new terminal)
npm run dev:backend
```

5. Start ngrok:
```bash
ngrok http 3000
```

6. Update your Shopify App URLs in the Shopify Partner dashboard with your ngrok URL.

## Development

- Frontend runs on `http://localhost:3000`
- Backend runs on `http://localhost:8000`
- API documentation available at `http://localhost:8000/docs`

## Features

- OAuth 2.0 authentication with Shopify
- AI-powered image processing
- Product image management
- Batch processing capabilities
- Real-time processing status updates

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository.
