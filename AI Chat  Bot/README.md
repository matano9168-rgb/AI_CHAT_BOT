# AI Chatbot Application

A fully functional, professional-grade chatbot application built with Python 3.11+ and React. This chatbot features advanced AI capabilities, conversation memory, file upload support, and a modern web interface.

## 🚀 Features

### Core AI Capabilities
- **OpenAI Integration**: Powered by GPT-4 for intelligent conversations
- **Conversation Memory**: ChromaDB vector database for context retention
- **Multi-turn Dialogues**: Maintains conversation context across sessions
- **Natural Language Processing**: Advanced understanding and response generation

### Plugin System
- **Weather Plugin**: Get current weather for any location
- **News Plugin**: Fetch latest news from various sources
- **Wikipedia Plugin**: Search and retrieve information from Wikipedia
- **Extensible Architecture**: Easy to add new plugins and capabilities

### File Management
- **Document Upload**: Support for PDF, TXT, DOCX, and Markdown files
- **Knowledge Base**: AI can reference uploaded documents in conversations
- **Smart Chunking**: Intelligent document segmentation for better retrieval
- **Vector Search**: Semantic search across uploaded content

### User Experience
- **Modern UI**: Beautiful React frontend with Tailwind CSS
- **Dark/Light Mode**: Theme switching with system preference detection
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Chat**: Smooth conversation flow with typing indicators

### Security & Authentication
- **JWT Authentication**: Secure user login and session management
- **Password Hashing**: Bcrypt encryption for user passwords
- **Input Sanitization**: Protection against prompt injection attacks
- **User Isolation**: Secure data separation between users

### Advanced Features
- **Conversation Export**: Download chats as TXT or JSON
- **Voice Support**: Text-to-speech and speech recognition ready
- **Multi-user Support**: User registration and profile management
- **API Documentation**: Interactive API docs with FastAPI

## 🏗️ Architecture

```
AI Chatbot/
├── backend/                 # FastAPI backend
│   ├── __init__.py
│   ├── main.py             # Main FastAPI application
│   ├── config.py           # Configuration management
│   ├── database.py         # MongoDB models and operations
│   ├── memory.py           # ChromaDB memory management
│   ├── chatbot.py          # Core AI engine
│   ├── auth.py             # Authentication system
│   └── plugins/            # Plugin system
│       ├── __init__.py
│       ├── base.py         # Base plugin class
│       ├── weather.py      # Weather plugin
│       ├── news.py         # News plugin
│       └── wikipedia.py    # Wikipedia plugin
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── stores/         # Zustand state management
│   │   ├── contexts/       # React contexts
│   │   ├── services/       # API services
│   │   └── App.js          # Main app component
│   ├── package.json
│   └── tailwind.config.js  # Tailwind CSS configuration
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
└── README.md               # This file
```

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**: Core programming language
- **FastAPI**: Modern, fast web framework
- **OpenAI**: GPT-4 integration for AI responses
- **ChromaDB**: Vector database for memory and search
- **MongoDB**: Document database for conversations
- **LangChain**: AI framework for enhanced capabilities
- **Pydantic**: Data validation and settings management

### Frontend
- **React 18**: Modern UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **Zustand**: Lightweight state management
- **Axios**: HTTP client for API communication
- **React Router**: Client-side routing

### DevOps & Tools
- **Uvicorn**: ASGI server for FastAPI
- **Motor**: Async MongoDB driver
- **JWT**: JSON Web Token authentication
- **Bcrypt**: Password hashing
- **Pytest**: Testing framework

## 📋 Prerequisites

Before running this application, ensure you have:

- **Python 3.11+** installed
- **Node.js 16+** and npm installed
- **MongoDB** running locally or accessible
- **OpenAI API key** for AI functionality
- **Optional API keys** for plugins (weather, news)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Chat-Bot
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your configuration
# Add your OpenAI API key and other settings
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Start the Backend

```bash
# From the root directory
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TTS_MODEL=tts-1

# Database Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=chatbot_db

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys for Plugins
WEATHER_API_KEY=your_openweathermap_api_key
NEWS_API_KEY=your_newsapi_key
GOOGLE_SEARCH_API_KEY=your_google_search_api_key
GOOGLE_SEARCH_CSE_ID=your_google_search_cse_id

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### Required API Keys

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/)
2. **Weather API Key**: Get from [OpenWeatherMap](https://openweathermap.org/api)
3. **News API Key**: Get from [NewsAPI](https://newsapi.org/)
4. **Google Search API**: Get from [Google Cloud Console](https://console.cloud.google.com/)

## 🔧 Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting

```bash
# Backend
black backend/
isort backend/

# Frontend
cd frontend
npm run format
```

### Building for Production

```bash
# Frontend build
cd frontend
npm run build

# Backend production server
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📱 Usage

### Getting Started

1. **Register/Login**: Create an account or sign in
2. **Start Chatting**: Begin a conversation with the AI
3. **Upload Files**: Add documents to your knowledge base
4. **Use Plugins**: Try weather, news, or Wikipedia queries
5. **Manage Conversations**: View and export chat history

### Plugin Commands

- **Weather**: "What's the weather in London?"
- **News**: "Get news about artificial intelligence"
- **Wikipedia**: "Tell me about Python programming"

### File Upload

Supported formats:
- **Text files**: .txt, .md
- **Documents**: .pdf, .docx
- **Size limit**: 10MB per file

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Considerations

1. **Environment Variables**: Set production values
2. **Database**: Use production MongoDB instance
3. **Security**: Configure CORS and rate limiting
4. **Monitoring**: Add logging and health checks
5. **SSL**: Enable HTTPS in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Review the API documentation at `/docs`
3. Check the logs for error messages
4. Ensure all dependencies are properly installed

## 🔮 Roadmap

- [ ] Voice input/output integration
- [ ] Advanced plugin marketplace
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] Mobile app development
- [ ] Advanced security features
- [ ] Performance optimizations

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- FastAPI team for the excellent web framework
- React team for the frontend framework
- Tailwind CSS for the styling system
- All contributors and open source projects used

---

**Happy Chatting! 🤖✨**
