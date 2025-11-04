# Colab ChemLLM 통합 가이드

이 가이드는 Google Colab에서 ChemLLM 모델을 실행하고 로컬 백엔드와 연결하는 방법을 설명합니다.

## 📋 개요

```
┌─────────────────┐      HTTP      ┌──────────────────┐
│  로컬 백엔드    │ ────────────> │  Colab (Flask)   │
│ (FastAPI)       │                │  + ngrok 터널    │
│                 │ <──────────── │                  │
└─────────────────┘   AI 분석     └──────────────────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │ ChemLLM 모델 │
                                   │ (GPU: T4)    │
                                   └──────────────┘
```

**장점**:
- ✅ 완전 무료 (Google Colab 무료 GPU)
- ✅ 화학 전문 모델 사용 가능
- ✅ 로컬에 GPU 불필요

**단점**:
- ⚠️ Colab 세션 12시간 제한
- ⚠️ ngrok URL이 세션마다 변경됨
- ⚠️ 첫 모델 로딩에 5-10분 소요

---

## 🚀 단계별 설정

### 1️⃣ Colab 노트북 실행

#### 1-1. 노트북 열기
1. Google Colab 접속: https://colab.research.google.com/
2. `ChemLLM_Colab_API.ipynb` 파일 업로드
   - File > Upload notebook
   - 또는 GitHub에서 직접 열기

#### 1-2. GPU 활성화
1. Runtime > Change runtime type
2. Hardware accelerator: **T4 GPU** 선택
3. Save

#### 1-3. Colab Secrets 설정 (선택사항)
1. 왼쪽 🔑 아이콘 클릭 (Secrets)
2. Add new secret:
   - Name: `HF_TOKEN`
   - Value: `YOUR_HF_TOKEN_HERE` (또는 본인 토큰)

> 💡 이 단계를 건너뛰면 하드코딩된 토큰이 사용됩니다.

#### 1-4. 모든 셀 실행
1. Runtime > Run all
2. 각 셀이 순서대로 실행되는지 확인

**주요 단계**:
- Cell 2: GPU 확인 (`nvidia-smi`)
- Cell 3: 패키지 설치 (5분 소요)
- Cell 6: 모델 로드 (Qwen2-1.5B, 3-5분 소요)
- Cell 8-11: 분석 함수 로드
- Cell 16: Flask API 서버 시작
- Cell 19: **ngrok 터널 시작 및 URL 출력** ⭐

#### 1-5. ngrok URL 복사

Cell 19 실행 결과에서 다음과 같은 출력을 찾으세요:

```
 * ngrok tunnel URL: https://xxxx-xx-xx-xx-xx.ngrok.io
======================================================================
🎉 API Server is ready!
======================================================================

📌 Public URL: https://xxxx-xx-xx-xx-xx.ngrok.io
```

**이 URL을 복사하세요!** 예:
```
https://1a2b-34-56-78-90.ngrok-free.app
```

---

### 2️⃣ 로컬 환경 설정

#### 2-1. .env 파일 업데이트

프로젝트 폴더의 `.env` 파일을 열고 `COLAB_API_URL`을 업데이트:

```bash
# .env 파일

HF_API_TOKEN=YOUR_HF_TOKEN_HERE

# 👇 여기에 Colab에서 복사한 URL을 붙여넣기
COLAB_API_URL=https://1a2b-34-56-78-90.ngrok-free.app
```

⚠️ **주의**: URL 끝에 `/`를 붙이지 마세요!

#### 2-2. 의존성 설치 확인

```bash
pip install -r requirements.txt
```

---

### 3️⃣ 연결 테스트

#### 3-1. Colab API 테스트

새로 만든 테스트 스크립트를 실행하세요:

```bash
python test_colab_connection.py
```

**성공 시 출력**:
```
======================================================================
🔗 Colab API 연결 테스트
======================================================================

📌 Colab URL: https://xxxx.ngrok.io

1️⃣ Health Check 테스트...
   ✅ 연결 성공!
   📊 상태: healthy
   🤖 모델: YourModelNameHere

2️⃣ AI 분석 테스트...
   📤 테스트 데이터 전송 중...
   ✅ AI 분석 성공!

   📝 분석 결과 (처음 500자):
   ----------------------------------------------------------------------
   1. RISK LEVEL: HIGH

   2. KEY CHEMICALS:
      - HYDROCHLORIC ACID
      - SODIUM HYDROXIDE
   ...
   ----------------------------------------------------------------------

======================================================================
🎉 모든 테스트 통과! Colab API가 정상 작동 중입니다.
======================================================================
```

**실패 시 해결 방법**:

| 오류 | 원인 | 해결 방법 |
|------|------|----------|
| `COLAB_API_URL이 설정되지 않았습니다` | .env 파일 누락 | .env 파일에 URL 추가 |
| `연결 오류` | Colab 노트북이 실행 중이 아님 | Colab에서 Cell 19 다시 실행 |
| `타임아웃` | 모델 로딩 중 | 5분 후 다시 시도 |
| `HTTP 404` | ngrok URL 만료 | Colab에서 새 URL 받아서 .env 업데이트 |

