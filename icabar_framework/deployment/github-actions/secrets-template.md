# GitHub Actions Secrets and Variables Configuration

This document outlines the required secrets and variables that need to be configured in your GitHub repository for the ICABAR Framework CI/CD pipeline to function properly.

## Repository Secrets

Configure these secrets in your GitHub repository settings under **Settings > Secrets and variables > Actions**.

### Container Registry Secrets

```
GITHUB_TOKEN
```
- **Description**: GitHub token for container registry access
- **Value**: Automatically provided by GitHub Actions
- **Scope**: Repository

### Kubernetes Configuration Secrets

```
KUBE_CONFIG_STAGING
```
- **Description**: Base64-encoded kubeconfig file for staging cluster
- **Value**: `cat ~/.kube/config-staging | base64 -w 0`
- **Scope**: Environment (staging)

```
KUBE_CONFIG_PRODUCTION
```
- **Description**: Base64-encoded kubeconfig file for production cluster
- **Value**: `cat ~/.kube/config-production | base64 -w 0`
- **Scope**: Environment (production)

### Database Secrets

```
DATABASE_PASSWORD_STAGING
```
- **Description**: PostgreSQL password for staging environment
- **Value**: Strong password for staging database
- **Scope**: Environment (staging)

```
DATABASE_PASSWORD_PRODUCTION
```
- **Description**: PostgreSQL password for production environment
- **Value**: Strong password for production database
- **Scope**: Environment (production)

### Application Secrets

```
SECRET_KEY_STAGING
```
- **Description**: Application secret key for staging
- **Value**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Scope**: Environment (staging)

```
SECRET_KEY_PRODUCTION
```
- **Description**: Application secret key for production
- **Value**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Scope**: Environment (production)

```
JWT_SECRET_STAGING
```
- **Description**: JWT signing secret for staging
- **Value**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Scope**: Environment (staging)

```
JWT_SECRET_PRODUCTION
```
- **Description**: JWT signing secret for production
- **Value**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Scope**: Environment (production)

### Monitoring and Alerting Secrets

```
SLACK_WEBHOOK
```
- **Description**: Slack webhook URL for deployment notifications
- **Value**: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
- **Scope**: Repository

```
MONITORING_TOKEN_PRODUCTION
```
- **Description**: Token for production monitoring access
- **Value**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Scope**: Environment (production)

### External Service Secrets

```
CODECOV_TOKEN
```
- **Description**: Codecov token for coverage reporting
- **Value**: Token from Codecov dashboard
- **Scope**: Repository

## Repository Variables

Configure these variables in your GitHub repository settings under **Settings > Secrets and variables > Actions**.

### Build Configuration Variables

```
DOCKER_REGISTRY
```
- **Description**: Docker registry URL
- **Value**: `ghcr.io`
- **Scope**: Repository

```
IMAGE_NAME
```
- **Description**: Docker image name
- **Value**: `icabar/framework`
- **Scope**: Repository

### Performance Configuration Variables

```
PERFORMANCE_TARGET_MS
```
- **Description**: Performance target in milliseconds
- **Value**: `47.0`
- **Scope**: Repository

```
COVERAGE_THRESHOLD
```
- **Description**: Minimum code coverage percentage
- **Value**: `90`
- **Scope**: Repository

### Research Validation Variables

```
ACCURACY_IMPROVEMENT_TARGET
```
- **Description**: Target accuracy improvement percentage
- **Value**: `33.0`
- **Scope**: Repository

```
DIVERSITY_IMPROVEMENT_TARGET
```
- **Description**: Target diversity improvement percentage
- **Value**: `65.0`
- **Scope**: Repository

```
NOVELTY_IMPROVEMENT_TARGET
```
- **Description**: Target novelty improvement percentage
- **Value**: `45.0`
- **Scope**: Repository

## Environment Configuration

### Staging Environment

Create a staging environment in your repository with the following settings:

- **Environment name**: `staging`
- **Protection rules**: None (automatic deployment)
- **Environment secrets**: All staging-specific secrets listed above
- **Deployment URL**: `https://staging.icabar.example.com`

