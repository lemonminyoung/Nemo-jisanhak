# 🧪 Chemical Safety Analysis API

화학물질 안전성 분석 API - NOAA CAMEO 데이터베이스 기반 규칙 분석 + AI 요약

[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=flat-square)](https://nemo-jisanhak-6lu8.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

---

## 🚀 빠른 시작

### API 호출 (5분 안에 연동)
```bash
curl -X POST "https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze" \
  -H "Content-Type: application/json" \
  -d '{"substances": ["Bleach", "Ammonia"], "use_ai": true}' \
  --max-time 300
```

### 응답 예시
```json
{
  "simple_response": {
    "risk_level": "위험",
    "message": "안녕하세요! 화학 안전 도우미입니다. 😊\n\n확인 결과 1가지 위험한 조합이 발견되었습니다!\n\n락스(표백제)와 암모니아가 만나면 유독가스가 발생하여 호흡곤란, 폐손상이 발생할 수 있어요..."
  },
  "safety_links": {
    "specific_links": [...],
    "msds_links": [...],
    "general_resources": [...]
  }
}
```

---

## 📚 문서

**백엔드 개발자라면 이것만 보세요!**
- 📖 **[BACKEND_INTEGRATION_GUIDE.md](./BACKEND_INTEGRATION_GUIDE.md)** - 5분 통합 가이드 (JavaScript, Python, Java 샘플 코드)
- 📋 **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - 전체 API 명세서

---

## ✨ 주요 기능

### 1. 규칙 기반 분석 (100% 정확도)
- **NOAA CAMEO 데이터베이스** 실시간 크롤링
- 화학물질 조합별 위험도 자동 분류
- 11가지 위험 유형 분석 (폭발, 독성가스, 화재 등)

### 2. AI 요약 (사용자 친화적)
- **Hugging Face Qwen2-1.5B** 모델로 영어 분석
- **Google Gemini 2.5-flash** 한국어 번역
- 중복 제거 및 구체적 조건 명시
- 안전 사용법 제시

### 3. 안전 정보 링크 (NEW!)
- 특정 화학물질 조합에 대한 사고예방 기사
- 각 화학물질의 MSDS(물질안전보건자료) 링크
- KOSHA, 환경부 등 공식 자료

---

## 🏗️ 기술 스택

| Category | Technology |
|----------|-----------|
| **Backend** | FastAPI, Python 3.11 |
| **Web Scraping** | Playwright (Chromium) |
| **AI Analysis** | Hugging Face Spaces (Qwen2-1.5B) |
| **Translation** | Google Gemini 2.5-flash API |
| **Deployment** | Render.com (Auto-deploy from GitHub) |
| **Database** | NOAA CAMEO (Real-time crawling) |

---

## 📦 설치 및 실행

### 1. 레포지토리 클론
```bash
git clone https://github.com/lemonminyoung/Nemo-jisanhak.git
cd Nemo-jisanhak
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. 환경 변수 설정
`.env` 파일 생성:
```env
AI_API_URL=https://gimchabssal-chemical-ai.hf.space
GEMINI_API_KEY=your-gemini-api-key-here
```

### 4. 서버 실행
```bash
python backend_with_hf.py
```

서버는 `http://localhost:8000`에서 실행됩니다.

---

## 🧪 테스트

### 간단한 테스트
```bash
python test_api_multiple.py
```

### Postman으로 테스트
```
POST http://localhost:8000/hybrid-analyze
Content-Type: application/json

{
  "substances": ["Bleach", "Ammonia"],
  "use_ai": true
}
```

---

## 📊 API 엔드포인트

### 1. Health Check
```
GET /
```

### 2. Simple Analyze (빠름, 규칙만)
```
POST /simple-analyze
```
- 응답 시간: ~30-60초
- CAMEO 규칙 분석만 제공

### 3. Hybrid Analyze (느림, AI 포함) ⭐ 권장
```
POST /hybrid-analyze
```
- 응답 시간: ~2-4분
- CAMEO 규칙 + AI 요약 + 안전 링크

**상세 사용법**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) 참고

---

## 🎯 사용 예시

### JavaScript (React/Node.js)
```javascript
const result = await fetch('https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    substances: ['Bleach', 'Ammonia'],
    use_ai: true
  }),
  timeout: 300000  // 5분
});

const data = await result.json();
console.log(data.simple_response.risk_level);  // "위험"
console.log(data.simple_response.message);     // 사용자 메시지
```

### Python
```python
import requests

response = requests.post(
    'https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze',
    json={'substances': ['Bleach', 'Ammonia'], 'use_ai': True},
    timeout=300
)

data = response.json()
print(data['simple_response']['risk_level'])
print(data['simple_response']['message'])
```

더 많은 예시: [BACKEND_INTEGRATION_GUIDE.md](./BACKEND_INTEGRATION_GUIDE.md)

---

## 📁 프로젝트 구조

```
Nemo-jisanhak/
├── backend_with_hf.py           # FastAPI 메인 서버
├── safety_links.py              # 안전 정보 링크 데이터베이스
├── requirements.txt             # Python 의존성
├── render.yaml                  # Render 배포 설정
├── API_DOCUMENTATION.md         # API 전체 명세서
├── BACKEND_INTEGRATION_GUIDE.md # 백엔드 통합 가이드
├── test_api_multiple.py         # API 테스트 스크립트
└── README.md                    # 이 파일
```

---

## 🔧 주요 설정

### 타임아웃 설정 (중요!)
API 응답 시간이 길기 때문에 클라이언트에서 반드시 타임아웃을 설정해야 합니다:
- `/simple-analyze`: 최소 120초 (2분)
- `/hybrid-analyze`: 최소 300초 (5분)

### Cold Start 처리 및 성능 개선
Render 무료 플랜 사용 시 첫 요청은 30-60초 추가 소요됩니다.

**⚡ 성능 개선 방법**:
- **UptimeRobot 설정** (무료) - Cold Start 방지, 응답 시간 50% 단축!
- 📖 **[UPTIME_ROBOT_SETUP.md](./UPTIME_ROBOT_SETUP.md)** - 5분 안에 설정 가능

---

## 🌟 주요 업데이트

### v2.1.0 (2025-01-06)
- ✅ `safety_links` 필드 추가 (MSDS, 공식 자료 링크)
- ✅ Gemini 프롬프트 개선 (중복 제거, 구체적 조건 명시, 안전 사용법)
- ✅ 백엔드 개발자용 통합 가이드 추가

### v2.0.0 (2025-01-06)
- ✅ Hugging Face Spaces 연동 (Qwen2-1.5B)
- ✅ Gemini 2.5-flash 한국어 번역
- ✅ `simple_response` 필드 추가 (백엔드 사용 편의성)

### v1.0.0
- ✅ CAMEO 크롤링 기반 규칙 분석

---

## 📄 라이선스

MIT License

---

## 🤝 기여하기

이슈 및 PR은 언제나 환영합니다!

- **GitHub Issues**: https://github.com/lemonminyoung/Nemo-jisanhak/issues
- **Pull Requests**: https://github.com/lemonminyoung/Nemo-jisanhak/pulls

---

## 📧 문의

백엔드 통합 관련 문의는 GitHub Issues에 남겨주세요.

---

**⚠️ 주의사항**: 이 API는 교육 및 일반 안전 정보 제공 목적입니다. 산업용 또는 전문적인 화학 안전 결정에는 반드시 전문가의 검토가 필요합니다.