---

### 4️⃣ 백엔드 실행

테스트가 성공하면 이제 백엔드를 실행하세요:

#### 방법 1: Python 직접 실행
```bash
cd C:\Users\김민영\Desktop\cameo_project
python backend_with_colab.py
```

#### 방법 2: Uvicorn 사용 (권장)
```bash
uvicorn backend_with_colab:app --reload --host 0.0.0.0 --port 8000
```

**출력**:
```
✅ Colab API URL configured: https://xxxx.ngrok.io
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

### 5️⃣ 전체 플로우 테스트

#### 5-1. API 테스트 (curl)

```bash
curl -X POST http://localhost:8000/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"substances\": [\"Acetic Acid\", \"Sodium Hydroxide\"], \"use_ai\": true}"
```

#### 5-2. API 테스트 (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "substances": ["Acetic Acid", "Sodium Hydroxide"],
        "use_ai": True
    }
)

result = response.json()

if result["success"]:
    print("✅ 성공!")
    print(f"\n📊 CAMEO 결과: {len(result['cameo_results'])}개 발견")
    print(f"🤖 AI 상태: {result['ai_status']}")

    if result["ai_analysis"]:
        print("\n📝 AI 분석:")
        print(result["ai_analysis"][:500])
else:
    print(f"❌ 실패: {result.get('error')}")
```

#### 5-3. 브라우저 테스트

브라우저에서 Swagger UI 접속:
```
http://localhost:8000/docs
```

- `/analyze` 엔드포인트 선택
- Try it out
- Request body 입력:
  ```json
  {
    "substances": ["Acetic Acid", "Sodium Hydroxide"],
    "use_ai": true
  }
  ```
- Execute

---

## 🔧 문제 해결

### 문제 1: ngrok URL이 만료됨

**증상**:
```
❌ 연결 오류: Colab 서버에 연결할 수 없습니다.
```

**해결**:
1. Colab 노트북의 Cell 19 다시 실행
2. 새 ngrok URL 복사
3. `.env` 파일 업데이트
4. 백엔드 재시작 (Ctrl+C 후 다시 실행)

---

### 문제 2: 모델이 응답하지 않음

**증상**:
```
❌ 타임아웃: AI 모델이 응답하지 않습니다.
```

**원인**:
- 첫 실행 시 모델 로딩 중 (5-10분)
- GPU 메모리 부족

**해결**:
1. Colab Cell 6에서 모델 로딩 완료 확인:
   ```
   ✅ Qwen2-1.5B loaded!
   💻 Device: cuda:0
   ```
2. 5분 후 다시 시도
3. 여전히 실패하면 Colab 런타임 재시작:
   - Runtime > Restart runtime
   - Run all 다시 실행

---

### 문제 3: Colab 세션 만료

**증상**:
```
❌ HTTP 502: Bad Gateway
```

**원인**:
- Colab 무료 버전은 12시간 후 세션 종료
- 90분 미사용 시 자동 종료

**해결**:
1. Colab 노트북에서 Runtime > Run all
2. 새 ngrok URL 복사 및 .env 업데이트
3. 백엔드 재시작

**방지 방법**:
- Colab Pro 구독 ($9.99/월)
- 또는 정기적으로 노트북 재실행

---

### 문제 4: GPU 할당 안됨

**증상**:
```
💻 Device: cpu
```

**해결**:
1. Runtime > Change runtime type
2. T4 GPU 선택
3. Runtime > Restart runtime
4. Run all

---

## 📊 성능 최적화

### 모델 변경

현재 사용 중인 모델: **Qwen2-1.5B-Instruct** (가볍고 빠름)

더 나은 성능을 원하면 Cell 6에서 모델 변경:

#### 옵션 1: Mistral-7B (더 정확, 느림)
```python
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
```

#### 옵션 2: Phi-3-mini (균형잡힌 성능)
```python
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
```

#### 옵션 3: ChemLLM-7B (화학 전문, 느림)
```python
MODEL_NAME = "AI4Chem/ChemLLM-7B-Chat"
```

---

## 🎯 다음 단계

통합이 완료되면:

1. ✅ `app.py`를 Render에 배포
2. ✅ Render 환경변수에 `COLAB_API_URL` 추가
3. ✅ 프론트엔드 개발 시작
4. ✅ 데이터베이스 연동 (결과 캐싱)

---

## 📚 참고 자료

- [ngrok 공식 문서](https://ngrok.com/docs)
- [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)
- [Flask API 문서](https://flask.palletsprojects.com/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)

---

## 💡 팁

1. **Colab 세션 유지**:
   - 브라우저 탭을 열어두기
   - 매 2시간마다 셀 하나 실행하기

2. **ngrok URL 관리**:
   - URL을 메모장에 저장
   - 변경 시마다 .env 파일 업데이트

3. **디버깅**:
   - Colab 출력 확인
   - 백엔드 로그 확인 (`[Colab]` 태그)
   - `test_colab_connection.py` 먼저 실행

4. **비용 절감**:
   - Colab 무료 버전으로 충분
   - ngrok 무료 계정 사용 가능
   - Render 무료 플랜으로 배포
