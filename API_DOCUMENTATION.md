# Chemical Safety Analysis API Documentation

## 🚀 빠른 시작 (5분 안에 연동하기)

### 1. API 호출 (가장 간단한 방법)
```bash
curl -X POST "https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze" \
  -H "Content-Type: application/json" \
  -d '{"substances": ["Bleach", "Ammonia"], "use_ai": true}'
```

### 2. 백엔드에서 사용할 필드 (이것만 보세요!)
```json
{
  "simple_response": {
    "risk_level": "위험",    // "위험", "주의", "안전" 중 하나
    "message": "안녕하세요! 화학 안전 도우미입니다..."  // 사용자에게 보여줄 메시지
  },
  "safety_links": {
    "msds_links": [...],           // 각 화학물질 MSDS 링크
    "general_resources": [...]     // KOSHA 등 공식 자료
  }
}
```

### 3. 주의사항
- ⏱️ **타임아웃**: 최소 300초 (5분) 설정 필요
- 🐢 **첫 요청**: Cold start로 30-60초 추가 소요
- 💡 **권장**: `simple_response` 필드만 사용하세요 (나머지는 무시해도 됨)

---

## Base URL
```
https://nemo-jisanhak-6lu8.onrender.com
```

## Overview
화학 물질 안전성 분석 API입니다. CAMEO 데이터베이스 기반의 규칙 분석과 AI 요약을 제공합니다.

---

## Endpoints

### 1. Health Check
서버 상태 확인

**Endpoint**: `GET /`

**Response**:
```json
{
  "message": "Chemical Safety Analysis API",
  "status": "running",
  "version": "2.0.0",
  "ai_status": "configured"
}
```

---

### 2. Simple Analyze (권장)
규칙 기반 분석만 제공 (빠르고 정확)

**Endpoint**: `POST /simple-analyze`

**Request Body**:
```json
{
  "substances": ["Hydrogen Peroxide", "Acetic Acid"]
}
```

**Response Time**: ~30-60초 (CAMEO 크롤링 시간)

**Response**:
```json
{
  "summary": {
    "total_pairs": 1,
    "total_chemicals": 2,
    "chemicals_list": ["ACETIC ACID, GLACIAL", "HYDROGEN PEROXIDE..."],
    "dangerous_count": 1,
    "caution_count": 0,
    "safe_count": 0,
    "overall_status": "위험",
    "message": "[위험] 1개의 위험한 조합이 발견되었습니다! 즉시 분리 보관이 필요합니다."
  },
  "dangerous_pairs": [
    {
      "chemical_1": "ACETIC ACID, GLACIAL",
      "chemical_2": "HYDROGEN PEROXIDE...",
      "status": "incompatible",
      "risk_level": "위험",
      "severity_score": 23,
      "hazards": [
        "Explosive: Reaction products may be explosive",
        "Flammable: Reaction products may be flammable",
        "Generates gas: Reaction liberates gaseous products"
      ],
      "hazard_count": 11,
      "summary": "ACETIC ACID, GLACIAL와 HYDROGEN PEROXIDE는 절대 혼합 금지!"
    }
  ],
  "caution_pairs": [],
  "safe_pairs": [],
  "recommendations": [
    "[즉시 조치 필요]",
    "  - ACETIC ACID, GLACIAL와 HYDROGEN PEROXIDE를 최소 3m 이상 떨어뜨려 보관하세요",
    "[일반 안전 수칙]",
    "  - 화학물질 취급 시 장갑, 보안경 착용",
    "  - 비상 샤워 시설 위치 확인",
    "  - MSDS(물질안전보건자료) 비치"
  ]
}
```

---

### 3. Hybrid Analyze (AI 포함)
규칙 기반 분석 + AI 요약 제공

**Endpoint**: `POST /hybrid-analyze`

**Request Body**:
```json
{
  "substances": ["Hydrogen Peroxide", "Acetic Acid"],
  "use_ai": true
}
```

**Parameters**:
- `substances` (required): 화학 물질 이름 배열 (2개 이상)
- `use_ai` (optional): AI 요약 사용 여부 (기본값: true)

**Response Time**: ~2-4분 (CAMEO 크롤링 + AI 분석 + 번역)