### Production Environment

Create a production environment in your repository with the following settings:

- **Environment name**: `production`
- **Protection rules**: 
  - Required reviewers: 2
  - Wait timer: 5 minutes
  - Restrict to protected branches: `main` and tags matching `v*.*.*`
- **Environment secrets**: All production-specific secrets listed above
- **Deployment URL**: `https://api.icabar.example.com`

### Production Rollback Environment

Create a production rollback environment for emergency rollbacks:

- **Environment name**: `production-rollback`
- **Protection rules**:
  - Required reviewers: 1 (senior engineer)
  - Restrict to manual workflow dispatch
- **Environment secrets**: Same as production
- **Deployment URL**: `https://api.icabar.example.com`

### PyPI Environment

Create a PyPI environment for package publishing:

- **Environment name**: `pypi`
- **Protection rules**:
  - Required reviewers: 1
  - Restrict to tags matching `v*.*.*`
- **Deployment URL**: `https://pypi.org/p/icabar-framework`

## Security Best Practices

### Secret Management

1. **Rotation**: Rotate all secrets regularly (quarterly for production)
2. **Scope**: Use environment-specific secrets where possible
3. **Access**: Limit secret access to necessary environments only
4. **Audit**: Regularly audit secret usage and access logs

### Kubernetes Security

1. **RBAC**: Use role-based access control for Kubernetes clusters
2. **Namespaces**: Isolate environments using separate namespaces
3. **Network Policies**: Implement network policies for pod communication
4. **Service Accounts**: Use dedicated service accounts for deployments

### Container Security

1. **Image Scanning**: Enable container image vulnerability scanning
2. **SBOM**: Generate and store Software Bill of Materials
3. **Signatures**: Sign container images for integrity verification
4. **Base Images**: Use minimal, regularly updated base images

## Validation Commands

Use these commands to validate your secret configuration:

### Test Kubernetes Connectivity

```bash
# Decode and test staging kubeconfig
echo "$KUBE_CONFIG_STAGING" | base64 -d > /tmp/kubeconfig-staging
KUBECONFIG=/tmp/kubeconfig-staging kubectl cluster-info

# Decode and test production kubeconfig
echo "$KUBE_CONFIG_PRODUCTION" | base64 -d > /tmp/kubeconfig-production
KUBECONFIG=/tmp/kubeconfig-production kubectl cluster-info
```

### Test Database Connectivity

```bash
# Test staging database
PGPASSWORD="$DATABASE_PASSWORD_STAGING" psql -h staging-db.example.com -U icabar -d icabar_staging -c "SELECT 1;"

# Test production database
PGPASSWORD="$DATABASE_PASSWORD_PRODUCTION" psql -h production-db.example.com -U icabar -d icabar_production -c "SELECT 1;"
```

### Test Slack Webhook

```bash
# Test Slack notification
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test notification from ICABAR CI/CD pipeline"}' \
  "$SLACK_WEBHOOK"
```

## Troubleshooting

### Common Issues

1. **Invalid kubeconfig**: Ensure kubeconfig is properly base64 encoded without line breaks
2. **Database connection**: Verify database hostname, port, and credentials
3. **Slack notifications**: Check webhook URL format and channel permissions
4. **Container registry**: Ensure GITHUB_TOKEN has package write permissions

### Debug Commands

```bash
# Check secret availability in workflow
echo "Checking secrets..."
echo "KUBE_CONFIG_STAGING length: ${#KUBE_CONFIG_STAGING}"
echo "DATABASE_PASSWORD_STAGING length: ${#DATABASE_PASSWORD_STAGING}"

# Validate base64 encoding
echo "$KUBE_CONFIG_STAGING" | base64 -d | head -5

# Test container registry access
docker login ghcr.io -u ${{ github.actor }} -p ${{ secrets.GITHUB_TOKEN }}
```

This configuration ensures that your ICABAR Framework CI/CD pipeline has all necessary credentials and configuration to deploy successfully across all environments while maintaining security best practices.
