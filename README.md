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

### **🚀 One-Command Setup (Recommended)**
```bash
# Complete setup and deployment
make minikube-setup
```

This single command will:
1. ✅ Start minikube cluster (if not running)
2. ✅ Build all Docker images
3. ✅ Load images into minikube
4. ✅ Deploy all services to Kubernetes
5. ✅ Wait for deployments to be ready
6. ✅ Display access URLs

### **📋 Manual Step-by-Step (Alternative)**
If you prefer manual control:

```bash
# 1. Start minikube
make minikube-start

# 2. Build and load images
make build-images
make load-images

# 3. Deploy to Kubernetes
make k8s-deploy

# 4. Get access URLs
make minikube-access
```

### **🌐 Access the Application**
After deployment, the application will be available at:
- **Frontend**: `http://127.0.0.1:30090` (or similar localhost URL)
- **Backend API**: `http://127.0.0.1:30080` (or similar localhost URL)
- **API Documentation**: `http://127.0.0.1:30080/docs`

**Note**: On macOS with Docker driver, minikube provides localhost URLs instead of the minikube IP.

## 🔌 Service Ports and Endpoints

The application consists of multiple services, each running on specific ports. Here's a comprehensive overview:

### **📱 Application Services**

| Service | Port | Type | Purpose | Access URL |
|---------|------|------|---------|------------|
| **Frontend (React)** | 30090 | NodePort | Web application UI with voice dictation | `http://127.0.0.1:30090` |
| **Backend API (FastAPI)** | 30080 | NodePort | REST API for notes and AI Q&A | `http://127.0.0.1:30080` |
| **API Documentation** | 30080/docs | NodePort | Interactive API documentation | `http://127.0.0.1:30080/docs` |

### **🗄️ Database Services**

| Service | Port | Type | Purpose | Internal Access |
|---------|------|------|---------|-----------------|
| **PostgreSQL** | 5432 | ClusterIP | Main database with pgvector extension | `notes-app-postgres-service:5432` |
| **PostgreSQL Init Job** | - | Job | Database initialization and schema setup | One-time execution |

### **🤖 AI/LLM Services**

| Service | Port | Type | Purpose | Internal Access |
|---------|------|------|---------|-----------------|
| **Ollama Server** | 11434 | ClusterIP | Local LLM server for text generation | `notes-app-ollama-service:11434` |
| **Ollama Init Job** | - | Job | Model downloading (phi3:mini, nomic-embed-text) | One-time execution |

### **📊 Monitoring Services**

| Service | Port | Type | Purpose | Access URL |
|---------|------|------|---------|------------|
| **Grafana Dashboard** | 30300 | NodePort | Visual dashboards and metrics | `http://127.0.0.1:30300` |
| **Prometheus Metrics** | 30900 | NodePort | Raw metrics and queries | `http://127.0.0.1:30900` |
| **AlertManager** | 30903 | NodePort | Alert management and routing | `http://127.0.0.1:30903` |
| **k9s Terminal** | - | CLI | Real-time pod monitoring | `make k9s` |

### **🔧 Internal Service Communication**

| From Service | To Service | Port | Protocol | Purpose |
|--------------|------------|------|----------|---------|
| Frontend | Backend API | 8000 | HTTP | API requests for CRUD operations |
| Backend | PostgreSQL | 5432 | TCP | Database queries and transactions |
| Backend | Ollama | 11434 | HTTP | LLM inference and embeddings |
| Prometheus | All Services | Various | HTTP | Metrics collection |
| Grafana | Prometheus | 9090 | HTTP | Metrics visualization |

### **📋 Service Details**

#### **Frontend Service (React)**
- **Port**: 30090 (NodePort)
- **Internal Port**: 80 (Nginx)
- **Purpose**: Serves the React web application
- **Features**: 
  - Voice dictation with Web Speech API
  - Real-time note management
  - AI Q&A interface
  - Multi-language support
- **Dependencies**: Backend API service

#### **Backend Service (FastAPI)**
- **Port**: 30080 (NodePort)
- **Internal Port**: 8000 (FastAPI)
- **Purpose**: REST API for all application functionality
- **Endpoints**:
  - `GET /api/notes` - List all notes
  - `POST /api/notes` - Create new note
  - `PUT /api/notes/{id}` - Update note
  - `DELETE /api/notes/{id}` - Delete note
  - `POST /api/ask` - AI Q&A with RAG
  - `GET /api/llm/status` - LLM service health
  - `GET /api/conversations/{user_id}` - Conversation history
- **Dependencies**: PostgreSQL, Ollama services

#### **PostgreSQL Database**
- **Port**: 5432 (ClusterIP)
- **Purpose**: Data persistence with vector search capabilities
- **Features**:
  - Notes storage and retrieval
  - Vector embeddings for similarity search
  - Conversation history management
  - ACID compliance and data integrity
- **Extensions**: pgvector for vector operations