**Response**:
```json
{
  "success": true,
  "rule_based_analysis": {
    "summary": {
      "total_pairs": 1,
      "total_chemicals": 2,
      "chemicals_list": ["ACETIC ACID, GLACIAL", "HYDROGEN PEROXIDE..."],
      "dangerous_count": 1,
      "caution_count": 0,
      "safe_count": 0,
      "overall_status": "위험",
      "message": "[위험] 1개의 위험한 조합이 발견되었습니다!"
    },
    "dangerous_pairs": [...],
    "caution_pairs": [],
    "safe_pairs": [],
    "recommendations": [...]
  },
  "ai_summary_english": "This is a warning sign that indicates potential danger...",
  "ai_summary_korean": "안녕하세요! 화학 안전 도우미입니다. 😊\n\n확인 결과 1가지 위험 결과가 발견되었습니다!\n\n`빙초산`과 `20%에서 60% 농도의 과산화수소 수용액`이 만날 경우...",
  "ai_status": "success",
  "simple_response": {
    "risk_level": "위험",
    "message": "안녕하세요! 화학 안전 도우미입니다. 😊\n\n확인 결과 1가지 위험 결과가 발견되었습니다!..."
  },
  "safety_links": {
    "specific_links": [
      {
        "title": "과산화수소 취급 안전 지침",
        "url": "https://www.kosha.or.kr",
        "source": "안전보건공단",
        "type": "안전지침"
      }
    ],
    "msds_links": [
      {
        "chemical": "ACETIC ACID, GLACIAL",
        "url": "https://msds.kosha.or.kr/MSDSInfo/kcic/msdsSearch.do?menuId=13&msdsEname=ACETIC+ACID,+GLACIAL",
        "title": "ACETIC ACID, GLACIAL 물질안전보건자료(MSDS)"
      },
      {
        "chemical": "HYDROGEN PEROXIDE",
        "url": "https://msds.kosha.or.kr/MSDSInfo/kcic/msdsSearch.do?menuId=13&msdsEname=HYDROGEN+PEROXIDE",
        "title": "HYDROGEN PEROXIDE 물질안전보건자료(MSDS)"
      }
    ],
    "general_resources": [
      {
        "title": "MSDS 통합검색 (안전보건공단)",
        "url": "https://msds.kosha.or.kr/",
        "description": "모든 화학물질의 물질안전보건자료(MSDS) 검색"
      },
      {
        "title": "화학물질 안전정보 (환경부)",
        "url": "https://ncis.nier.go.kr/",
        "description": "국가 화학물질 정보시스템"
      },
      {
        "title": "화학물질 배출이동량 정보",
        "url": "https://tri.me.go.kr/",
        "description": "화학물질 배출량 및 유해성 정보"
      }
    ]
  }
}
```

**Response Fields**:
- `success` (boolean): 전체 작업 성공 여부
- `rule_based_analysis` (object): CAMEO 기반 규칙 분석 결과
- `ai_summary_english` (string): AI가 생성한 영어 요약
- `ai_summary_korean` (string): Gemini가 번역한 친절한 한국어 요약
- `ai_status` (string): AI 처리 상태
  - `"success"`: AI 요약 성공
  - `"skipped"`: AI 요약 비활성화 (use_ai=false)
  - `"unavailable"`: AI API 미설정
  - `"error"`: AI 요약 실패
- `simple_response` (object): **백엔드 사용 권장 필드**
  - `risk_level` (string): "위험", "주의", "안전"
  - `message` (string): 사용자에게 보여줄 최종 메시지
- `safety_links` (object): **안전 정보 링크 (위험/주의 조합일 때만 제공)**
  - `specific_links` (array): 특정 화학물질 조합에 대한 사고예방 기사 및 안전지침
  - `msds_links` (array): 각 화학물질의 MSDS(물질안전보건자료) 검색 링크
  - `general_resources` (array): 공식 화학물질 안전정보 사이트 (KOSHA, 환경부 등)

---

## Quick Start

### 1. 간단한 테스트 (빠른 응답)
```bash
curl -X POST "https://nemo-jisanhak-6lu8.onrender.com/simple-analyze" \
  -H "Content-Type: application/json" \
  -d '{"substances": ["Bleach", "Ammonia"]}'
```

### 2. AI 요약 포함 (상세한 응답)
```bash
curl -X POST "https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze" \
  -H "Content-Type: application/json" \
  -d '{"substances": ["Bleach", "Ammonia"], "use_ai": true}'
```

