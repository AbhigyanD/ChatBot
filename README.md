# TechPal - Educational AI Assistant for Children

🚀 **TechPal** is an educational AI assistant designed to help children (ages 8-16) learn about technology, science, and school subjects in a safe and engaging way.

## 🌟 Features

- **Age-Appropriate Learning**: Tailored responses for different age groups (8-10, 11-13, 14-16)
- **Safety First**: Content filtering and educational focus with safety reminders
- **Multi-LLM Support**: Works with OpenAI GPT and Anthropic Claude
- **Conversation History**: Persistent chat sessions with conversation management
- **Child-Friendly Interface**: Beautiful Streamlit frontend designed for young learners
- **Educational Focus**: Covers technology, science, math, and school subjects

## 🛡️ Safety Features

- Content filtering for inappropriate material
- No personal information collection
- Educational focus with safety reminders
- Encouragement to discuss with parents/teachers
- Age-appropriate language and examples

## 🏗️ Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (easily upgradable to PostgreSQL)
- **LLM Integration**: OpenAI GPT-3.5/4 and Anthropic Claude
- **Frontend**: Streamlit with child-friendly UI
- **API Documentation**: Automatic OpenAPI/Swagger docs

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key OR Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ChatBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys
   ```

4. **Configure API keys**
   - Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
   - OR get an Anthropic API key from [Anthropic Console](https://console.anthropic.com/)
   - Add your key(s) to the `.env` file

### Running the Application

1. **Start the FastAPI backend**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   streamlit run streamlit_app.py
   ```
   The web interface will be available at `http://localhost:8501`

## 📚 API Endpoints

### Core Endpoints

- `GET /` - Welcome page with project information
- `POST /chat` - Main chat endpoint
- `GET /conversations/{session_id}` - Get user conversations
- `GET /conversations/{session_id}/{conversation_id}` - Get conversation details
- `DELETE /conversations/{session_id}/{conversation_id}` - Delete conversation
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Example API Usage

```python
import requests

# Chat with TechPal
response = requests.post("http://localhost:8000/chat", json={
    "message": "How do computers work?",
    "session_id": "user-session-123",
    "age_group": "8-10"
})

print(response.json())
```

## 🎯 Educational Topics Covered

### Technology
- Computer basics and how they work
- Internet and web technologies
- Programming concepts and coding
- Digital tools and applications
- Emerging technologies (AI, robotics, VR)

### School Subjects
- **Math**: Technology-based problem solving
- **Science**: Scientific concepts with tech analogies
- **History**: Evolution of technology and inventors
- **Language Arts**: Digital communication skills
- **Art**: Creative technology applications

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | None |
| `ANTHROPIC_API_KEY` | Anthropic API key | None |
| `DEFAULT_LLM_PROVIDER` | Default LLM provider | `openai` |
| `DATABASE_URL` | Database connection string | `sqlite:///./techpal.db` |
| `DEBUG` | Enable debug mode | `false` |

### LLM Providers

The system supports multiple LLM providers:

- **OpenAI**: GPT-3.5-turbo (default) or GPT-4
- **Anthropic**: Claude-3-Haiku (fast and cost-effective)

## 🗄️ Database Schema

### Tables

- **users**: User sessions and age groups
- **conversations**: Chat conversations with titles
- **messages**: Individual messages with role and content

### Relationships

- Users have many conversations
- Conversations have many messages
- Messages belong to conversations

## 🚀 Deployment

### Local Development

```bash
# Backend
python main.py

# Frontend
streamlit run streamlit_app.py
```

### Production Deployment

1. **Set up a production database** (PostgreSQL recommended)
2. **Configure environment variables**
3. **Use a production WSGI server** (Gunicorn + Uvicorn)
4. **Set up reverse proxy** (Nginx)
5. **Configure SSL certificates**

### Hosting Options

- **Railway**: Easy deployment with automatic scaling
- **Render**: Free tier available with PostgreSQL
- **Heroku**: Traditional hosting with add-ons
- **DigitalOcean**: VPS with full control

## 🔒 Security Considerations

- **Content Filtering**: Basic inappropriate content detection
- **Rate Limiting**: Configurable request limits
- **Input Validation**: Message length and content validation
- **No Personal Data**: Session-based without PII collection
- **Educational Focus**: Redirects inappropriate questions

## 🧪 Testing

### Manual Testing

1. Start both backend and frontend
2. Open Streamlit interface
3. Test different age groups
4. Try various educational topics
5. Test conversation persistence

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do computers work?", "session_id": "test-123", "age_group": "8-10"}'
```

## 🎨 Customization

### System Prompt

The TechPal system prompt is defined in `app/config.py`. You can modify it to:

- Adjust the tone and style
- Add specific educational topics
- Modify safety guidelines
- Change response patterns

### Frontend Styling

The Streamlit interface uses custom CSS for a child-friendly design. Modify the CSS in `streamlit_app.py` to:

- Change colors and themes
- Adjust layout and spacing
- Add animations or effects
- Customize button styles

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- FastAPI for the excellent web framework
- Streamlit for the beautiful frontend framework
- The educational technology community

## 📞 Support

For questions or support:

1. Check the API documentation at `/docs`
2. Review the health endpoint at `/health`
3. Check the logs for error messages
4. Ensure API keys are properly configured

---

**Remember**: TechPal is designed to inspire a lifelong love of learning and technology while keeping children safe and engaged! 🚀
