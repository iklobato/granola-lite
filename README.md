# Notes App with AI-Powered Q&A and Voice Dictation

A full-stack web application that combines note-taking with AI-powered question answering and voice dictation capabilities. Built with React, FastAPI, PostgreSQL with pgvector, and Ollama for local LLM processing.

## 🚀 What It Is

This is a modern note-taking application that allows users to:
- **Create, edit, and manage notes** with a clean, intuitive interface
- **Use voice dictation** to create notes by speaking (supports 11 languages)
- **Ask AI-powered questions** about their notes using Retrieval-Augmented Generation (RAG)
- **Maintain conversation history** with context-aware AI responses
- **Search through notes** using vector similarity search

## 🏗️ Architecture Overview

The application follows a microservices architecture deployed on Kubernetes:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   PostgreSQL    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   + pgvector    │
│   Port: 30090   │    │   Port: 30080   │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Ollama      │
                       │   (Local LLM)   │
                       │   Port: 11434   │
                       └─────────────────┘
```

## 🧩 Components

### Frontend (React)
- **Technology**: React 18 with modern hooks
- **Features**:
  - Responsive note management interface
  - Real-time voice dictation with Web Speech API
  - Multi-language support (11 languages)
  - Live transcript display with editing capabilities
  - AI Q&A interface with conversation history
  - Clean, modern UI with animations

### Backend (FastAPI)
- **Technology**: FastAPI with Python 3.11
- **Features**:
  - RESTful API for note CRUD operations
  - RAG (Retrieval-Augmented Generation) implementation
  - Vector similarity search using pgvector
  - Conversation memory management with LangChain
  - Ollama integration for local LLM processing
  - Health checks and status endpoints

### Database (PostgreSQL + pgvector)
- **Technology**: PostgreSQL 16 with pgvector extension
- **Features**:
  - Vector embeddings storage (768-dimensional)
  - Cosine similarity search for note retrieval
  - Optimized indexes for fast vector operations
  - Persistent storage for notes and embeddings

### LLM Service (Ollama)
- **Technology**: Ollama with local models
- **Models**:
  - `phi3:mini` - For text generation and Q&A
  - `nomic-embed-text` - For generating embeddings
- **Features**:
  - Local processing (no external API calls)
  - Privacy-focused (data stays on your machine)
  - Fast inference with optimized models

## 🔧 How It Works

### 1. Note Creation and Storage
1. User creates a note via the web interface or voice dictation
2. Note is stored in PostgreSQL database
3. When user asks questions, note content is embedded using `nomic-embed-text`
4. Embeddings are stored in the `note_embeddings` table with vector similarity indexing

### 2. Voice Dictation Process
1. User clicks "Start Voice Input" and grants microphone permission
2. Web Speech API captures audio and converts to text in real-time
3. Live transcript is displayed and can be edited
4. Final transcript is used to create or update notes
5. Supports 11 languages with automatic language detection

### 3. AI Q&A with RAG
1. User asks a question about their notes
2. Question is embedded using the same embedding model
3. Vector similarity search finds the most relevant note snippets
4. Relevant context is passed to `phi3:mini` along with the question
5. LLM generates an answer based on the retrieved context
6. Conversation history is maintained using LangChain memory

### 4. Vector Search Process
```sql
SELECT n.id, n.title, n.content, n.created_at, n.updated_at,
       1 - (ne.embedding <=> '[query_embedding]'::vector) as similarity
FROM notes n
JOIN note_embeddings ne ON n.id = ne.note_id
ORDER BY ne.embedding <=> '[query_embedding]'::vector
LIMIT 3
```

## 🚀 Prerequisites

Before deploying, ensure you have:

- **Minikube** installed and running
- **Docker** installed
- **kubectl** configured for minikube
- **kubectx** (optional, for context switching)
- At least **4GB RAM** available for minikube
- **Internet connection** for downloading Docker images

## 📦 Local Deployment with Minikube

### 1. Start Minikube
```bash
# Start minikube with sufficient resources
minikube start --memory=4096 --cpus=2

# Verify minikube is running
minikube status
```

### 2. Set Kubernetes Context
```bash
# Switch to minikube context
kubectx minikube
# OR
kubectl config use-context minikube
```

### 3. Build and Load Docker Images
```bash
# Build backend image
docker build -f backend/Dockerfile.prod -t notes-app-backend:latest ./backend

# Build frontend image
docker build -f frontend/Dockerfile.k8s -t notes-app-frontend:latest ./frontend

