.PHONY: help build up down logs test clean k8s-build k8s-deploy k8s-delete k8s-status minikube-setup minikube-deploy minikube-access minikube-logs minikube-clean

# Default target
help:
	@echo "Notes App - Available Commands:"
	@echo ""
	@echo "Quick Start (Minikube):"
	@echo "  make minikube-setup   - Complete minikube setup and deployment"
	@echo "  make minikube-deploy  - Deploy to minikube (assumes setup done)"
	@echo "  make minikube-access  - Get access URLs for the application"
	@echo "  make minikube-logs    - View application logs"
	@echo "  make minikube-clean   - Clean up minikube deployment"
	@echo ""
	@echo "Minikube Management:"
	@echo "  make minikube-start   - Start minikube cluster"
	@echo "  make minikube-stop    - Stop minikube cluster"
	@echo "  make minikube-status  - Check minikube status"
	@echo "  make minikube-dashboard - Open minikube dashboard"
	@echo ""
	@echo "Docker Development:"
	@echo "  make up        - Start the application locally with docker-compose"
	@echo "  make up-d      - Start in background"
	@echo "  make down      - Stop the application"
	@echo "  make logs      - View application logs"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Clean up containers and images"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  make build-images     - Build all Docker images"
	@echo "  make load-images      - Load images into minikube"
	@echo "  make k8s-deploy       - Deploy to Kubernetes"
	@echo "  make k8s-delete       - Delete from Kubernetes"
	@echo "  make k8s-status       - Check Kubernetes deployment status"
	@echo ""
	@echo "Monitoring & Observability:"
	@echo "  make monitoring-setup - Install Prometheus, Grafana, and monitoring tools"
	@echo "  make monitoring-access - Get monitoring tool access URLs"
	@echo "  make grafana          - Open Grafana dashboard"
	@echo "  make prometheus       - Open Prometheus metrics"
	@echo "  make monitoring-logs  - View monitoring tool logs"
	@echo "  make monitoring-clean - Clean up monitoring tools"
	@echo ""

# Minikube Quick Start Commands
minikube-setup: minikube-start build-images load-images k8s-deploy minikube-access
	@echo "🎉 Complete minikube setup finished!"
	@echo "Your Notes App is now running on minikube."

minikube-deploy: build-images load-images k8s-deploy
	@echo "✅ Deployed to minikube successfully!"

minikube-access:
	@echo "🌐 Getting access URLs..."
	@echo ""
	@echo "Frontend URL:"
	@minikube service notes-app-frontend-service --url
	@echo ""
	@echo "Backend API URL:"
	@minikube service notes-app-backend-service --url
	@echo ""
	@echo "💡 Note: On macOS with Docker driver, use the localhost URLs above."

minikube-logs:
	@echo "📋 Application Logs:"
	@echo ""
	@echo "=== Backend Logs ==="
	@kubectl logs -l app=notes-app-backend --tail=20
	@echo ""
	@echo "=== Frontend Logs ==="
	@kubectl logs -l app=notes-app-frontend --tail=20
	@echo ""
	@echo "=== PostgreSQL Logs ==="
	@kubectl logs -l app=notes-app-postgres --tail=10
	@echo ""
	@echo "=== Ollama Logs ==="
	@kubectl logs -l app=notes-app-ollama --tail=10

minikube-clean: k8s-delete
	@echo "🧹 Minikube cleanup completed!"

# Minikube Management Commands
minikube-start:
	@echo "🚀 Starting minikube cluster..."
	@if ! minikube status >/dev/null 2>&1; then \
		minikube start --memory=4096 --cpus=2; \
	else \
		echo "Minikube is already running."; \
	fi
	@echo "✅ Minikube is ready!"

minikube-stop:
	@echo "🛑 Stopping minikube cluster..."
	minikube stop
	@echo "✅ Minikube stopped!"

minikube-status:
	@echo "📊 Minikube Status:"
	minikube status
	@echo ""
	@echo "📊 Kubernetes Status:"
	kubectl get nodes
	@echo ""
	@echo "📊 Pod Status:"
	kubectl get pods

minikube-dashboard:
	@echo "🌐 Opening minikube dashboard..."
	minikube dashboard

# Build Commands
build-images:
	@echo "🔨 Building Docker images..."
	docker build -f backend/Dockerfile.prod -t notes-app-backend:latest ./backend
	docker build -f frontend/Dockerfile.k8s -t notes-app-frontend:latest ./frontend
	@echo "✅ Images built successfully!"

load-images:
	@echo "📦 Loading images into minikube..."
	minikube image load notes-app-backend:latest
	minikube image load notes-app-frontend:latest
	@echo "✅ Images loaded into minikube!"

# Local Development Commands (Docker Compose)
up:
	@echo "⚠️  Note: Docker Compose files were removed. Use 'make minikube-setup' for local development."

up-d:
	@echo "⚠️  Note: Docker Compose files were removed. Use 'make minikube-setup' for local development."