#### **Ollama LLM Service**
- **Port**: 11434 (ClusterIP)
- **Purpose**: Local AI model inference
- **Models**:
  - `phi3:mini` - Text generation and Q&A
  - `nomic-embed-text` - Text embeddings (768-dimensional)
- **Features**:
  - Privacy-focused (no external API calls)
  - Fast local inference
  - Multiple model support

#### **Grafana Dashboard**
- **Port**: 30300 (NodePort)
- **Purpose**: Visual monitoring and alerting
- **Features**:
  - Real-time dashboards
  - Custom metrics visualization
  - Alert management
  - Export and sharing capabilities
- **Credentials**: admin / admin123

#### **Prometheus Metrics**
- **Port**: 30900 (NodePort)
- **Purpose**: Metrics collection and storage
- **Features**:
  - Time-series data storage
  - PromQL query language
  - Service discovery
  - Alert rule management

#### **AlertManager**
- **Port**: 30903 (NodePort)
- **Purpose**: Alert routing and notifications
- **Features**:
  - Alert deduplication
  - Notification routing
  - Silence management
  - Integration with external systems

### **🔍 Port Usage Summary**

#### **External Access Ports (NodePort)**
- **30090**: Frontend web application
- **30080**: Backend API and documentation
- **30300**: Grafana monitoring dashboard
- **30900**: Prometheus metrics interface
- **30903**: AlertManager interface

#### **Internal Communication Ports (ClusterIP)**
- **5432**: PostgreSQL database
- **11434**: Ollama LLM service
- **8000**: Backend API (internal)
- **80**: Frontend Nginx (internal)
- **9090**: Prometheus (internal)
- **9093**: AlertManager (internal)

#### **Management Ports**
- **k9s**: Terminal-based pod monitoring (no port)
- **kubectl**: Kubernetes API access (443)
- **minikube**: Cluster management (various)

### **🌐 Network Architecture**

```
Internet/User
    ↓
[Minikube NodePort Services]
    ↓
[Kubernetes Cluster]
    ├── Frontend (React) → Backend API
    ├── Backend API → PostgreSQL
    ├── Backend API → Ollama
    ├── Prometheus → All Services
    └── Grafana → Prometheus
```

### **🔧 Port Configuration**

All ports are configured in the Kubernetes manifests:
- **NodePort services**: `k8s/*-service.yaml` files
- **ClusterIP services**: Internal service communication
- **Monitoring services**: `k8s/monitoring-services.yaml`

### **🚨 Security Considerations**

- **NodePort services** are exposed externally for development
- **ClusterIP services** are only accessible within the cluster
- **Database and LLM services** are not directly exposed
- **Monitoring services** have basic authentication
- **Production deployments** should use Ingress controllers

## 🛠️ Development Commands

The project includes a comprehensive Makefile with all necessary commands for easy local deployment:

### **🚀 Quick Start (Recommended)**
```bash
# Complete setup and deployment in one command
make minikube-setup

# Get access URLs after deployment
make minikube-access

# View application logs
make minikube-logs

# Clean up when done
make minikube-clean
```

### **📋 All Available Commands**
```bash
# View all available commands
make help

# Minikube Management
make minikube-start      # Start minikube cluster
make minikube-stop       # Stop minikube cluster
make minikube-status     # Check minikube and K8s status
make minikube-dashboard  # Open minikube dashboard

# Build & Deploy
make build-images        # Build all Docker images
make load-images         # Load images into minikube
make k8s-deploy          # Deploy to Kubernetes
make k8s-delete          # Delete from Kubernetes
make k8s-status          # Check deployment status

# Development
make test                # Run backend tests
make clean               # Clean up Docker resources
```

### **🔄 Typical Workflow**
```bash
# 1. Complete setup (first time only)
make minikube-setup

# 2. Install monitoring tools
make monitoring-setup

# 3. Get access URLs
make minikube-access
make monitoring-access

# 4. Monitor your application
make k9s              # Real-time pod monitoring
make grafana          # Open Grafana dashboard
make prometheus       # Open Prometheus metrics

# 5. Check status if needed
make minikube-status

# 6. View logs if debugging
make minikube-logs
make monitoring-logs

# 7. Clean up when done
make minikube-clean
make monitoring-clean
```

## 📊 Monitoring and Observability

The application includes comprehensive monitoring tools for real-time insights into your deployment:

### **🔧 Monitoring Tools Setup**
```bash
# Install monitoring stack (Prometheus + Grafana + k9s)
make monitoring-setup

# Get all monitoring access URLs
make monitoring-access
```

### **🌐 Monitoring Access URLs**

| Tool | URL | Credentials | Purpose |
|------|-----|-------------|---------|
| **Grafana Dashboard** | `http://127.0.0.1:30300` | admin / admin123 | Visual dashboards, metrics, alerts |
| **Prometheus Metrics** | `http://127.0.0.1:30900` | - | Raw metrics, queries, targets |
| **AlertManager** | `http://127.0.0.1:30903` | - | Alert management and routing |
| **k9s (Terminal)** | `make k9s` | - | Real-time pod monitoring |

