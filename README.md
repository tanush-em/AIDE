# Next.js + Flask Full-Stack Application

This is a full-stack application with a Next.js frontend and Flask backend with CORS support.

## Project Structure

```
├── frontend/          # Next.js application
├── backend/           # Flask application
└── README.md         # This file
```

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- npm or yarn

## Setup Instructions

### Backend (Flask)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (copy from env.example):
   ```bash
   cp env.example .env
   ```

5. Run the Flask application:
   ```bash
   python app.py
   ```

The backend will be available at `http://localhost:5000`

### Frontend (Next.js)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## API Endpoints

The Flask backend provides the following endpoints:

- `GET /` - Home endpoint
- `GET /api/health` - Health check endpoint
- `GET /api/data` - Sample data endpoint

## Features

- **CORS Support**: The Flask backend is configured with CORS to allow requests from the Next.js frontend
- **TypeScript**: The frontend uses TypeScript for better type safety
- **Tailwind CSS**: Modern styling with Tailwind CSS
- **Environment Variables**: Both applications support environment variables
- **Hot Reload**: Both applications support hot reloading during development

## Development

### Backend Development

The Flask app includes:
- CORS configuration for cross-origin requests
- Environment variable support
- Basic API endpoints
- Error handling

### Frontend Development

The Next.js app includes:
- TypeScript support
- Tailwind CSS for styling
- API integration with the Flask backend
- Responsive design
- Error handling for API calls

## Production Deployment

### Backend

For production deployment of the Flask app:

1. Set `FLASK_ENV=production` in your environment variables
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Frontend

For production deployment of the Next.js app:

1. Build the application:
   ```bash
   npm run build
   ```

2. Start the production server:
   ```bash
   npm start
   ```

## Troubleshooting

### CORS Issues

If you encounter CORS issues:
1. Ensure the Flask backend is running on port 5000
2. Check that the CORS configuration in `app.py` includes the correct frontend URL
3. Verify that both applications are running simultaneously

### Port Conflicts

If port 5000 is already in use:
1. Change the port in the backend `.env` file
2. Update the frontend API calls to use the new port
3. Update the CORS configuration in the backend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## License

This project is open source and available under the MIT License.
