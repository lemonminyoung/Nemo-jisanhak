# 백엔드 통합 가이드 (5분 완성)

## 📦 필요한 파일
이 3개 파일을 백엔드 담당자에게 공유하세요:
1. **API_DOCUMENTATION.md** - 전체 API 명세서
2. **BACKEND_INTEGRATION_GUIDE.md** - 이 파일 (빠른 통합 가이드)
3. **test_api_multiple.py** - 테스트 스크립트

---

## 🚀 1분 요약

### API 호출 방법
```javascript
fetch('https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    substances: ["Bleach", "Ammonia"],
    use_ai: true
  }),
  timeout: 300000  // 5분 (중요!)
})
.then(res => res.json())
.then(data => {
  // 이 2개 필드만 사용하세요!
  const riskLevel = data.simple_response.risk_level;  // "위험", "주의", "안전"
  const message = data.simple_response.message;        // 사용자에게 보여줄 메시지

  // 선택: 안전 링크도 표시 가능
  const links = data.safety_links;
});
```

---

## 📋 체크리스트

### 필수 사항
- [ ] API URL: `https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze`
- [ ] Method: `POST`
- [ ] Headers: `Content-Type: application/json`
- [ ] Timeout: **최소 300초 (5분)** ⚠️
- [ ] Request Body: `{"substances": [...], "use_ai": true}`

### 응답 처리
- [ ] `simple_response.risk_level` 파싱 → UI 색상 표시
  - "위험" → 🔴 빨간색
  - "주의" → 🟠 주황색
  - "안전" → 🟢 초록색
- [ ] `simple_response.message` 파싱 → 사용자에게 표시
- [ ] (선택) `safety_links` 파싱 → 추가 정보 링크

### 에러 처리
- [ ] HTTP 400 → "최소 2개 이상의 물질을 입력해주세요"
- [ ] HTTP 500 → "일시적 오류입니다. 잠시 후 다시 시도해주세요"
- [ ] Timeout → "분석 시간이 초과되었습니다. 다시 시도해주세요"

---

## 💻 언어별 샘플 코드

### JavaScript (React/Node.js)
```javascript
async function analyzeChemicals(substances) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5분

    const response = await fetch(
      'https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ substances, use_ai: true }),
        signal: controller.signal
      }
    );

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    return {
      riskLevel: data.simple_response.risk_level,
      message: data.simple_response.message,
      links: data.safety_links
    };
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('분석 시간이 초과되었습니다');
    }
    throw error;
  }
}

// 사용 예시
analyzeChemicals(['Bleach', 'Ammonia'])
  .then(result => {
    console.log('위험도:', result.riskLevel);
    console.log('메시지:', result.message);
  })
  .catch(error => {
    console.error('에러:', error.message);
  });
```

### Python (FastAPI/Flask)
```python
import requests

def analyze_chemicals(substances):
    url = "https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze"

    try:
        response = requests.post(
            url,
            json={"substances": substances, "use_ai": True},
            timeout=300  # 5분
        )
        response.raise_for_status()

        data = response.json()
        return {
            "risk_level": data["simple_response"]["risk_level"],
            "message": data["simple_response"]["message"],
            "links": data.get("safety_links", {})
        }
    except requests.exceptions.Timeout:
        raise Exception("분석 시간이 초과되었습니다")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception("최소 2개 이상의 물질을 입력해주세요")
        else:
            raise Exception("일시적 오류입니다. 잠시 후 다시 시도해주세요")

# 사용 예시
result = analyze_chemicals(['Bleach', 'Ammonia'])
print(f"위험도: {result['risk_level']}")
print(f"메시지: {result['message']}")
```

