# Chemical Safety Analyzer API

화학물질 안전성 분석 API - NOAA CAMEO 데이터 기반 규칙 분석 + AI 요약

## 기능

- **규칙 기반 분석**: NOAA CAMEO 데이터베이스의 정확한 화학 반응성 데이터 사용 (100% 정확도)
- **AI 요약**: Google Gemini API로 사용자 친화적인 한국어 안전 메시지 생성
- **하이브리드 접근**: 정확성 + 사용자 편의성

## API 엔드포인트

### POST `/hybrid-analyze`

화학물질 목록을 분석하여 위험한 조합을 찾고 AI 요약을 제공합니다.

**요청:**
```json
{
  "substances": [
    "Hydrogen Peroxide",
    "Acetic Acid",
    "Sodium Hydroxide"
  ],
  "use_ai": true
}
```

**응답:**
```json
{
  "risk_level": "위험",
  "message": "3가지 위험 결과가 발견되었습니다!\n\n빙초산과 과산화수소가 만나면..."
}
```

## 기술 스택

- **Backend**: FastAPI, Python 3.11
- **크롤링**: Playwright (NOAA CAMEO)
- **AI**: Google Gemini API (번역), Colab ChemLLM (분석)
- **배포**: Railway.app

## 환경 변수

```env
COLAB_API_URL=https://your-colab-ngrok-url.ngrok.io
GEMINI_API_KEY=your-gemini-api-key
```

## 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt
playwright install chromium

# 서버 실행
python backend_with_colab.py
```

서버는 `http://localhost:8000`에서 실행됩니다.

## 테스트

```bash
python test_hybrid_analyze.py
```

## 라이선스

MIT