down:
	@echo "⚠️  Note: Docker Compose files were removed. Use 'make minikube-clean' to stop the application."

logs:
	@echo "📋 Use 'make minikube-logs' to view application logs."

test:
	@echo "🧪 Running tests..."
	cd backend && python -m pytest

clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker system prune -f
	@echo "✅ Cleanup completed!"

# Kubernetes Production Commands
k8s-build:
	@echo "Building production Docker images..."
	docker build -f backend/Dockerfile.prod -t notes-app-backend:latest ./backend
	docker build -f frontend/Dockerfile.k8s -t notes-app-frontend:latest ./frontend
	@echo "Images built: notes-app-backend:latest, notes-app-frontend:latest"

k8s-deploy:
	@echo "🚀 Deploying to Kubernetes..."
	kubectl apply -k k8s/
	@echo "⏳ Waiting for deployments to be ready..."
	kubectl wait --for=condition=available --timeout=300s deployment/notes-app-backend || true
	kubectl wait --for=condition=available --timeout=300s deployment/notes-app-frontend || true
	kubectl wait --for=condition=available --timeout=300s deployment/notes-app-postgres || true
	kubectl wait --for=condition=available --timeout=300s deployment/notes-app-ollama || true
	@echo "✅ Deployment completed!"

k8s-delete:
	@echo "🗑️  Deleting from Kubernetes..."
	kubectl delete -k k8s/ --ignore-not-found=true
	@echo "✅ Cleanup completed!"

k8s-status:
	@echo "📊 Kubernetes deployment status:"
	@echo ""
	@echo "=== Pods ==="
	@kubectl get pods
	@echo ""
	@echo "=== Services ==="
	@kubectl get services
	@echo ""
	@echo "=== PVCs ==="
	@kubectl get pvc
	@echo ""
	@echo "=== Jobs ==="
	@kubectl get jobs
	@echo ""
	@echo "=== Ingress ==="
	@kubectl get ingress 2>/dev/null || echo "No ingress found"

# Monitoring & Observability Commands
monitoring-setup:
	@echo "🔧 Setting up monitoring stack..."
	@echo "Installing Prometheus and Grafana..."
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
	helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
		--namespace monitoring \
		--set grafana.adminPassword=admin123 \
		--set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
		--set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
		--set prometheus.prometheusSpec.ruleSelectorNilUsesHelmValues=false
	@echo "Creating NodePort services for easy access..."
	kubectl apply -f k8s/monitoring-services.yaml
	@echo "⏳ Waiting for monitoring stack to be ready..."
	kubectl wait --for=condition=available --timeout=300s deployment/prometheus-grafana -n monitoring || true
	@echo "✅ Monitoring stack installed!"
	@echo "Use 'make monitoring-access' to get access URLs"

monitoring-access:
	@echo "🌐 Monitoring Tool Access URLs:"
	@echo ""
	@echo "=== Grafana Dashboard ==="
	@echo "URL: http://127.0.0.1:30300"
	@echo "Username: admin"
	@echo "Password: admin123"
	@echo ""
	@echo "=== Prometheus Metrics ==="
	@echo "URL: http://127.0.0.1:30900"
	@echo ""
	@echo "=== AlertManager ==="
	@echo "URL: http://127.0.0.1:30903"
	@echo ""
	@echo "💡 Note: On macOS with Docker driver, use the localhost URLs above."


grafana:
	@echo "🌐 Opening Grafana dashboard..."
	@echo "URL: http://127.0.0.1:30300"
	@echo "Username: admin"
	@echo "Password: admin123"
	@echo ""
	@echo "Opening in browser..."
	open http://127.0.0.1:30300 || echo "Please open http://127.0.0.1:30300 in your browser"

prometheus:
	@echo "📊 Opening Prometheus metrics..."
	@echo "URL: http://127.0.0.1:30900"
	@echo ""
	@echo "Opening in browser..."
	open http://127.0.0.1:30900 || echo "Please open http://127.0.0.1:30900 in your browser"

monitoring-logs:
	@echo "📋 Monitoring Stack Logs:"
	@echo ""
	@echo "=== Grafana Logs ==="
	@kubectl logs -l app.kubernetes.io/name=grafana -n monitoring --tail=10
	@echo ""
	@echo "=== Prometheus Logs ==="
	@kubectl logs -l app.kubernetes.io/name=prometheus -n monitoring --tail=10
	@echo ""
	@echo "=== AlertManager Logs ==="
	@kubectl logs -l app.kubernetes.io/name=alertmanager -n monitoring --tail=10

monitoring-clean:
	@echo "🧹 Cleaning up monitoring stack..."
	helm uninstall prometheus -n monitoring || true
	kubectl delete namespace monitoring --ignore-not-found=true
	kubectl delete -f k8s/monitoring-services.yaml --ignore-not-found=true
	@echo "✅ Monitoring cleanup completed!"