---

## Integration Examples

### JavaScript (Fetch API)
```javascript
// 간단 분석
async function analyzeChemicals(substances) {
  const response = await fetch('https://nemo-jisanhak-6lu8.onrender.com/simple-analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ substances })
  });

  const data = await response.json();
  return data;
}

// AI 요약 포함
async function analyzeWithAI(substances) {
  const response = await fetch('https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      substances,
      use_ai: true
    })
  });

  const data = await response.json();

  // 백엔드에서 사용하기 쉬운 형식
  const { risk_level, message } = data.simple_response;

  console.log(`Risk Level: ${risk_level}`);
  console.log(`Message: ${message}`);

  return data;
}

// 사용 예시
analyzeWithAI(['Hydrogen Peroxide', 'Acetic Acid'])
  .then(result => {
    console.log('Analysis complete!');
    console.log(result.simple_response);
  });
```

### Python (Requests)
```python
import requests
import json

API_URL = "https://nemo-jisanhak-6lu8.onrender.com"

# 간단 분석
def simple_analyze(substances):
    response = requests.post(
        f"{API_URL}/simple-analyze",
        json={"substances": substances},
        timeout=120
    )
    return response.json()

# AI 요약 포함
def analyze_with_ai(substances):
    response = requests.post(
        f"{API_URL}/hybrid-analyze",
        json={
            "substances": substances,
            "use_ai": True
        },
        timeout=300  # AI 분석은 더 오래 걸림
    )

    data = response.json()

    # 백엔드에서 사용하기 쉬운 형식
    simple = data['simple_response']
    print(f"Risk Level: {simple['risk_level']}")
    print(f"Message: {simple['message']}")

    return data

# 사용 예시
result = analyze_with_ai(['Hydrogen Peroxide', 'Acetic Acid'])
print(json.dumps(result['simple_response'], indent=2, ensure_ascii=False))
```

### Java (Spring Boot)
```java
@Service
public class ChemicalAnalysisService {

    private static final String API_URL = "https://nemo-jisanhak-6lu8.onrender.com";
    private final RestTemplate restTemplate;

    public ChemicalAnalysisService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public AnalysisResponse analyzeWithAI(List<String> substances) {
        String url = API_URL + "/hybrid-analyze";

        Map<String, Object> request = new HashMap<>();
        request.put("substances", substances);
        request.put("use_ai", true);

        ResponseEntity<AnalysisResponse> response = restTemplate.postForEntity(
            url,
            request,
            AnalysisResponse.class
        );

        return response.getBody();
    }
}

// Response DTO
@Data
public class AnalysisResponse {
    private boolean success;
    private RuleBasedAnalysis ruleBasedAnalysis;
    private String aiSummaryKorean;
    private String aiStatus;
    private SimpleResponse simpleResponse;
}

@Data
public class SimpleResponse {
    private String riskLevel;  // "위험", "주의", "안전"
    private String message;
}
```

---

## Response Examples

### Case 1: 위험한 조합
**Request**: `["Bleach", "Ammonia"]`

**simple_response**:
```json
{
  "risk_level": "위험",
  "message": "안녕하세요! 화학 안전 도우미입니다. 😊\n\n확인 결과 1가지 위험 결과가 발견되었습니다!\n\n락스(표백제)와 암모니아가 만날 경우 유독가스가 발생하여 호흡곤란, 폐손상이 발생할 수 있어요.\n\n제가 분석하기로는 이 제품들을 섞어 쓰는 건 매우 위험하다고 판단됩니다."
}
```

### Case 2: 안전한 조합
**Request**: `["Water", "Salt"]`

**simple_response**:
```json
{
  "risk_level": "안전",
  "message": "안녕하세요! 화학 안전 도우미입니다. 😊\n\n좋은 소식입니다! 분석 결과 위험한 조합이 발견되지 않았어요.\n\n제가 분석하기로는 이 물질들을 함께 사용해도 안전하다고 판단됩니다."
}
```

---

## Error Handling

### 400 Bad Request
```json
{
  "detail": "At least 2 substances are required"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "CAMEO crawling failed: timeout"
}
```