# Load images into minikube
minikube image load notes-app-backend:latest
minikube image load notes-app-frontend:latest
```

### 4. Deploy the Application
```bash
# Deploy all services
kubectl apply -k k8s/

# Wait for all pods to be ready
kubectl get pods -w
```

### 5. Access the Application
```bash
# Get frontend URL
minikube service notes-app-frontend-service --url

# Get backend URL
minikube service notes-app-backend-service --url
```

The application will be available at:
- **Frontend**: `http://127.0.0.1:30090` (or similar localhost URL)
- **Backend API**: `http://127.0.0.1:30080` (or similar localhost URL)
- **API Documentation**: `http://127.0.0.1:30080/docs`

## 🛠️ Development Commands

The project includes a comprehensive Makefile with all necessary commands:

```bash
# View all available commands
make help

# Build and load images
make build-images

# Deploy to minikube
make k8s-minikube-deploy

# Check deployment status
make k8s-status

# View logs
make k8s-logs

# Clean up deployment
make k8s-delete
```

## 📊 Monitoring and Debugging

### Check Pod Status
```bash
kubectl get pods
kubectl get services
kubectl get pvc
```

### View Logs
```bash
# Backend logs
kubectl logs -l app=notes-app-backend

# Frontend logs
kubectl logs -l app=notes-app-frontend

# PostgreSQL logs
kubectl logs -l app=notes-app-postgres

# Ollama logs
kubectl logs -l app=notes-app-ollama
```

### Debug Issues
```bash
# Check pod details
kubectl describe pod <pod-name>

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/bash

# Port forward for direct access
kubectl port-forward svc/notes-app-backend-service 8000:8000
```

## 🔧 Configuration

### Environment Variables
The application uses Kubernetes ConfigMaps and Secrets for configuration:

- **Database**: PostgreSQL connection settings
- **Ollama**: Local LLM service configuration
- **API URLs**: Service discovery configuration

### Resource Limits
The deployment includes resource limits optimized for local development:
- **Backend**: 256Mi RAM, 200m CPU
- **Frontend**: 64Mi RAM, 50m CPU
- **PostgreSQL**: 256Mi RAM, 200m CPU
- **Ollama**: 1Gi RAM, 500m CPU

## 🌐 API Endpoints

### Notes Management
- `GET /api/notes` - List all notes
- `POST /api/notes` - Create a new note
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note

### AI Q&A
- `POST /api/ask` - Ask a question about notes
- `GET /api/llm/status` - Check LLM service status

### Conversation Management
- `GET /api/conversations/{user_id}` - Get conversation history
- `POST /api/conversations/{user_id}/clear` - Clear conversation history

## 🎯 Features

### Voice Dictation
- **Real-time transcription** with live preview
- **11 language support** including English, Spanish, French, German, etc.
- **Editable transcript** before saving
- **Visual recording indicators** with animations
- **Error handling** with user-friendly messages

### AI-Powered Q&A
- **Context-aware responses** based on your notes
- **Vector similarity search** for relevant information
- **Conversation memory** to maintain context
- **Source attribution** showing which notes were used
- **Local processing** for privacy and speed

### Note Management
- **CRUD operations** with intuitive interface
- **Real-time updates** across the application
- **Responsive design** for all screen sizes
- **Error handling** with clear feedback

## 🔒 Security & Privacy

- **Local LLM processing** - No data sent to external services
- **Vector embeddings** stored locally in PostgreSQL
- **No external API dependencies** for core functionality
- **HTTPS ready** for production deployments
- **Resource isolation** through Kubernetes namespaces

## 🚀 Production Considerations

For production deployment, consider:

1. **Resource scaling** - Adjust CPU/memory limits based on usage
2. **Persistent storage** - Use proper storage classes for data persistence
3. **Security** - Implement proper RBAC and network policies
4. **Monitoring** - Add Prometheus/Grafana for observability
5. **Backup** - Implement database backup strategies
6. **SSL/TLS** - Configure proper certificates for HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Database connection issues:**
```bash
kubectl logs -l app=notes-app-postgres
kubectl exec -it <postgres-pod> -- psql -U notes_user -d notes_app
```

**Ollama model issues:**
```bash
kubectl logs -l app=notes-app-ollama
kubectl exec -it <ollama-pod> -- ollama list
```

**Frontend not loading:**
```bash
kubectl logs -l app=notes-app-frontend
kubectl get ingress
```

For more help, check the logs and ensure all services are running properly.