### **📈 Real-Time Monitoring**

#### **k9s - Terminal-Based Pod Monitoring**
```bash
# Open k9s for real-time monitoring
make k9s

# Key k9s shortcuts:
# - 'd' - Describe selected pod
# - 'l' - View pod logs
# - 's' - Shell into pod
# - 'e' - Edit resource
# - '?' - Help
# - 'q' - Quit
```

#### **Grafana - Visual Dashboards**
```bash
# Open Grafana dashboard
make grafana

# Pre-configured dashboards:
# - Kubernetes Cluster Overview
# - Pod Metrics
# - Node Metrics
# - Application Metrics
# - Custom Notes App Dashboard
```

#### **Prometheus - Metrics and Queries**
```bash
# Open Prometheus interface
make prometheus

# Useful queries for Notes App:
# - up{job="notes-app-backend"} - Backend health
# - rate(http_requests_total[5m]) - Request rate
# - container_memory_usage_bytes{pod=~"notes-app-.*"} - Memory usage
# - container_cpu_usage_seconds_total{pod=~"notes-app-.*"} - CPU usage
```

### **📊 Application-Specific Monitoring**

#### **Notes App Metrics**
- **Request Rate**: API calls per second
- **Response Time**: Average response time
- **Error Rate**: Failed requests percentage
- **Memory Usage**: Per-service memory consumption
- **CPU Usage**: Per-service CPU utilization
- **Database Connections**: PostgreSQL connection pool
- **LLM Usage**: Ollama model inference metrics

#### **Custom Grafana Dashboards**
1. **Notes App Overview**: High-level application health
2. **Backend Performance**: API metrics, response times
3. **Frontend Metrics**: React app performance
4. **Database Health**: PostgreSQL metrics, connections
5. **LLM Monitoring**: Ollama usage, model performance
6. **Infrastructure**: Node resources, pod status

### **🚨 Alerting and Notifications**

#### **Pre-configured Alerts**
- **Pod Crash**: When any pod restarts unexpectedly
- **High Memory Usage**: When memory usage exceeds 80%
- **High CPU Usage**: When CPU usage exceeds 80%
- **Database Connection Issues**: When PostgreSQL is unreachable
- **LLM Service Down**: When Ollama service is unavailable
- **API Error Rate**: When error rate exceeds 5%

#### **Alert Channels**
- **Email**: Configure SMTP settings in AlertManager
- **Slack**: Webhook integration for team notifications
- **PagerDuty**: For critical production alerts

### **🔍 Debugging and Troubleshooting**

#### **Quick Health Checks**
```bash
# Check all pod status
make minikube-status

# View application logs
make minikube-logs

# View monitoring logs
make monitoring-logs

# Check specific service logs
kubectl logs -l app=notes-app-backend --tail=50
kubectl logs -l app=notes-app-frontend --tail=50
```

#### **Advanced Debugging**
```bash
# Describe problematic pods
kubectl describe pod <pod-name>

# Execute commands in pods
kubectl exec -it <pod-name> -- /bin/bash

# Port forward for direct access
kubectl port-forward svc/notes-app-backend-service 8000:8000
kubectl port-forward svc/notes-app-frontend-service 3000:80

# Check resource usage
kubectl top pods
kubectl top nodes
```

#### **Performance Analysis**
```bash
# Check resource limits and requests
kubectl describe deployment notes-app-backend
kubectl describe deployment notes-app-frontend

# Monitor resource usage over time
kubectl top pods --containers

# Check persistent volume usage
kubectl get pvc
kubectl describe pvc <pvc-name>
```

### **📈 Metrics and Insights**

#### **Key Performance Indicators (KPIs)**
- **Application Availability**: Uptime percentage
- **Response Time**: P50, P95, P99 latencies
- **Throughput**: Requests per second
- **Error Rate**: 4xx and 5xx error percentage
- **Resource Utilization**: CPU, memory, storage usage
- **Database Performance**: Query time, connection pool
- **LLM Performance**: Inference time, model accuracy

#### **Business Metrics**
- **Notes Created**: Total notes in the system
- **AI Queries**: Number of Q&A interactions
- **Voice Usage**: Voice dictation sessions
- **User Activity**: Active users and sessions
- **Feature Usage**: Most used features and endpoints

### **🛠️ Monitoring Commands Reference**

```bash
# Monitoring setup and access
make monitoring-setup      # Install monitoring stack
make monitoring-access     # Get all access URLs
make monitoring-logs       # View monitoring tool logs
make monitoring-clean      # Clean up monitoring tools

# Real-time monitoring
make k9s                   # Open k9s terminal interface
make grafana              # Open Grafana dashboard
make prometheus           # Open Prometheus metrics

# Application monitoring
make minikube-status      # Check pod and service status
make minikube-logs        # View application logs
make minikube-access      # Get application URLs
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