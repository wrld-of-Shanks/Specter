# SPECTER Developer Quick Reference

## 🚀 Quick Commands

### Backend
```bash
# Start backend server
cd backend
uvicorn main:app --reload --port 8002

# Run tests
python3 test_system.py

# Install dependencies
pip3 install -r requirements.txt

# Check API docs
open http://localhost:8002/docs
```

### Frontend
```bash
# Start frontend dev server
cd frontend/react_app
npm run dev

# Build for production
npm run build

# Install dependencies
npm install
```

### Database
```bash
# Start local MongoDB
mongod

# Connect to MongoDB
mongosh

# View collections
use specter_legal
show collections
```

---

## 📁 Project Structure

```
lawman-main/
├── backend/
│   ├── main.py                 # Main FastAPI app
│   ├── auth_mongo.py           # Authentication
│   ├── legal_api.py            # Document API
│   ├── document_processor.py   # Text extraction
│   ├── legal_analysis.py       # AI analysis
│   ├── chat_engine_rag.py      # Chat system
│   ├── usage_tracker.py        # Usage limits
│   ├── requirements.txt        # Python deps
│   ├── .env                    # Config (gitignored)
│   └── test_system.py          # Test suite
│
├── frontend/react_app/
│   ├── src/
│   │   ├── App.tsx             # Main component
│   │   ├── Login.tsx           # Login page
│   │   ├── Signup.tsx          # Signup page
│   │   ├── UserProfile.tsx     # Profile page
│   │   └── config.ts           # API config
│   ├── package.json            # Node deps
│   └── vite.config.ts          # Vite config
│
├── SUMMARY.md                  # Complete summary
├── TESTING_GUIDE.md            # Testing guide
├── VERIFICATION_REPORT.md      # Verification report
├── ARCHITECTURE.md             # System architecture
└── quickstart.sh               # Setup script
```

---

## 🔑 Environment Variables

### Required
```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=specter_legal

# JWT
JWT_SECRET_KEY=your-secret-key-here

```

### Optional
```bash
# Email (for lawyer contact)
LAWYER_SMTP_USER=your-email@gmail.com
LAWYER_SMTP_PASS=your-app-password
LAWYER_RECEIVER_EMAIL=lawyer@example.com

# Server
PORT=8002
HOST=0.0.0.0
```

---

## 🌐 API Endpoints

### Authentication
```
POST   /auth/signup          - Create new user
POST   /auth/login           - Login user
GET    /auth/profile         - Get user profile
PUT    /auth/profile         - Update profile
```

### Chat
```
POST   /chat                 - Ask legal question
```

### Document Processing
```
POST   /legal/upload_doc     - Upload document
POST   /legal/analyze_doc    - Analyze document
```

### Usage & Subscription
```
GET    /usage                - Get usage stats
POST   /payment/create-order - Create payment
POST   /payment/verify       - Verify payment
```

### Contact
```
POST   /api/contact_lawyer   - Contact lawyer
```

---

## 🧪 Testing

### Run All Tests
```bash
cd backend
python3 test_system.py
```

### Test Individual Components
```python
# Test document processor
from document_processor import document_processor
text = document_processor.extract_text(file_path)

# Test legal analyzer
from legal_analysis import legal_analyzer
doc_type = legal_analyzer.identify_document_type(text)
summary = legal_analyzer.summarize_document(text, doc_type)

# Test chat engine
from chat_engine_rag import answer_query_with_rag
result = answer_query_with_rag("What is bail?")
```

### Manual API Testing
```bash
# Test upload
curl -X POST http://localhost:8002/legal/upload_doc \
  -F "file=@test.pdf"

# Test chat
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "What is bail?"}'
```

---

## 🐛 Common Issues

### Issue: "Module not found"
```bash
# Solution: Install dependencies
pip3 install -r backend/requirements.txt
```

### Issue: "Tesseract not found"
```bash
# macOS
brew install tesseract poppler

# Ubuntu
sudo apt-get install tesseract-ocr poppler-utils
```

### Issue: "MongoDB connection failed"
```bash
# Check if MongoDB is running
mongod --version

# Start MongoDB
mongod

# Or use MongoDB Atlas (cloud)
```



### Issue: "CORS error"
```bash
# Check CORS settings in main.py
# Ensure frontend URL is allowed
```

---

## 📊 Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String,
  password_hash: String,
  full_name: String,
  subscription_tier: String,  // "free", "basic", "premium"
  created_at: Date,
  updated_at: Date
}
```

### Usage Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  questions_count: Number,
  uploads_count: Number,
  last_reset: Date
}
```

### Contacts Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  name: String,
  email: String,
  phone: String,
  lawyer_type: String,
  budget: String,
  case_description: String,
  created_at: Date
}
```

---

## 🎨 Frontend Components

### Main Components
```typescript
// App.tsx - Main app
function App() {
  const [currentView, setCurrentView] = useState('login');
  const [user, setUser] = useState(null);
  // ...
}

// Login.tsx - Login page
function Login({ onLoginSuccess, onSwitchToSignup }) {
  // ...
}

// UserProfile.tsx - Profile page
function UserProfile({ user, token, onLogout, onBack }) {
  // ...
}
```

### API Calls
```typescript
// Login
const response = await fetch(`${config.API_BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

// Upload document
const formData = new FormData();
formData.append('file', file);
const response = await fetch(`${config.API_BASE_URL}/legal/upload_doc`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

// Chat
const response = await fetch(`${config.API_BASE_URL}/chat`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ message })
});
```

---

## 🔧 Configuration

### Frontend Config (`src/config.ts`)
```typescript
const config = {
  API_BASE_URL: process.env.VITE_API_URL || 'http://localhost:8002'
};
export default config;
```

### Backend Config (`.env`)
```bash
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=specter_legal
JWT_SECRET_KEY=your-secret-key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

---

## 📦 Deployment

### Backend (Render)
1. Push to GitHub
2. Create Web Service on Render
3. Set environment variables
4. Deploy

### Frontend (Netlify)
1. Build: `npm run build`
2. Deploy `dist` folder
3. Set environment variables
4. Configure custom domain

---

## 🔍 Debugging

### Enable Debug Logging
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend console
# Open browser DevTools (F12)
```

### Test Database Connection
```python
from mongodb_config import connect_to_mongo
import asyncio

async def test():
    await connect_to_mongo()
    print("Connected!")

asyncio.run(test())
```

---

## 📈 Performance Tips

1. **Use indexes** on MongoDB collections
2. **Cache** common queries
3. **Optimize** LLM prompts
4. **Compress** responses
5. **Use CDN** for static assets
6. **Enable gzip** compression
7. **Lazy load** components

---

## 🔐 Security Checklist

- [ ] Use HTTPS in production
- [ ] Validate all inputs
- [ ] Sanitize user data
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting
- [ ] Enable CORS properly
- [ ] Hash passwords with bcrypt
- [ ] Use JWT for authentication
- [ ] Delete uploaded files after processing
- [ ] Keep dependencies updated

---

## 📚 Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **MongoDB Docs:** https://docs.mongodb.com/
- **Tesseract Docs:** https://tesseract-ocr.github.io/

---

## 🆘 Getting Help

1. Check `TESTING_GUIDE.md` for troubleshooting
2. Review `ARCHITECTURE.md` for system design
3. Read `SUMMARY.md` for feature overview
4. Run `python3 test_system.py` to verify setup
5. Check logs for error messages

---

**Last Updated:** 2025-12-30  
**Version:** 1.0.0
