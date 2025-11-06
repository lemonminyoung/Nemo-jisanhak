# UptimeRobot 설정 가이드

Hugging Face Space와 Render API를 항상 깨어있게 유지하여 Cold Start를 방지합니다.

---

## 🎯 목적

### 문제점
- **Hugging Face Space**: 15분 미사용 시 sleep → 첫 요청에 2-3분 소요 (cold start)
- **Render 무료 플랜**: 15분 미사용 시 sleep → 첫 요청에 30-60초 소요

### 해결책
- UptimeRobot으로 5분마다 핑 전송
- 항상 깨어있는 상태 유지
- Cold start 제거 → **응답 시간 대폭 단축!**

---

## 📝 UptimeRobot 설정

### 1. UptimeRobot 가입
1. https://uptimerobot.com 접속
2. 무료 계정 생성 (최대 50개 모니터 무료)

---

### 2. Hugging Face Space 모니터 추가

**Monitor #1: Hugging Face Space**

| 설정 항목 | 값 |
|----------|---|
| **Monitor Type** | HTTP(s) |
| **Friendly Name** | Chemical AI - Hugging Face |
| **URL** | `https://gimchabssal-chemical-ai.hf.space/` |
| **Monitoring Interval** | 5 minutes |
| **Monitor Timeout** | 30 seconds |
| **HTTP Method** | GET (기본값) |

**설정 방법:**
1. Dashboard → Add New Monitor 클릭
2. Monitor Type: "HTTP(s)" 선택
3. Friendly Name: "Chemical AI - Hugging Face" 입력
4. URL: `https://gimchabssal-chemical-ai.hf.space/` 입력
5. Monitoring Interval: "5 minutes" 선택
6. HTTP Method: GET (기본값 그대로)
7. Create Monitor 클릭

> **참고**: GET 요청만으로도 Hugging Face Space가 깨어나고 활성 상태를 유지합니다.

---

### 3. Render API 모니터 추가

**Monitor #2: Render Backend API**

| 설정 항목 | 값 |
|----------|---|
| **Monitor Type** | HTTP(s) |
| **Friendly Name** | Chemical Safety API - Render |
| **URL** | `https://nemo-jisanhak-6lu8.onrender.com/` |
| **Monitoring Interval** | 5 minutes |
| **Monitor Timeout** | 30 seconds |
| **HTTP Method** | GET |

**설정 방법:**
1. Dashboard → Add New Monitor 클릭
2. Monitor Type: "HTTP(s)" 선택
3. Friendly Name: "Chemical Safety API - Render" 입력
4. URL: `https://nemo-jisanhak-6lu8.onrender.com/` 입력
5. Monitoring Interval: "5 minutes" 선택
6. HTTP Method: GET (기본값)
7. Create Monitor 클릭

---

## ✅ 설정 확인

### 모니터 상태 확인
1. UptimeRobot Dashboard 접속
2. 두 모니터가 "Up" 상태인지 확인
3. Response Time이 정상 범위인지 확인:
   - Hugging Face: 5-15초 (정상)
   - Render: 1-3초 (정상)

### 효과 테스트
**Before (UptimeRobot 없이):**
```bash
# 15분 후 첫 요청
curl -X POST "https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze" \
  -H "Content-Type: application/json" \
  -d '{"substances": ["Bleach", "Ammonia"], "use_ai": true}'
# 응답 시간: 2-3분 (cold start)
```

**After (UptimeRobot 설정 후):**
```bash
# 언제든지 요청
curl -X POST "https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze" \
  -H "Content-Type: application/json" \
  -d '{"substances": ["Bleach", "Ammonia"], "use_ai": true}'
# 응답 시간: 30-60초 (warm start)
```

---

## 📊 예상 성능 개선

| 구분 | Before | After | 개선 |
|------|--------|-------|------|
| **Render API (첫 요청)** | 60-90초 | 30-60초 | 30초 단축 |
| **Hugging Face (첫 요청)** | 180-240초 | 30-60초 | **2분 단축!** |
| **전체 응답 시간** | 3-4분 | 1-2분 | **50% 단축!** |

---

## 🔔 알림 설정 (선택사항)

서비스가 다운되면 알림을 받을 수 있습니다:

1. UptimeRobot Dashboard → Alert Contacts 메뉴
2. Add Alert Contact 클릭
3. 이메일, SMS, Slack 등 선택
4. 각 모니터에 Alert Contact 연결

---

## 💰 비용

**무료 플랜:**
- 모니터: 최대 50개
- 체크 간격: 5분
- 알림: 이메일, SMS, Slack 등
- **완전 무료!**

**유료 플랜 (필요시):**
- 1분 간격 체크: $7/월
- 더 많은 모니터: $7/월

현재 설정(5분 간격)으로는 **무료 플랜으로 충분**합니다.

---

## 🛠️ 트러블슈팅

### 문제 1: Hugging Face 모니터가 계속 "Down" 상태
**원인**: HTTP Method가 잘못 설정되었거나 타임아웃
**해결**:
1. HTTP Method가 **GET**으로 설정되어 있는지 확인
2. URL이 정확한지 확인: `https://gimchabssal-chemical-ai.hf.space/`
3. Monitor Timeout을 60초로 늘려보기 (Hugging Face는 응답이 느릴 수 있음)

### 문제 2: Response Time이 너무 길어요
**원인**: Cold start가 여전히 발생
**해결**:
1. Monitoring Interval을 3분으로 줄이기 (무료 플랜 최소값)
2. Hugging Face Space 로그 확인

### 문제 3: 여전히 느려요
**추가 해결책**:
1. Hugging Face Space "Persistent Storage" 옵션 확인
2. Render 유료 플랜 고려 ($7/월 - 항상 켜짐)
3. CAMEO 크롤링 결과 캐싱 추가

---

## 📈 모니터링 대시보드

UptimeRobot 대시보드에서 확인할 수 있는 정보:
- ✅ **Uptime %**: 가동률 (목표: 99.9% 이상)
- ⏱️ **Response Time**: 응답 시간 추이
- 📊 **Response Time Graph**: 24시간/7일/30일 그래프
- 🚨 **Down Events**: 다운 이력

---

## ✨ 완료!

설정이 완료되면:
1. 5분마다 자동으로 서비스 체크
2. Cold start 방지
3. 빠른 응답 시간
4. 다운 시 즉시 알림

**이제 API 응답이 훨씬 빨라질 거예요!** 🚀

---

## 📞 문의

UptimeRobot 설정 관련 문의:
- GitHub Issues: https://github.com/lemonminyoung/Nemo-jisanhak/issues
