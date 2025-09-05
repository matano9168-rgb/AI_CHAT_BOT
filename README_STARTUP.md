# AI Chatbot - Quick Start Guide

## 🚀 Quick Start (Recommended)

### Option 1: Simple Backend Only
```bash
# Install Python dependencies and start backend
python start_simple.py
```

### Option 2: Full Application
```bash
# Start both backend and frontend
python start_all.py
```

## 📋 Prerequisites

### Required
- Python 3.8+ 
- Node.js 16+ (for frontend)

### Optional (for full features)
- MongoDB (for persistent storage)
- OpenAI API key (for AI features)
- Weather API key (for weather plugin)
- News API key (for news plugin)

## 🔧 Setup Steps

### 1. Backend Setup
```bash
# Install minimal dependencies
pip install -r requirements_minimal.txt

# Start backend server
python start_simple.py
```

The backend will start at: http://localhost:8000

### 2. Frontend Setup (Optional)
```bash
cd frontend
npm install
npm start
```

The frontend will start at: http://localhost:3000

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔑 Configuration

### Environment Variables (.env file)
```env
# Minimal required settings
SECRET_KEY=your-secret-key-change-in-production-12345
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Optional: Add these for full features
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017
WEATHER_API_KEY=your_weather_api_key
NEWS_API_KEY=your_news_api_key
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Change PORT in .env file
   - Or kill existing process: `lsof -ti:8000 | xargs kill`

2. **Dependencies missing**
   - Run: `pip install -r requirements_minimal.txt`

3. **MongoDB connection error**
   - Install MongoDB or ignore (app works without it)
   - Or use MongoDB Atlas cloud service

4. **OpenAI API errors**
   - Add valid OPENAI_API_KEY to .env file
   - Or use app without AI features

### Getting Help

1. Check the health endpoint: http://localhost:8000/health
2. View logs in terminal
3. Check API docs: http://localhost:8000/docs

## 📱 Usage

### Without Frontend
- Use API directly: http://localhost:8000/docs
- Test with curl or Postman

### With Frontend
- Register new account at: http://localhost:3000/register
- Login and start chatting
- Upload documents to knowledge base
- View conversation history

## 🎯 Features Available

### ✅ Working without external dependencies:
- User authentication
- Basic chat interface
- File upload
- Conversation history
- Plugin system (basic)

### 🔧 Requires API keys:
- AI-powered responses (OpenAI)
- Weather information (OpenWeatherMap)
- News updates (NewsAPI)
- Persistent storage (MongoDB)

## 🚀 Production Deployment

1. Set strong SECRET_KEY
2. Configure production database
3. Set DEBUG=False
4. Use proper web server (nginx + gunicorn)
5. Enable HTTPS
6. Set up monitoring

---

**Need help?** Check the logs and API documentation at `/docs`