### Java (Spring Boot)
```java
@Service
public class ChemicalAnalysisService {

    private final RestTemplate restTemplate;
    private static final String API_URL = "https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze";

    public ChemicalAnalysisService() {
        this.restTemplate = new RestTemplate();
        // 타임아웃 설정
        HttpComponentsClientHttpRequestFactory factory = new HttpComponentsClientHttpRequestFactory();
        factory.setConnectTimeout(300000);
        factory.setReadTimeout(300000);
        this.restTemplate.setRequestFactory(factory);
    }

    public AnalysisResult analyzeChemicals(List<String> substances) {
        Map<String, Object> request = new HashMap<>();
        request.put("substances", substances);
        request.put("use_ai", true);

        ResponseEntity<ApiResponse> response = restTemplate.postForEntity(
            API_URL,
            request,
            ApiResponse.class
        );

        ApiResponse apiResponse = response.getBody();
        return new AnalysisResult(
            apiResponse.getSimpleResponse().getRiskLevel(),
            apiResponse.getSimpleResponse().getMessage(),
            apiResponse.getSafetyLinks()
        );
    }
}
```

---

## 🧪 테스트 방법

### 1. Postman으로 테스트
```
POST https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze
Headers: Content-Type: application/json
Body (raw JSON):
{
  "substances": ["Bleach", "Ammonia"],
  "use_ai": true
}
```

### 2. cURL로 테스트
```bash
curl -X POST "https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze" \
  -H "Content-Type: application/json" \
  -d '{"substances": ["Bleach", "Ammonia"], "use_ai": true}' \
  --max-time 300
```

### 3. Python 테스트 스크립트 실행
```bash
python test_api_multiple.py
```
→ 선택: `2` (Hybrid Analyze)
→ 테스트 개수: `3`

---

## 📊 응답 예시

### 위험한 조합
```json
{
  "simple_response": {
    "risk_level": "위험",
    "message": "안녕하세요! 화학 안전 도우미입니다. 😊\n\n확인 결과 1가지 위험한 조합이 발견되었습니다!\n\n락스(표백제)와 암모니아가 만나면 유독가스가 발생하여 호흡곤란, 폐손상이 발생할 수 있어요..."
  },
  "safety_links": {
    "specific_links": [
      {
        "title": "락스와 암모니아 혼합 사고 예방",
        "url": "https://www.kosha.or.kr/kosha/data/musafetydata.do?mode=view&articleNo=430945",
        "source": "안전보건공단"
      }
    ],
    "msds_links": [...],
    "general_resources": [...]
  }
}
```

### 안전한 조합
```json
{
  "simple_response": {
    "risk_level": "안전",
    "message": "안녕하세요! 화학 안전 도우미입니다. 😊\n\n좋은 소식입니다! 분석 결과 위험한 조합이 발견되지 않았어요..."
  },
  "safety_links": {
    "specific_links": [],
    "msds_links": [...],
    "general_resources": [...]
  }
}
```

---

## ⚠️ 주의사항

### 1. 타임아웃 설정 필수!
- API 응답 시간: 2-4분 (AI 분석 포함)
- Cold start: 첫 요청 시 30-60초 추가
- **반드시 300초(5분) 이상으로 설정**

### 2. 응답 필드 선택
- ✅ 사용: `simple_response`, `safety_links`
- ❌ 무시: `rule_based_analysis`, `ai_summary_english` (내부용)

### 3. 에러 핸들링
- AI가 실패해도 `simple_response`는 항상 제공됨
- 네트워크 에러는 재시도 로직 추가 권장

---

## 🔗 추가 자료
- **전체 API 명세서**: `API_DOCUMENTATION.md` 참고
- **GitHub**: https://github.com/lemonminyoung/Nemo-jisanhak
- **이슈 리포팅**: https://github.com/lemonminyoung/Nemo-jisanhak/issues

---

## ✅ 완료 체크
통합이 완료되면 아래를 확인하세요:
- [ ] 위험한 조합 테스트 (Bleach + Ammonia) → "위험" 표시 확인
- [ ] 안전한 조합 테스트 (Water + Salt) → "안전" 표시 확인
- [ ] 타임아웃 에러 핸들링 확인
- [ ] UI에 위험도 색상 표시 확인
- [ ] 메시지 한국어 출력 확인

---

**문의사항이 있으면 GitHub Issues에 남겨주세요!**
