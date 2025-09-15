.PHONY: help build up down logs test clean k8s-build k8s-deploy k8s-delete k8s-status

# Default target
help:
	@echo "Notes App - Available Commands:"
	@echo ""
	@echo "Local Development:"
	@echo "  make up        - Start the application locally"
	@echo "  make up-d      - Start in background"
	@echo "  make down      - Stop the application"
	@echo "  make logs      - View application logs"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Clean up containers and images"
	@echo "  make init-models - Initialize Ollama models"
	@echo "  make dev-setup - Complete development setup"
	@echo ""
	@echo "Kubernetes Production:"
	@echo "  make k8s-build  - Build production Docker images"
	@echo "  make k8s-deploy - Deploy to Kubernetes"
	@echo "  make k8s-delete - Delete from Kubernetes"
	@echo "  make k8s-status - Check Kubernetes deployment status"
	@echo "  make k8s-minikube-deploy - Deploy to minikube with unique ports"
	@echo ""

# Local Development Commands
up:
	docker-compose up --build

up-d:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v
	docker system prune -f

init-models:
	@echo "Initializing Ollama models..."
	./scripts/init-models.sh

dev-setup: up-d init-models
	@echo "Development environment ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "Ollama: http://localhost:11434"

# Kubernetes Production Commands
k8s-build:
	@echo "Building production Docker images..."
	docker build -f backend/Dockerfile.prod -t notes-app-backend:latest ./backend
	docker build -f frontend/Dockerfile.k8s -t notes-app-frontend:latest ./frontend
	@echo "Images built: notes-app-backend:latest, notes-app-frontend:latest"

k8s-deploy:
	@echo "Deploying to Kubernetes..."
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secret.yaml
	kubectl apply -f k8s/pvc.yaml
	kubectl apply -f k8s/postgres-pvc.yaml
	kubectl apply -f k8s/postgres-deployment.yaml
	kubectl apply -f k8s/postgres-service.yaml
	kubectl apply -f k8s/postgres-init-job.yaml
	kubectl apply -f k8s/ollama-pvc.yaml
	kubectl apply -f k8s/ollama-deployment.yaml
	kubectl apply -f k8s/ollama-service.yaml
	kubectl apply -f k8s/ollama-init-job.yaml
	kubectl apply -f k8s/backend-deployment.yaml
	kubectl apply -f k8s/frontend-deployment.yaml
	kubectl apply -f k8s/backend-service.yaml
	kubectl apply -f k8s/frontend-service.yaml
	kubectl apply -f k8s/ingress.yaml
	kubectl apply -f k8s/hpa.yaml
	@echo "Deployment completed!"

k8s-delete:
	@echo "Deleting from Kubernetes..."
	kubectl delete -f k8s/hpa.yaml --ignore-not-found=true
	kubectl delete -f k8s/ingress.yaml --ignore-not-found=true
	kubectl delete -f k8s/frontend-service.yaml --ignore-not-found=true
	kubectl delete -f k8s/backend-service.yaml --ignore-not-found=true
	kubectl delete -f k8s/frontend-deployment.yaml --ignore-not-found=true
	kubectl delete -f k8s/backend-deployment.yaml --ignore-not-found=true
	kubectl delete -f k8s/ollama-service.yaml --ignore-not-found=true
	kubectl delete -f k8s/ollama-deployment.yaml --ignore-not-found=true
	kubectl delete -f k8s/ollama-init-job.yaml --ignore-not-found=true
	kubectl delete -f k8s/postgres-service.yaml --ignore-not-found=true
	kubectl delete -f k8s/postgres-deployment.yaml --ignore-not-found=true
	kubectl delete -f k8s/postgres-init-job.yaml --ignore-not-found=true
	kubectl delete -f k8s/pvc.yaml --ignore-not-found=true
	kubectl delete -f k8s/postgres-pvc.yaml --ignore-not-found=true
	kubectl delete -f k8s/ollama-pvc.yaml --ignore-not-found=true
	kubectl delete -f k8s/secret.yaml --ignore-not-found=true
	kubectl delete -f k8s/configmap.yaml --ignore-not-found=true
	kubectl delete -f k8s/namespace.yaml --ignore-not-found=true
	@echo "Cleanup completed!"

k8s-status:
	@echo "Kubernetes deployment status:"
	@echo "Pods:"
	@kubectl get pods
	@echo ""
	@echo "Services:"
	@kubectl get services
	@echo ""
	@echo "Ingress:"
	@kubectl get ingress

k8s-minikube-deploy:
	@echo "Deploying to minikube with unique ports..."
	@echo "Building production images..."
	docker build -f backend/Dockerfile.prod -t notes-app-backend:latest ./backend
	docker build -f frontend/Dockerfile.k8s -t notes-app-frontend:latest ./frontend
	@echo "Loading images into minikube..."
	minikube image load notes-app-backend:latest
	minikube image load notes-app-frontend:latest
	@echo "Deploying to Kubernetes..."
	kubectl apply -k k8s/
	@echo "Waiting for deployment to be ready..."
	kubectl wait --for=condition=available --timeout=300s deployment/notes-app-backend
	kubectl wait --for=condition=available --timeout=300s deployment/notes-app-frontend
	@echo "Getting minikube IP..."
	@MINIKUBE_IP=$$(minikube ip); \
	echo "✅ Deployment complete!"; \
	echo ""; \
	echo "Access URLs:"; \
	echo "  Frontend: http://$$MINIKUBE_IP:30090"; \
	echo "  Backend API: http://$$MINIKUBE_IP:30080"; \
	echo "  API Docs: http://$$MINIKUBE_IP:30080/docs"; \
	echo ""; \
	echo "Or use ingress (if nginx-ingress is enabled):"; \
	echo "  Frontend: http://$$MINIKUBE_IP"; \
	echo "  Backend API: http://$$MINIKUBE_IP/api"; \
	echo ""; \
	echo "To check status: make k8s-status"; \
	echo "To view logs: kubectl logs -f deployment/notes-app-backend"
