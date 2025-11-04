# Deployment Guide - Chemical Safety Analyzer API

## 준비된 배포 플랫폼

### 1. Railway.app (추천 ⭐)

**장점:**
- 무료 크레딧 월 $5 제공
- Playwright/Chromium 지원 우수
- 타임아웃 관대함 (크롤링에 적합)
- GitHub 자동 배포

**배포 방법:**

1. Railway 계정 생성: https://railway.app
2. GitHub에 프로젝트 푸시 (선택사항)
3. Railway 대시보드에서 "New Project" 클릭
4. "Deploy from GitHub repo" 선택 (또는 "Empty Project"로 시작)
5. 환경 변수 설정:
   - `COLAB_API_URL`: Colab ngrok URL (예: https://abc123.ngrok.io)
   - `GEMINI_API_KEY`: AIzaSyAnLtULeCMJHjHgSrcfaLO-QH24TqNdLJ0
   - `PORT`: 8000 (자동 설정됨)

6. 배포!

**필요한 파일:**
- ✅ `requirements.txt`
- ✅ `railway.json`
- ✅ `Procfile`
- ✅ `runtime.txt`

---

### 2. Render.com

**장점:**
- 무료 티어 있음 (750시간/월)
- 간단한 YAML 설정
- 자동 SSL 인증서

**단점:**
- 무료 티어는 15분 비활성 후 스핀다운 (첫 요청 느림)
- 월 750시간 제한

**배포 방법:**

1. Render 계정 생성: https://render.com
2. GitHub에 프로젝트 푸시
3. "New Web Service" 클릭
4. GitHub 레포 연결
5. Render가 자동으로 `render.yaml` 감지
6. 환경 변수 설정 (Railway와 동일)
7. Deploy!

**필요한 파일:**
- ✅ `requirements.txt`
- ✅ `render.yaml`

---

### 3. Fly.io

**장점:**
- Docker 기반 (완전한 환경 제어)
- 무료 티어: 3개 shared-cpu VM
- 항상 켜져 있음 (스핀다운 없음)
- Playwright 지원 완벽

**배포 방법:**

1. Fly CLI 설치:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. 로그인:
   ```bash
   fly auth login
   ```

3. 앱 생성:
   ```bash
   fly launch
   ```

4. 환경 변수 설정:
   ```bash
   fly secrets set COLAB_API_URL="https://your-colab-url.ngrok.io"
   fly secrets set GEMINI_API_KEY="AIzaSyAnLtULeCMJHjHgSrcfaLO-QH24TqNdLJ0"
   ```

5. 배포:
   ```bash
   fly deploy
   ```

**필요한 파일:**
- `Dockerfile` 생성 필요 (아래 참조)

---

## 추가 설정 파일

### Dockerfile (Fly.io 또는 Docker 배포용)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend_with_colab:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 환경 변수 설정

모든 플랫폼에서 다음 환경 변수를 설정해야 합니다:

| 변수명 | 값 | 설명 |
|--------|-----|------|
| `COLAB_API_URL` | `https://xxxx.ngrok.io` | Colab ngrok URL |
| `GEMINI_API_KEY` | `AIzaSy...` | Gemini API 키 |
| `PORT` | `8000` | 서버 포트 (자동 설정) |

---

## 배포 후 테스트

배포 완료 후 다음 명령으로 테스트:

```bash
curl -X POST https://your-deployed-url.com/hybrid-analyze \
  -H "Content-Type: application/json" \
  -d '{"substances": ["Hydrogen Peroxide", "Acetic Acid"], "use_ai": true}'
```

또는 Python으로:

```python
import requests

response = requests.post(
    "https://your-deployed-url.com/hybrid-analyze",
    json={
        "substances": ["Hydrogen Peroxide", "Acetic Acid"],
        "use_ai": True
    }
)

print(response.json())
```

---

## 추천 배포 순서

1. **Railway.app** - 가장 간단하고 빠름
2. **Render** - 무료 티어 좋음 (스핀다운 감수)
3. **Fly.io** - Docker 경험 있으면 최고

---

## 주의사항

1. **Colab URL 업데이트**: Colab ngrok URL은 재시작 시마다 변경됩니다. 환경 변수를 업데이트해야 합니다.
2. **타임아웃**: 크롤링 시간이 길면 (>30초) Railway나 Fly.io 추천
3. **비용**: Railway 무료 크레딧은 한 달에 $5, 초과 시 과금됨
4. **Playwright 메모리**: 브라우저 자동화는 메모리를 많이 사용합니다. 프리 티어에서 문제 생기면 업그레이드 고려

---

## 배포 완료 후

API 엔드포인트를 백엔드 팀에게 공유:

- Base URL: `https://your-app.railway.app` (또는 render.com, fly.dev)
- Endpoint: `POST /hybrid-analyze`
- Request body:
  ```json
  {
    "substances": ["Chemical1", "Chemical2", "Chemical3"],
    "use_ai": true
  }
  ```
- Response:
  ```json
  {
    "risk_level": "위험",
    "message": "6가지 위험 결과가 발견되었습니다!..."
  }
  ```

완료! 🎉