### AI Error (부분 성공)
```json
{
  "success": true,
  "rule_based_analysis": {...},
  "ai_status": "error",
  "ai_summary_english": "AI summary unavailable: HTTP 404",
  "ai_summary_korean": null,
  "simple_response": {
    "risk_level": "위험",
    "message": "[위험] 1개의 위험한 조합이 발견되었습니다!"
  }
}
```
> Note: AI 요약이 실패해도 규칙 기반 분석 결과는 반환됩니다.

---

## Best Practices

### 1. 타임아웃 설정
- `/simple-analyze`: 최소 120초 (2분)
- `/hybrid-analyze`: 최소 300초 (5분)

### 2. 에러 처리
```javascript
try {
  const response = await fetch(url, options);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const data = await response.json();

  // AI 실패는 부분 성공
  if (data.success && data.ai_status === "error") {
    console.warn("AI summary failed, using rule-based only");
  }

  return data;
} catch (error) {
  console.error("Analysis failed:", error);
  // Fallback logic
}
```

### 3. 권장 사용 방법
프론트엔드에서는 `simple_response` 필드만 사용하세요:

```javascript
const result = await analyzeWithAI(substances);

// 이것만 사용하면 됨!
const { risk_level, message } = result.simple_response;

// UI에 표시
displayRiskLevel(risk_level);  // "위험", "주의", "안전"
displayMessage(message);        // 사용자 친화적인 한국어 메시지
```

---

## Performance

| Endpoint | Response Time | Accuracy | Use Case |
|----------|--------------|----------|----------|
| `/simple-analyze` | ~30-60초 | 100% (NOAA 검증) | 빠른 응답 필요 시 |
| `/hybrid-analyze` | ~2-4분 | 규칙 100% + AI 요약 | 상세한 설명 필요 시 |

### Cold Start
첫 요청은 서버 시작 시간으로 인해 30-60초 추가 소요될 수 있습니다.

---

## Rate Limits
현재 rate limit 없음 (추후 추가 예정)

---

## 📋 백엔드 개발자를 위한 체크리스트

### 필수 구현 사항
- [ ] API 엔드포인트: `POST /hybrid-analyze`
- [ ] Request Body: `{"substances": [...], "use_ai": true}`
- [ ] HTTP 타임아웃: **최소 300초 (5분)**
- [ ] Response 파싱: `response.simple_response.risk_level`, `response.simple_response.message`

### UI에 표시할 데이터
```javascript
// 1. 위험도 표시 (필수)
const riskLevel = response.simple_response.risk_level;
// "위험" -> 빨간색 경고
// "주의" -> 주황색 주의
// "안전" -> 초록색 안전

// 2. 메시지 표시 (필수)
const message = response.simple_response.message;
// 사용자 친화적인 한국어 설명

// 3. 안전 링크 표시 (선택)
const links = response.safety_links;
// MSDS 링크, 공식 자료 등
```

### 에러 처리
```javascript
// HTTP 500: 서버 에러 -> "일시적 오류입니다. 잠시 후 다시 시도해주세요"
// HTTP 400: 잘못된 요청 -> "최소 2개 이상의 물질을 입력해주세요"
// Timeout: "분석 시간이 초과되었습니다. 다시 시도해주세요"
```

### 테스트용 샘플 데이터
```json
// 위험한 조합
{"substances": ["Bleach", "Ammonia"]}

// 안전한 조합
{"substances": ["Water", "Salt"]}

// 복잡한 조합 (10개)
{"substances": ["Bleach", "Ammonia", "Vinegar", "Hydrogen Peroxide", "Rubbing Alcohol", "Baking Soda", "Sulfuric Acid", "Sodium Hydroxide", "Acetone", "Hydrochloric Acid"]}
```

---

## Support
- GitHub: https://github.com/lemonminyoung/Nemo-jisanhak
- Issues: https://github.com/lemonminyoung/Nemo-jisanhak/issues
- API 문서: 이 파일을 공유하세요!

---

## Changelog

### v2.1.0 (2025-01-06)
- `safety_links` 필드 추가 (MSDS, 공식 자료 링크)
- Gemini 프롬프트 개선 (중복 제거, 구체적 조건 명시)
- API 문서 개선 (백엔드 개발자용 가이드 추가)

### v2.0.0 (2025-01-06)
- Hugging Face Space 연동
- Gemini API 한국어 번역 추가
- `simple_response` 필드 추가
- AI 요약 성능 개선

### v1.0.0
- 초기 릴리즈
- CAMEO 크롤링
- 규칙 기반 분석
