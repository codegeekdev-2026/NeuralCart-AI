# Deployment Guide

Complete guide for deploying the E-commerce Personalization Platform.

## Local Development

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### Setup Steps

1. **Clone repository**
```bash
git clone <repo-url>
cd LLM-client
```

2. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Install dependencies**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Start services**
```bash
docker-compose up -d
```

5. **Run application**
```bash
uvicorn app.main:app --reload
```

6. **Access API**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

---

## Docker Deployment

### Build Image

```bash
docker build -t ecommerce-api:latest .
```

### Run Container

```bash
docker run -d \
  --name ecommerce-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e STRIPE_API_KEY=pk_... \
  ecommerce-api:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## AWS Deployment

### Prerequisites
- AWS account
- AWS CLI installed
- IAM user with appropriate permissions

### Option 1: AWS Lambda

1. **Prepare Lambda package**
```bash
./deploy_lambda.sh
```

2. **Create Lambda function**
```bash
aws lambda create-function \
  --function-name ecommerce-recommendations \
  --runtime python3.11 \
  --handler aws/lambda_handler.lambda_handler \
  --zip-file fileb://lambda_deployment.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role
```

3. **Configure API Gateway**
```bash
aws apigateway create-rest-api \
  --name ecommerce-api
```

### Option 2: ECS/Fargate

1. **Push image to ECR**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag ecommerce-api:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ecommerce-api:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ecommerce-api:latest
```

2. **Create ECS cluster**
```bash
aws ecs create-cluster --cluster-name ecommerce-cluster
```

3. **Register task definition**
```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json
```

4. **Create ECS service**
```bash
aws ecs create-service \
  --cluster ecommerce-cluster \
  --service-name ecommerce-api \
  --task-definition ecommerce-api:1 \
  --desired-count 2 \
  --launch-type FARGATE
```

### Option 3: Elastic Beanstalk

1. **Initialize Elastic Beanstalk**
```bash
eb init -p docker ecommerce-api --region us-east-1
```

2. **Create environment**
```bash
eb create ecommerce-env
```

3. **Deploy**
```bash
eb deploy
```

---

## Kubernetes Deployment

### Prerequisites
- kubectl configured
- Kubernetes cluster (EKS, GKE, AKS)

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecommerce-api
  template:
    metadata:
      labels:
        app: ecommerce-api
    spec:
      containers:
      - name: api
        image: your-registry/ecommerce-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ecommerce-api-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: ecommerce-api
```

### Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic api-secrets \
  --from-literal=openai-key=sk-...

# Create namespace
kubectl create namespace ecommerce

# Deploy
kubectl apply -f deployment.yaml -n ecommerce

# Check status
kubectl get deployments -n ecommerce
```

---

## Database Setup

### PostgreSQL

```bash
# Create database
createdb ecommerce

# Run migrations
alembic upgrade head
```

### Redis

```bash
# Start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

---

## CI/CD Pipeline

### GitHub Actions

The project includes automated CI/CD:

1. **Triggers**
   - Push to main/develop branches
   - Pull requests
   - Scheduled security scans

2. **Pipeline Steps**
   - Lint code
   - Run tests
   - Build Docker image
   - Push to registry
   - Deploy to AWS

### Manual Deployment

```bash
# Test
pytest tests/ -v

# Build
docker build -t ecommerce-api:latest .

# Push to registry
docker push your-registry/ecommerce-api:latest

# Deploy
./deploy_lambda.sh
# or
eb deploy
```

---

## Environment Variables

Required for production:

```env
# API
DEBUG=False
API_TITLE=AI E-commerce Personalization Platform

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Vector DB
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=...

# Stripe
STRIPE_API_KEY=pk_...
STRIPE_SECRET_KEY=sk_...

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET=ecommerce-personalization

# Database
DATABASE_URL=postgresql://user:pwd@host/db

# Redis
REDIS_URL=redis://host:6379

# Elasticsearch
ELASTICSEARCH_HOST=host:9200
```

---

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**
   - AWS ELB/ALB
   - NGINX
   - HAProxy

2. **Database Replication**
   - Read replicas
   - Write replicas (leader-follower)

3. **Cache Distribution**
   - Redis Cluster
   - Redis Sentinel

### Vertical Scaling

- Increase container resources
- Use larger database instances
- Optimize vector database indices

---

## Monitoring & Logging

### CloudWatch (AWS)

```bash
# View logs
aws logs tail /aws/lambda/ecommerce-api --follow

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name high-error-rate \
  --metric-name Errors \
  --threshold 10
```

### Application Metrics

- Request latency
- Error rate
- Recommendation accuracy
- Payment success rate

### Health Checks

```bash
# Check API health
curl http://api.example.com/health

# Check readiness
curl http://api.example.com/ready
```

---

## SSL/TLS Configuration

```bash
# AWS Certificate Manager
aws acm request-certificate \
  --domain-name api.ecommerce.com \
  --validation-method DNS
```

---

## Backup & Recovery

### Database Backups

```bash
# PostgreSQL
pg_dump ecommerce > backup.sql

# Restore
psql ecommerce < backup.sql
```

### S3 Backups

```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ecommerce-personalization \
  --versioning-configuration Status=Enabled
```

---

## Performance Tuning

1. **Database Indexes**
   - Create on frequently queried columns
   - FAISS index optimization

2. **Caching Strategy**
   - Cache frequently accessed products
   - Cache embeddings
   - Set appropriate TTLs

3. **Query Optimization**
   - Batch vector similarity searches
   - Use pagination
   - Limit result sets

---

## Security Hardening

- [ ] Enable HTTPS/TLS
- [ ] Set up WAF (Web Application Firewall)
- [ ] Implement API rate limiting
- [ ] Add authentication/authorization
- [ ] Encrypt sensitive data
- [ ] Enable audit logging
- [ ] Regular security scans

---

## Rollback Procedure

```bash
# Rollback Lambda function
aws lambda update-function-code \
  --function-name ecommerce-api \
  --s3-bucket deployment-bucket \
  --s3-key previous-version.zip

# Rollback ECS
aws ecs update-service \
  --cluster ecommerce-cluster \
  --service ecommerce-api \
  --task-definition ecommerce-api:2 \
  --force-new-deployment
```

---

## Troubleshooting

### Common Issues

1. **API not responding**
   - Check health endpoint
   - Review CloudWatch logs
   - Verify security group rules

2. **Database connection error**
   - Confirm DATABASE_URL
   - Check database credentials
   - Verify network connectivity

3. **Lambda timeout**
   - Increase timeout setting
   - Optimize function code
   - Check for blocking operations

4. **High latency**
   - Check database queries
   - Review vector search performance
   - Monitor resource utilization

---

## Support & Help

- **Documentation**: See [README.md](README.md)
- **API Reference**: See [API_REFERENCE.md](API_REFERENCE.md)
- **Architecture**: See [AGENT_ARCHITECTURE.md](AGENT_ARCHITECTURE.md)
- **Issues**: Create GitHub issue with error logs
