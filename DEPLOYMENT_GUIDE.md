# ICABAR Framework: Complete Deployment Guide

**Version**: 1.0  
**Date**: October 2025  
**Author**: A Kasim

## Overview

This comprehensive deployment guide provides step-by-step instructions for deploying the ICABAR Framework using the integrated CI/CD pipeline with GitHub Actions. The deployment strategy supports multiple environments, automated testing, performance validation, and research claim verification.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [GitHub Actions Configuration](#github-actions-configuration)
4. [Environment Setup](#environment-setup)
5. [Deployment Process](#deployment-process)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Infrastructure Requirements

**Kubernetes Clusters**: Three separate Kubernetes clusters for development, staging, and production environments with appropriate resource allocation and security configurations.

**Container Registry**: GitHub Container Registry (ghcr.io) access with package write permissions for storing Docker images.

**Database Systems**: PostgreSQL instances for each environment with appropriate backup and replication configurations.

**Monitoring Infrastructure**: Prometheus and Grafana setup for comprehensive monitoring and alerting across all environments.

### Development Tools

**Required Software**:
- Docker Desktop or Docker Engine (v20.10+)
- kubectl (v1.25+)
- Python 3.8+ with pip
- Git (v2.30+)
- curl and jq for API testing

**Optional Tools**:
- Helm (v3.10+) for advanced Kubernetes deployments
- k9s for Kubernetes cluster management
- Postman or similar for API testing

### Access Requirements

**GitHub Repository**: Admin access to configure secrets, environments, and workflow permissions.

**Kubernetes Clusters**: Cluster admin access for initial setup and service account configuration.

**External Services**: Access to Slack workspace for notifications, Codecov for coverage reporting, and PyPI for package publishing.

## Initial Setup

### 1. Repository Configuration

Clone the ICABAR Framework repository and ensure all deployment files are properly configured:

```bash
git clone https://github.com/yourusername/icabar-framework.git
cd icabar-framework

# Verify deployment structure
ls -la deployment/
ls -la .github/workflows/
```

### 2. Docker Environment Setup

Build and test the Docker environment locally:

```bash
# Build the Docker image
docker build -t icabar/framework:dev .

# Start the development environment
docker-compose up -d

# Verify services are running
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8080/metrics
```

### 3. Kubernetes Cluster Preparation

Prepare each Kubernetes cluster with necessary namespaces and configurations:

```bash
# Create namespaces for each environment
kubectl create namespace icabar-development
kubectl create namespace icabar-staging  
kubectl create namespace icabar-production

# Apply RBAC configurations
kubectl apply -f deployment/kubernetes/rbac.yml

# Create persistent volumes
kubectl apply -f deployment/kubernetes/storage.yml
```

## GitHub Actions Configuration

### 1. Secrets Configuration

Configure all required secrets in your GitHub repository following the template in `deployment/github-actions/secrets-template.md`:

**Repository Secrets**:
- `GITHUB_TOKEN` (automatically provided)
- `SLACK_WEBHOOK` for deployment notifications
- `CODECOV_TOKEN` for coverage reporting

**Environment-Specific Secrets**:
- `KUBE_CONFIG_STAGING` and `KUBE_CONFIG_PRODUCTION`
- `DATABASE_PASSWORD_STAGING` and `DATABASE_PASSWORD_PRODUCTION`
- `SECRET_KEY_STAGING` and `SECRET_KEY_PRODUCTION`
- `JWT_SECRET_STAGING` and `JWT_SECRET_PRODUCTION`

### 2. Environment Configuration

Create GitHub environments with appropriate protection rules:

**Staging Environment**:
```yaml
name: staging
protection_rules: []
deployment_url: https://staging.icabar.example.com
```

**Production Environment**:
```yaml
name: production
protection_rules:
  - required_reviewers: 2
  - wait_timer: 5
  - restrict_pushes: true
deployment_url: https://api.icabar.example.com
```

### 3. Workflow Validation

Test the GitHub Actions workflow with a pull request:

```bash
# Create a feature branch
git checkout -b feature/test-deployment

# Make a small change
echo "# Test deployment" >> README.md
git add README.md
git commit -m "Test: Validate CI/CD pipeline"

# Push and create pull request
git push origin feature/test-deployment
```

## Environment Setup

### Development Environment

The development environment runs locally using Docker Compose and provides rapid iteration capabilities:

```bash
# Start development environment
docker-compose up -d

# Run tests locally
python -m unittest discover -s icabar_framework/tests

# Access services
# Application: http://localhost:8000
# Metrics: http://localhost:8080
# Grafana: http://localhost:3000 (admin/admin)
# Jupyter: http://localhost:8888 (token: icabar-dev-token)
```

### Staging Environment

Staging deployment occurs automatically when code is merged to the `develop` branch:

```bash
# Merge to develop branch triggers staging deployment
git checkout develop
git merge feature/your-feature
git push origin develop

# Monitor deployment
kubectl get pods -n icabar-staging -w
kubectl logs -f deployment/icabar-staging -n icabar-staging
```

### Production Environment

Production deployment requires manual approval and occurs when version tags are pushed:

```bash
# Create and push version tag
git checkout main
git tag v1.0.0
git push origin v1.0.0

# Monitor canary deployment
kubectl get pods -n icabar-production -l app=icabar-production-canary
kubectl logs -f deployment/icabar-production-canary -n icabar-production

# Monitor full deployment after canary success
kubectl rollout status deployment/icabar-production -n icabar-production
```

## Deployment Process

### Automated Deployment Flow

The CI/CD pipeline follows this automated flow:

1. **Code Quality Validation**: Linting, formatting, and type checking
2. **Comprehensive Testing**: Unit tests with coverage analysis across Python versions
3. **Performance Benchmarking**: Validation of 47ms average latency target
4. **Research Validation**: Verification of claimed performance improvements
5. **Security Scanning**: Vulnerability assessment and dependency analysis
6. **Docker Image Building**: Multi-platform image with SBOM generation
7. **Staging Deployment**: Automated deployment with smoke testing
8. **Production Deployment**: Canary strategy with manual approval
9. **Package Publishing**: PyPI release and GitHub release creation

### Manual Deployment Commands

For manual deployments or troubleshooting:

```bash
# Deploy to staging manually
./deployment/scripts/deploy.sh -e staging -v develop

# Deploy to production with canary
./deployment/scripts/deploy.sh -e production -v v1.0.0 -c 10

# Rollback production deployment
./deployment/scripts/deploy.sh -e production --rollback

# Dry run deployment
./deployment/scripts/deploy.sh -e production -v v1.0.0 --dry-run
```

### Deployment Validation

Each deployment includes comprehensive validation:

**Health Checks**:
```bash
# Application health
curl -f https://api.icabar.example.com/health

# Metrics endpoint
curl -f https://api.icabar.example.com:8080/metrics

# Research validation endpoint
curl -f https://api.icabar.example.com/research-metrics
```

**Performance Validation**:
```bash
# Load testing with expected performance
ab -n 1000 -c 10 https://api.icabar.example.com/recommend

# Latency measurement
curl -w "@curl-format.txt" -o /dev/null -s https://api.icabar.example.com/health
```

## Monitoring and Maintenance

### Comprehensive Monitoring

The deployment includes multi-layered monitoring:

**Application Metrics**:
- Request latency (target: <47ms)
- Error rates (target: <1%)
- Throughput (requests per minute)
- Resource utilization (CPU, memory)

**Research Validation Metrics**:
- Accuracy improvement (target: >33%)
- Diversity improvement (target: >65%)
- Novelty improvement (target: >45%)

**Infrastructure Metrics**:
- Kubernetes cluster health
- Database performance
- Cache hit rates
- Network latency

### Alerting Configuration

Alerts are configured for various scenarios:

**Critical Alerts** (immediate response):
- Service downtime
- Error rate >5%
- Latency >60ms
- Research metrics below thresholds

**Warning Alerts** (monitoring required):
- Error rate >1%
- Latency >47ms
- High resource utilization
- Performance degradation trends

### Maintenance Procedures

**Regular Maintenance**:
- Weekly dependency updates
- Monthly security patches
- Quarterly secret rotation
- Bi-annual disaster recovery testing

**Performance Optimization**:
- Continuous model retraining
- Cache optimization
- Database query optimization
- Resource allocation tuning

## Troubleshooting

### Common Deployment Issues

**Docker Build Failures**:
```bash
# Check Docker daemon
docker info

# Build with verbose output
docker build --no-cache --progress=plain -t icabar/framework:debug .

# Check resource usage
docker system df
docker system prune
```

**Kubernetes Deployment Issues**:
```bash
# Check cluster connectivity
kubectl cluster-info
kubectl get nodes

# Debug pod issues
kubectl describe pod <pod-name> -n icabar-production
kubectl logs <pod-name> -n icabar-production --previous

# Check resource constraints
kubectl top nodes
kubectl top pods -n icabar-production
```

**Performance Issues**:
```bash
# Check application metrics
curl -s http://localhost:8080/metrics | grep latency

# Database performance
kubectl exec -it postgres-pod -- psql -c "SELECT * FROM pg_stat_activity;"

# Cache performance
kubectl exec -it redis-pod -- redis-cli info stats
```

### Emergency Procedures

**Immediate Rollback**:
```bash
# Automated rollback via GitHub Actions
gh workflow run rollback-production.yml

# Manual rollback
kubectl rollout undo deployment/icabar-production -n icabar-production
```

**Service Recovery**:
```bash
# Scale up replicas
kubectl scale deployment icabar-production --replicas=10 -n icabar-production

# Restart problematic pods
kubectl delete pod -l app=icabar-production -n icabar-production

# Check service endpoints
kubectl get endpoints icabar-production-service -n icabar-production
```

### Debugging Commands

**Application Debugging**:
```bash
# Access application logs
kubectl logs -f deployment/icabar-production -n icabar-production

# Execute commands in pod
kubectl exec -it <pod-name> -n icabar-production -- /bin/bash

# Port forward for local debugging
kubectl port-forward service/icabar-production-service 8000:80 -n icabar-production
```

**Performance Debugging**:
```bash
# CPU and memory profiling
kubectl exec -it <pod-name> -n icabar-production -- python -m cProfile -o profile.stats /app/main.py

# Network debugging
kubectl exec -it <pod-name> -n icabar-production -- netstat -tulpn
kubectl exec -it <pod-name> -n icabar-production -- ss -tulpn
```

## Best Practices

### Security Best Practices

1. **Secret Management**: Use environment-specific secrets with regular rotation
2. **Network Security**: Implement network policies and service mesh
3. **Image Security**: Scan images for vulnerabilities and use minimal base images
4. **Access Control**: Implement RBAC and principle of least privilege

### Performance Best Practices

1. **Resource Optimization**: Right-size containers and use horizontal pod autoscaling
2. **Caching Strategy**: Implement multi-layer caching with appropriate TTLs
3. **Database Optimization**: Use connection pooling and query optimization
4. **Monitoring**: Implement comprehensive monitoring with proactive alerting

### Operational Best Practices

1. **Documentation**: Maintain up-to-date deployment and operational documentation
2. **Testing**: Implement comprehensive testing including load and chaos testing
3. **Backup Strategy**: Regular backups with tested recovery procedures
4. **Change Management**: Use structured change management with approval processes

## Conclusion

This deployment guide provides comprehensive instructions for deploying the ICABAR Framework using modern CI/CD practices. The integrated approach ensures that deployments maintain research validation standards while providing enterprise-grade reliability and performance.

The deployment strategy supports continuous integration and delivery while maintaining the framework's claimed performance improvements of 33% accuracy enhancement, 65% diversity improvement, and 45% novelty advancement over traditional collaborative filtering approaches.

For additional support or questions, refer to the project documentation or contact the development team through the established communication channels.
