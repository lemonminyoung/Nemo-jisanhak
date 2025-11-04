# ngrok 문제 해결 가이드

## 문제: localhost:5000만 나오고 ngrok URL이 생성되지 않음

### 원인

Colab에서 ngrok 터널이 제대로 생성되지 않았습니다. 가능한 원인:

1. **ngrok 토큰 문제**: 토큰이 만료되었거나 유효하지 않음
2. **패키지 버전 문제**: pyngrok 버전이 오래됨
3. **기존 터널 충돌**: 이미 실행 중인 터널이 있음
4. **Colab 제한**: Google Colab의 네트워크 제한

---

## ✅ 해결 방법

### 방법 1: 수정된 노트북 재업로드 (권장)

방금 수정한 `ChemLLM_Colab_API.ipynb` 파일을 다시 업로드하세요.

**수정 사항**:
- Cell 3: `nest-asyncio` 패키지 추가
- Cell 18: 향상된 ngrok 에러 처리 및 URL 추출 로직

**실행 방법**:
```
1. Colab에서 현재 세션 종료
2. File > Upload notebook
3. 수정된 ChemLLM_Colab_API.ipynb 업로드
4. Runtime > Change runtime type > T4 GPU
5. Runtime > Run all
```

---

### 방법 2: ngrok 토큰 재생성

1. **ngrok 대시보드 접속**:
   ```
   https://dashboard.ngrok.com/get-started/your-authtoken
   ```

2. **새 토큰 생성**:
   - "Your Authtoken" 섹션에서 토큰 복사
   - Regenerate 버튼 클릭 (선택사항)

3. **Colab Cell 18 수정**:
   ```python
   NGROK_AUTH_TOKEN = "새로_받은_토큰"
   ```

---

### 방법 3: 패키지 수동 재설치

Colab에서 새 코드 셀 추가 후 실행:

```python
# 기존 패키지 제거
!pip uninstall pyngrok -y

# 최신 버전 설치
!pip install pyngrok --upgrade

# ngrok 설치 확인
!ngrok version

# Flask도 재설치
!pip install flask --upgrade
```

---

### 방법 4: ngrok CLI 직접 사용

Colab에서 ngrok CLI를 직접 사용하는 방법:

```python
# Cell 1: ngrok 다운로드 및 설치
!wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
!tar -xvzf ngrok-v3-stable-linux-amd64.tgz

# Cell 2: ngrok 인증
!./ngrok config add-authtoken 34dflI9kRYLX8COEWV7CxYAAQMA_W7dBiZTCfp6oe3Lf1LTY

# Cell 3: Flask 서버 백그라운드 실행
import threading
import time

def run_flask():
    app.run(port=5000, use_reloader=False)

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()
time.sleep(2)

# Cell 4: ngrok 터널 시작
!./ngrok http 5000 --log=stdout > ngrok.log &

# Cell 5: ngrok URL 확인
import time
time.sleep(3)

!curl http://localhost:4040/api/tunnels
```

---

### 방법 5: 대체 터널 서비스 사용

ngrok가 계속 실패하면 대체 서비스 사용:

#### **LocalTunnel** (무료, 설치 간단)

```python
# 설치
!npm install -g localtunnel

# Flask 서버 백그라운드 실행
import threading
def run_flask():
    app.run(port=5000, use_reloader=False)

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# LocalTunnel 시작
!lt --port 5000
```

#### **Cloudflared** (Cloudflare, 무료)

```python
# 설치
!wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
!chmod +x cloudflared-linux-amd64

# Flask 서버 백그라운드 실행
import threading
def run_flask():
    app.run(port=5000, use_reloader=False)

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Cloudflared 터널
!./cloudflared-linux-amd64 tunnel --url http://localhost:5000
```

---

## 🔍 디버깅 체크리스트

실행 전에 다음을 확인하세요:

### 1. Colab 환경 확인
```python
# GPU 할당 확인
!nvidia-smi

# Python 버전
!python --version

# 패키지 버전
!pip show pyngrok flask
```

### 2. ngrok 상태 확인
```python
from pyngrok import ngrok

# 기존 터널 조회
tunnels = ngrok.get_tunnels()
print(f"Active tunnels: {len(tunnels)}")
for tunnel in tunnels:
    print(f"  - {tunnel.public_url}")

# 모든 터널 종료
ngrok.kill()
```

### 3. 포트 확인
```bash
# 5000 포트 사용 중인지 확인
!netstat -tulpn | grep 5000

# 또는
!lsof -i :5000
```

### 4. Flask 앱 확인
```python
# Flask 앱이 정상적으로 로드되었는지 확인
print(f"Flask app: {app}")
print(f"Routes: {list(app.url_map.iter_rules())}")
```

---

## 📝 성공 확인

ngrok가 정상적으로 작동하면 다음과 같은 출력이 나와야 합니다:

```
======================================================================
🚀 Starting ngrok tunnel...
======================================================================
✅ Killed existing ngrok tunnels
✅ ngrok auth token set

======================================================================
🎉 API Server is ready!
======================================================================

📌 Public URL: https://xxxx-xx-xx-xx-xx.ngrok-free.app

💡 사용 방법:
  1. 위 URL을 복사하세요
  2. 로컬 .env 파일에 다음과 같이 추가:
     COLAB_API_URL=https://xxxx-xx-xx-xx-xx.ngrok-free.app

🧪 테스트:
  curl https://xxxx-xx-xx-xx-xx.ngrok-free.app/health

======================================================================

⏳ Starting Flask server on port 5000...
📍 Endpoints:
   - GET  /health
   - POST /analyze

======================================================================
 * Serving Flask app '__main__'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

**중요**: `http://localhost:5000`만 나오고 `https://xxxx.ngrok.io` URL이 없으면 실패한 것입니다!

---

## 🆘 여전히 안 되면?

### 최후의 수단: Colab 포트포워딩 사용 (복잡함)

Google Colab에는 기본 포트포워딩이 없지만, SSH 터널을 통해 가능합니다:

```python
# Colab에서 SSH 서버 실행
!apt-get install -qq openssh-server
!echo "root:password" | chpasswd
!service ssh start

# 로컬에서 SSH 터널 생성
# (로컬 터미널에서)
# ssh -L 8000:localhost:5000 root@<colab-ip>
```

**하지만 이 방법은 권장하지 않습니다!** ngrok나 대체 서비스를 사용하세요.

---

## 💡 권장 흐름

1. **방법 1 시도**: 수정된 노트북 재업로드 (가장 간단)
2. **방법 2 시도**: ngrok 토큰 재생성
3. **방법 3 시도**: 패키지 재설치
4. **방법 5 시도**: LocalTunnel 또는 Cloudflared 사용

---

## 📞 추가 도움

- ngrok 문서: https://ngrok.com/docs
- pyngrok 문서: https://pyngrok.readthedocs.io/
- Colab FAQ: https://research.google.com/colaboratory/faq.html

---

## ✅ 다음 단계 (ngrok 성공 후)

1. ✅ ngrok URL 복사
2. ✅ 로컬 `.env` 파일 업데이트:
   ```bash
   COLAB_API_URL=https://복사한-url.ngrok.io
   ```
3. ✅ 로컬에서 테스트:
   ```bash
   python test_colab_connection.py
   ```
4. ✅ 백엔드 실행:
   ```bash
   python backend_with_colab.py
   ```

화이팅! 🚀
