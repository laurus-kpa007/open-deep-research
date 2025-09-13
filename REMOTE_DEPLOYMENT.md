# 원격 배포 가이드 / Remote Deployment Guide

## 📋 사전 요구사항

- Linux 서버 (Ubuntu 20.04+ 권장)
- Docker & Docker Compose 설치
- 8GB+ RAM, 4+ CPU cores
- 포트 80, 443, 3000, 8000 개방
- 도메인 (선택사항)

## 🚀 배포 단계

### 1. 서버 준비

```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
newgrp docker
```

### 2. 프로젝트 클론

```bash
git clone https://github.com/your-repo/open_deep_research.git
cd open_deep_research
```

### 3. 환경 변수 설정

```bash
# 프로덕션 환경 변수 복사
cp .env.production .env

# .env 파일 수정
nano .env
```

다음 값들을 실제 서버 정보로 수정:

```env
# 서버 주소 설정 (IP 또는 도메인)
SERVER_HOST=your-server-ip-or-domain.com

# Frontend URLs (서버 IP/도메인으로 변경)
NEXT_PUBLIC_API_URL=http://your-server-ip:8000
NEXT_PUBLIC_WS_URL=ws://your-server-ip:8000

# Backend CORS (허용할 원격 주소)
CORS_ORIGINS=http://your-server-ip:3000,http://your-domain.com

# API 키
TAVILY_API_KEY=your_actual_api_key

# 보안 키 (강력한 암호로 변경)
SECRET_KEY=generate-strong-secret-key
POSTGRES_PASSWORD=strong-database-password
REDIS_PASSWORD=strong-redis-password
```

### 4. 방화벽 설정

```bash
# UFW 사용 시
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
sudo ufw reload

# iptables 사용 시
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables-save
```

### 5. Docker Compose 실행

```bash
# 프로덕션 설정으로 실행
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

### 6. 서비스 확인

```bash
# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# Ollama 모델 확인
docker exec -it open_deep_research_ollama_1 ollama list

# 헬스체크
curl http://localhost:8000/health
curl http://localhost:3000
```

## 🔒 보안 설정

### SSL/TLS 설정 (HTTPS)

#### Let's Encrypt 사용

```bash
# Certbot 설치
sudo apt update
sudo apt install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot certonly --standalone -d your-domain.com

# nginx.conf 수정하여 SSL 적용
```

#### Nginx 설정 파일 생성

```bash
nano nginx/nginx.conf
```

```nginx
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### 보안 강화

```bash
# 기본 포트 변경 (옵션)
# docker-compose.prod.yml에서 포트 매핑 수정

# IP 화이트리스트 설정 (특정 IP만 허용)
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Rate limiting 설정 (nginx)
# nginx.conf에 추가:
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

## 📊 모니터링

### 로그 확인

```bash
# 모든 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 리소스 모니터링

```bash
# Docker 리소스 사용량
docker stats

# 시스템 리소스
htop
```

## 🔄 업데이트 & 유지보수

### 서비스 업데이트

```bash
# 코드 업데이트
git pull origin main

# 컨테이너 재빌드 및 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 백업

```bash
# 데이터베이스 백업
docker exec open_deep_research_postgres_1 pg_dump -U research_user research_db > backup_$(date +%Y%m%d).sql

# 볼륨 백업
docker run --rm -v open_deep_research_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz /data
```

## 🚨 문제 해결

### 연결 문제

1. **프론트엔드가 백엔드에 연결되지 않음**
   ```bash
   # CORS 설정 확인
   docker-compose -f docker-compose.prod.yml exec backend env | grep CORS

   # 방화벽 확인
   sudo ufw status
   ```

2. **WebSocket 연결 실패**
   ```bash
   # nginx 설정 확인 (Upgrade 헤더)
   # 브라우저 콘솔에서 WebSocket 연결 URL 확인
   ```

3. **Ollama 모델 로드 실패**
   ```bash
   # Ollama 컨테이너 접속
   docker exec -it open_deep_research_ollama_1 bash

   # 모델 다시 다운로드
   ollama pull gemma3:12b
   ```

### 성능 최적화

```bash
# Docker 리소스 제한 조정
# docker-compose.prod.yml에서 deploy.resources 수정

# 스왑 메모리 추가 (메모리 부족 시)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📝 체크리스트

배포 전 확인 사항:

- [ ] 환경 변수 설정 완료
- [ ] 방화벽 규칙 설정
- [ ] Docker & Docker Compose 설치
- [ ] 서버 IP/도메인으로 URL 수정
- [ ] CORS 설정 확인
- [ ] SSL 인증서 설정 (프로덕션)
- [ ] 백업 스크립트 설정
- [ ] 모니터링 도구 설정

## 🆘 지원

문제 발생 시:
1. 로그 확인: `docker-compose -f docker-compose.prod.yml logs`
2. GitHub Issues에 문제 보고
3. 커뮤니티 포럼 참조