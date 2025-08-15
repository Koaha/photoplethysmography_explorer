#!/bin/bash

# Deployment script for PPG Analysis Tool
# Supports Docker, Render.com, and Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_status "Docker is available"
}

# Build Docker image
build_docker() {
    print_status "Building Docker image..."
    docker build -f Dockerfile.prod -t ppg-tool:latest .
    print_status "Docker image built successfully"
}

# Run locally with Docker
run_local() {
    print_status "Running application locally with Docker..."
    docker run -d --name ppg-tool -p 8080:8080 ppg-tool:latest
    print_status "Application is running at http://localhost:8080"
}

# Deploy to Render.com
deploy_render() {
    print_status "Deploying to Render.com..."
    if ! command -v render &> /dev/null; then
        print_warning "Render CLI not found. Please install it first:"
        echo "curl -sSL https://render.com/download-cli/install.sh | bash"
        exit 1
    fi
    
    render blueprint apply
    print_status "Deployment to Render.com initiated"
}

# Deploy to Google Cloud Platform
deploy_gcp() {
    print_status "Deploying to Google Cloud Platform..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud SDK not found. Please install it first."
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with Google Cloud. Please run 'gcloud auth login' first."
        exit 1
    fi
    
    # Get project ID
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        print_error "No project ID set. Please run 'gcloud config set project PROJECT_ID' first."
        exit 1
    fi
    
    print_status "Using project: $PROJECT_ID"
    
    # Build and deploy
    gcloud builds submit --config cloudbuild.yaml .
    print_status "Deployment to GCP completed"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  build       Build Docker image"
    echo "  local       Run locally with Docker"
    echo "  render      Deploy to Render.com"
    echo "  gcp         Deploy to Google Cloud Platform"
    echo "  all         Build and run locally"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build    # Build Docker image"
    echo "  $0 local    # Run locally"
    echo "  $0 render   # Deploy to Render.com"
    echo "  $0 gcp      # Deploy to GCP"
}

# Main script
main() {
    case "${1:-help}" in
        build)
            check_docker
            build_docker
            ;;
        local)
            check_docker
            build_docker
            run_local
            ;;
        render)
            deploy_render
            ;;
        gcp)
            deploy_gcp
            ;;
        all)
            check_docker
            build_docker
            run_local
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
