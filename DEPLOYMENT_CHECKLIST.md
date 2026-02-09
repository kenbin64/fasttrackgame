# ButterflyFx Deployment Checklist

**Complete checklist for deploying ButterflyFx to production VPS**

---

## Pre-Deployment (Local)

### 1. Code Preparation

- [x] All tests passing locally
  ```bash
  pytest tests/test_server.py -v
  pytest tests/test_substrate_stress.py -v
  ```

- [x] Docker build successful
  ```bash
  docker-compose build
  docker-compose up -d
  curl http://localhost:8000/api/v1/health
  docker-compose down
  ```

- [x] Documentation complete
  - [x] README.md updated
  - [x] DOCKER_DEPLOYMENT.md created
  - [x] API documentation in server/README.md

### 2. GitHub Preparation

- [ ] Push code to GitHub
  ```bash
  git add .
  git commit -m "Add Docker deployment configuration"
  git push origin main
  ```

- [ ] Verify GitHub Actions CI/CD
  - [ ] Check workflow runs successfully
  - [ ] All tests pass in CI
  - [ ] Docker image builds successfully

- [ ] (Optional) Set up Docker Hub
  - [ ] Create Docker Hub account
  - [ ] Add DOCKER_USERNAME secret to GitHub
  - [ ] Add DOCKER_PASSWORD secret to GitHub
  - [ ] Verify image pushes to Docker Hub

---

## VPS Setup

### 3. Server Preparation

- [ ] VPS provisioned
  - [ ] Ubuntu 22.04+ installed
  - [ ] 8GB+ RAM (16GB recommended)
  - [ ] 4+ CPU cores
  - [ ] 50GB+ storage

- [ ] SSH access configured
  ```bash
  ssh user@your-vps-ip
  ```

- [ ] Update system
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

- [ ] (Optional) Configure firewall
  ```bash
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw enable
  ```

### 4. Domain Configuration (Optional)

- [ ] Domain name registered
- [ ] DNS A record points to VPS IP
- [ ] Wait for DNS propagation (check with `dig your-domain.com`)

---

## Deployment

### 5. One-Command Deployment

```bash
# SSH into VPS
ssh user@your-vps-ip

# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/kenbin64/butterflyfxpython/main/deploy.sh -o deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh production
```

**Checklist:**
- [ ] Script downloads successfully
- [ ] Docker installs (if needed)
- [ ] Repository clones from GitHub
- [ ] Docker image builds
- [ ] Container starts
- [ ] Health check passes
- [ ] Server accessible at http://your-vps-ip:8000

### 6. Verify Deployment

```bash
# Health check
curl http://your-vps-ip:8000/api/v1/health

# Metrics
curl http://your-vps-ip:8000/api/v1/metrics

# API docs
curl http://your-vps-ip:8000/api/v1/docs
```

**Checklist:**
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Metrics show correct substrate count
- [ ] API docs accessible
- [ ] Can create substrate via API
- [ ] Can invoke substrate via API

---

## Post-Deployment

### 7. Monitoring Setup

- [ ] Check container status
  ```bash
  sudo docker-compose ps
  ```

- [ ] Monitor logs
  ```bash
  sudo docker-compose logs -f
  ```

- [ ] Monitor resources
  ```bash
  sudo docker stats
  ```

### 8. SSL/HTTPS (Recommended for Production)

- [ ] Install Certbot
  ```bash
  sudo apt install certbot python3-certbot-nginx -y
  ```

- [ ] Get SSL certificate
  ```bash
  sudo certbot --nginx -d your-domain.com
  ```

- [ ] Verify HTTPS works
  ```bash
  curl https://your-domain.com/api/v1/health
  ```

- [ ] Set up auto-renewal
  ```bash
  sudo certbot renew --dry-run
  ```

### 9. Performance Testing

- [ ] Run load tests (see BUTTERFLYFX_SERVER_PERFORMANCE.md)
  ```bash
  pip install locust
  locust -f tests/locustfile.py --host http://your-vps-ip:8000
  ```

- [ ] Monitor memory usage under load
- [ ] Verify concurrent request handling
- [ ] Check response times

### 10. Backup & Recovery

- [ ] Document backup strategy
- [ ] Test container restart
  ```bash
  sudo docker-compose restart
  ```

- [ ] Test full redeployment
  ```bash
  sudo ./deploy.sh production
  ```

---

## Maintenance

### Regular Tasks

- [ ] **Weekly:** Check logs for errors
  ```bash
  sudo docker-compose logs --tail=100
  ```

- [ ] **Weekly:** Monitor resource usage
  ```bash
  free -h
  df -h
  sudo docker stats
  ```

- [ ] **Monthly:** Update system packages
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

- [ ] **Monthly:** Renew SSL certificate (automatic with Certbot)

### Updates from GitHub

```bash
cd /opt/butterflyfx
sudo git pull origin main
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

Or use deployment script:
```bash
sudo ./deploy.sh production
```

---

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
sudo docker-compose logs
sudo docker-compose down
sudo docker-compose up -d
```

**Port already in use:**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

**Out of memory:**
```bash
free -h
# Reduce WORKERS in docker-compose.yml
sudo docker-compose restart
```

**Can't connect from outside:**
```bash
# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp
```

---

## Success Criteria

✅ **Deployment is successful when:**

1. Health check returns `{"status": "healthy"}`
2. API documentation accessible at `/api/v1/docs`
3. Can create and invoke substrates via API
4. Server handles expected load (10K+ req/sec)
5. Memory usage within limits (<15GB)
6. Logs show no errors
7. Container restarts automatically on failure
8. Updates deploy successfully from GitHub

---

**Your ButterflyFx server is production-ready!** 🦋🚀

