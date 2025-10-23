#!/bin/bash

# ICABAR Framework Deployment Script
# This script handles deployment to different environments with comprehensive validation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPLOYMENT_DIR="${PROJECT_ROOT}/deployment"

# Default values
ENVIRONMENT=""
VERSION=""
DRY_RUN=false
SKIP_TESTS=false
ROLLBACK=false
CANARY_PERCENTAGE=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy ICABAR Framework to specified environment

OPTIONS:
    -e, --environment ENV    Target environment (development|staging|production)
    -v, --version VERSION    Version to deploy (required for staging/production)
    -d, --dry-run           Perform dry run without actual deployment
    -s, --skip-tests        Skip pre-deployment tests
    -r, --rollback          Rollback to previous version
    -c, --canary PERCENT    Canary deployment percentage (default: 10)
    -h, --help              Show this help message

EXAMPLES:
    $0 -e development
    $0 -e staging -v v1.2.3
    $0 -e production -v v1.2.3 -c 5
    $0 -e production --rollback

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -s|--skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            -r|--rollback)
                ROLLBACK=true
                shift
                ;;
            -c|--canary)
                CANARY_PERCENTAGE="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Validate arguments
validate_args() {
    if [[ -z "$ENVIRONMENT" ]]; then
        log_error "Environment is required"
        usage
        exit 1
    fi

    if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT"
        exit 1
    fi

    if [[ "$ENVIRONMENT" != "development" && -z "$VERSION" && "$ROLLBACK" == false ]]; then
        log_error "Version is required for staging and production deployments"
        exit 1
    fi

    if [[ "$CANARY_PERCENTAGE" -lt 1 || "$CANARY_PERCENTAGE" -gt 50 ]]; then
        log_error "Canary percentage must be between 1 and 50"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check required tools
    local required_tools=("kubectl" "docker" "helm")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is required but not installed"
            exit 1
        fi
    done

    # Check Kubernetes connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    # Check namespace exists
    local namespace="icabar-${ENVIRONMENT}"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        namespace="icabar-production"
    fi

    if ! kubectl get namespace "$namespace" &> /dev/null; then
        log_warning "Namespace $namespace does not exist, creating..."
        kubectl create namespace "$namespace"
    fi

    log_success "Prerequisites check passed"
}

# Run pre-deployment tests
run_pre_deployment_tests() {
    if [[ "$SKIP_TESTS" == true ]]; then
        log_warning "Skipping pre-deployment tests"
        return 0
    fi

    log_info "Running pre-deployment tests..."

    # Run unit tests
    log_info "Running unit tests..."
    if ! python -m unittest discover -s icabar_framework/tests -p "test_*.py"; then
        log_error "Unit tests failed"
        exit 1
    fi

    # Run performance benchmark
    if [[ "$ENVIRONMENT" != "development" ]]; then
        log_info "Running performance benchmark..."
        if ! python icabar_framework/scripts/performance_benchmark.py; then
            log_error "Performance benchmark failed"
            exit 1
        fi
    fi

    # Run research validation
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_info "Running research validation..."
        if ! python icabar_framework/scripts/research_validation.py; then
            log_error "Research validation failed"
            exit 1
        fi
    fi

    log_success "Pre-deployment tests passed"
}

# Build and push Docker image
build_and_push_image() {
    if [[ "$ENVIRONMENT" == "development" ]]; then
        log_info "Using development image..."
        return 0
    fi

    log_info "Building Docker image for version $VERSION..."

    local image_tag="icabar/framework:${VERSION}"
    local latest_tag="icabar/framework:${ENVIRONMENT}-latest"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would build and push $image_tag"
        return 0
    fi

    # Build image
    docker build -t "$image_tag" -t "$latest_tag" .

    # Push image
    docker push "$image_tag"
    docker push "$latest_tag"

    log_success "Docker image built and pushed: $image_tag"
}

# Deploy to environment
deploy_to_environment() {
    log_info "Deploying to $ENVIRONMENT environment..."

    local config_file="${DEPLOYMENT_DIR}/environments/${ENVIRONMENT}.yml"
    local namespace="icabar-${ENVIRONMENT}"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        namespace="icabar-production"
    fi

    if [[ ! -f "$config_file" ]]; then
        log_error "Configuration file not found: $config_file"
        exit 1
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would deploy to $ENVIRONMENT"
        kubectl apply --dry-run=client -f "$config_file"
        return 0
    fi

    # Apply configuration
    if [[ "$ENVIRONMENT" == "production" ]]; then
        deploy_production_canary
    else
        kubectl apply -f "$config_file"
    fi

    log_success "Deployment to $ENVIRONMENT completed"
}

