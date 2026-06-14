# SPECTER System Testing & Deployment Guide

## Overview
This guide helps you verify that all components of SPECTER are working correctly, especially the document upload, summarization, and verification features.

## Prerequisites

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install System Dependencies (for OCR)
**macOS:**
```bash
brew install tesseract
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

### 3. Setup Ollama (for LLM features)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama2
```

### 4. Setup MongoDB
You need a MongoDB instance running. Options:
- **Local:** Install MongoDB locally
- **Cloud:** Use MongoDB Atlas (free tier available)

Update your `.env` file with MongoDB connection string.

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and fill in the values:
```bash
cp backend/.env.example backend/.env
```

Required variables:
- `MONGODB_URL` - MongoDB connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `OLLAMA_BASE_URL` - Ollama API URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - Model name (default: llama2)

## Running Tests

### Quick Test
Run the comprehensive test suite:
```bash
cd backend
python3 test_system.py
```

This will test:
- ✓ All module imports
- ✓ Document type identification
- ✓ Chat engine (RAG system)
- ✓ Document processor
- ✓ Legal analyzer

### Manual Testing

#### 1. Test Document Upload
```bash
# Start the backend server
cd backend
uvicorn main:app --reload --port 8002

# In another terminal, test upload
curl -X POST "http://localhost:8002/legal/upload_doc" \
  -F "file=@/path/to/test/document.pdf"
```

#### 2. Test Document Analysis
```bash
curl -X POST "http://localhost:8002/legal/analyze_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a rent agreement...",
    "doc_type": "Rent Agreement",
    "action": "summarize",
    "target_lang": "English"
  }'
```

#### 3. Test Chat
```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "What is bail?"}'
```

## Frontend Testing

### 1. Install Frontend Dependencies
```bash
cd frontend/react_app
npm install
```

### 2. Configure Frontend
Update `frontend/react_app/src/config.ts`:
```typescript
const config = {
  API_BASE_URL: 'http://localhost:8002'
};
```

### 3. Run Frontend
```bash
npm run dev
```

### 4. Test Document Upload Feature
1. Navigate to http://localhost:5173
2. Login/Signup
3. Click "Upload Documents"
4. Choose analysis type (Summarize/Translate/Verify)
5. Upload a test document (PDF, DOCX, TXT, or image)
6. Verify the analysis results

## Common Issues & Solutions

### Issue 1: "Tesseract not found"
**Solution:** Install Tesseract OCR
```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr
```

### Issue 2: "Poppler not found"
**Solution:** Install Poppler for PDF processing
```bash
# macOS
brew install poppler

# Ubuntu
sudo apt-get install poppler-utils
```

### Issue 3: "Ollama connection failed"
**Solution:** 
1. Ensure Ollama is running: `ollama serve`
2. Check if model is pulled: `ollama list`
3. Pull model if needed: `ollama pull llama2`

### Issue 4: "MongoDB connection failed"
**Solution:**
1. Check if MongoDB is running
2. Verify connection string in `.env`
3. For MongoDB Atlas, ensure IP whitelist is configured

### Issue 5: "Upload limit reached"
**Solution:** This is expected for free tier users. Either:
1. Upgrade subscription
2. Reset usage in MongoDB manually
3. Use admin account for testing

## Feature Verification Checklist

### Document Upload Feature
- [ ] Can upload PDF files
- [ ] Can upload DOCX files
- [ ] Can upload TXT files
- [ ] Can upload image files (PNG, JPG)
- [ ] Text extraction works correctly
- [ ] Document type is identified correctly

### Document Summarization
- [ ] Summary is generated
- [ ] Key entities are extracted
- [ ] Important clauses are identified
- [ ] Summary is accurate and relevant

### Document Translation
- [ ] Translation to Hindi works
- [ ] Translation to other languages works
- [ ] Legal terminology is preserved
- [ ] Translation is accurate

### Document Verification
- [ ] Checklist items are verified
- [ ] Verdict is provided
- [ ] Analysis is detailed
- [ ] Recommendations are given

### Chat Feature
- [ ] Can ask legal questions
- [ ] Receives relevant answers
- [ ] Sources are cited
- [ ] Multi-language support works

### Authentication
- [ ] Can signup
- [ ] Can login
- [ ] Can logout
- [ ] Token is stored correctly
- [ ] Protected routes work

### Usage Tracking
- [ ] Usage stats are displayed
- [ ] Limits are enforced
- [ ] Upgrade modal appears when limit reached

## Performance Optimization

### For Production Deployment

1. **Use Production MongoDB**
   - Use MongoDB Atlas or dedicated MongoDB server
   - Enable connection pooling

2. **Optimize LLM Calls**
   - Use smaller models for faster response
   - Implement caching for common queries
   - Consider using API-based LLMs (OpenAI, etc.)

3. **Enable Caching**
   - Cache document analysis results
   - Cache chat responses for common queries

4. **Use CDN for Frontend**
   - Deploy frontend to Netlify/Vercel
   - Use CDN for static assets

5. **Scale Backend**
   - Use Gunicorn with multiple workers
   - Deploy to cloud platform (Render, Railway, etc.)

## Deployment

### Backend Deployment (Render)
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Set environment variables
5. Deploy

### Frontend Deployment (Netlify)
1. Build frontend: `npm run build`
2. Deploy `dist` folder to Netlify
3. Configure environment variables
4. Set up custom domain (optional)

## Monitoring

### Health Check
```bash
curl http://localhost:8002/health
```

### Usage Stats
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8002/usage
```

## Support

For issues or questions:
1. Check the logs: `tail -f backend/logs/app.log`
2. Review error messages in browser console
3. Check MongoDB logs
4. Review Ollama logs

## License
See LICENSE file for details.