# Deploy production with canary strategy
deploy_production_canary() {
    log_info "Starting canary deployment with ${CANARY_PERCENTAGE}% traffic..."

    local config_file="${DEPLOYMENT_DIR}/environments/production.yml"
    local namespace="icabar-production"

    # Create canary deployment
    local canary_config="/tmp/canary-deployment.yml"
    sed "s/icabar-production/icabar-production-canary/g" "$config_file" > "$canary_config"
    sed -i "s/replicas: 5/replicas: 1/g" "$canary_config"

    # Deploy canary
    kubectl apply -f "$canary_config"

    # Wait for canary to be ready
    kubectl rollout status deployment/icabar-production-canary -n "$namespace" --timeout=300s

    # Monitor canary for 5 minutes
    log_info "Monitoring canary deployment for 5 minutes..."
    sleep 300

    # Check canary health
    if check_canary_health; then
        log_success "Canary deployment healthy, proceeding with full rollout..."
        kubectl apply -f "$config_file"
        kubectl rollout status deployment/icabar-production -n "$namespace" --timeout=600s
        
        # Clean up canary
        kubectl delete -f "$canary_config" || true
    else
        log_error "Canary deployment failed health checks, rolling back..."
        kubectl delete -f "$canary_config" || true
        exit 1
    fi

    rm -f "$canary_config"
}

# Check canary deployment health
check_canary_health() {
    local namespace="icabar-production"
    local canary_pod=$(kubectl get pods -n "$namespace" -l app=icabar-production-canary -o jsonpath='{.items[0].metadata.name}')

    if [[ -z "$canary_pod" ]]; then
        log_error "No canary pod found"
        return 1
    fi

    # Check pod status
    local pod_status=$(kubectl get pod "$canary_pod" -n "$namespace" -o jsonpath='{.status.phase}')
    if [[ "$pod_status" != "Running" ]]; then
        log_error "Canary pod not running: $pod_status"
        return 1
    fi

    # Check health endpoint
    if ! kubectl exec "$canary_pod" -n "$namespace" -- curl -f http://localhost:8000/health; then
        log_error "Canary health check failed"
        return 1
    fi

    # Check performance metrics
    local avg_latency=$(kubectl exec "$canary_pod" -n "$namespace" -- curl -s http://localhost:8080/metrics | grep avg_latency | awk '{print $2}')
    if (( $(echo "$avg_latency > 47.0" | bc -l) )); then
        log_error "Canary performance degraded: ${avg_latency}ms > 47ms"
        return 1
    fi

    return 0
}

# Rollback deployment
rollback_deployment() {
    log_info "Rolling back $ENVIRONMENT deployment..."

    local namespace="icabar-${ENVIRONMENT}"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        namespace="icabar-production"
    fi

    local deployment_name="icabar-${ENVIRONMENT}"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        deployment_name="icabar-production"
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would rollback $deployment_name"
        return 0
    fi

    # Rollback to previous revision
    kubectl rollout undo deployment/"$deployment_name" -n "$namespace"
    kubectl rollout status deployment/"$deployment_name" -n "$namespace" --timeout=300s

    log_success "Rollback completed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    local namespace="icabar-${ENVIRONMENT}"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        namespace="icabar-production"
    fi

    local deployment_name="icabar-${ENVIRONMENT}"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        deployment_name="icabar-production"
    fi

    # Check deployment status
    if ! kubectl rollout status deployment/"$deployment_name" -n "$namespace" --timeout=300s; then
        log_error "Deployment verification failed"
        exit 1
    fi

    # Check pod health
    local pods=$(kubectl get pods -n "$namespace" -l app="$deployment_name" -o jsonpath='{.items[*].metadata.name}')
    for pod in $pods; do
        local pod_status=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.phase}')
        if [[ "$pod_status" != "Running" ]]; then
            log_error "Pod $pod not running: $pod_status"
            exit 1
        fi
    done

    # Run smoke tests
    if [[ "$ENVIRONMENT" != "development" ]]; then
        run_smoke_tests
    fi

    log_success "Deployment verification passed"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."

    local namespace="icabar-${ENVIRONMENT}"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        namespace="icabar-production"
    fi

    local service_name="icabar-${ENVIRONMENT}-service"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        service_name="icabar-production-service"
    fi

    # Get service endpoint
    local service_ip=$(kubectl get service "$service_name" -n "$namespace" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [[ -z "$service_ip" ]]; then
        service_ip=$(kubectl get service "$service_name" -n "$namespace" -o jsonpath='{.spec.clusterIP}')
    fi

    # Test health endpoint
    if ! curl -f "http://${service_ip}/health"; then
        log_error "Health endpoint test failed"
        exit 1
    fi

    # Test metrics endpoint
    if ! curl -f "http://${service_ip}:8080/metrics"; then
        log_error "Metrics endpoint test failed"
        exit 1
    fi

    log_success "Smoke tests passed"
}

# Main function
main() {
    log_info "Starting ICABAR Framework deployment..."

    parse_args "$@"
    validate_args
    check_prerequisites

    if [[ "$ROLLBACK" == true ]]; then
        rollback_deployment
        verify_deployment
    else
        run_pre_deployment_tests
        build_and_push_image
        deploy_to_environment
        verify_deployment
    fi

    log_success "Deployment completed successfully!"
}

# Run main function with all arguments
main "$@"
