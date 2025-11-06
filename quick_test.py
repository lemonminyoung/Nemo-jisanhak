"""
빠른 API 테스트
Render URL만 입력하면 됩니다!
"""
import requests
import json

# Render URL
RENDER_URL = "https://chemical-analyzer-api.onrender.com"

print(f"\n🧪 Testing API: {RENDER_URL}")
print("=" * 70)

# Test 1: Health Check
print("\n[1] Health Check...")
try:
    response = requests.get(f"{RENDER_URL}/", timeout=10)
    print(f"✅ {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 2: Simple Analyze (2개 물질)
print("\n[2] Simple Analyze (Hydrogen Peroxide + Acetic Acid)...")
print("⏳ 크롤링 중... (30초~1분 소요)")

try:
    response = requests.post(
        f"{RENDER_URL}/simple-analyze",
        json={"substances": ["Hydrogen Peroxide", "Acetic Acid"]},
        timeout=120
    )

    if response.status_code == 200:
        data = response.json()
        summary = data['summary']
        print(f"\n✅ 분석 완료!")
        print(f"   전체 쌍: {summary['total_pairs']}")
        print(f"   위험: {summary['dangerous_count']}")
        print(f"   상태: {summary['overall_status']}")
        print(f"   메시지: {summary['message'][:100]}...")
    else:
        print(f"❌ Error {response.status_code}: {response.text[:200]}")

except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Hybrid Analyze (AI 요약 포함)
print("\n[3] Hybrid Analyze (규칙 + AI 요약)...")
print("⚠️  이 테스트는 AI API가 실행 중이어야 합니다!")
print("⏳ 분석 중... (1~3분 소요)")

try:
    response = requests.post(
        f"{RENDER_URL}/hybrid-analyze",
        json={
            "substances": ["Hydrogen Peroxide", "Acetic Acid"],
            "use_ai": True
        },
        timeout=300
    )

    if response.status_code == 200:
        data = response.json()

        # 규칙 기반 분석
        summary = data['rule_based_analysis']['summary']
        print(f"\n✅ 규칙 분석 완료!")
        print(f"   위험도: {summary['overall_status']}")
        print(f"   위험한 조합: {summary['dangerous_count']}개")

        # AI 요약
        ai_status = data['ai_status']
        print(f"\n🤖 AI 요약 상태: {ai_status}")

        if ai_status == "success":
            ai_message = data['ai_summary_korean']
            print(f"\n📝 한국어 요약:")
            print(f"{ai_message}")

            # 백엔드용 간단 JSON
            simple = {
                "risk_level": summary['overall_status'],
                "message": ai_message
            }

            with open("api_result.json", "w", encoding="utf-8") as f:
                json.dump(simple, f, indent=2, ensure_ascii=False)

            print(f"\n💾 결과 저장됨: api_result.json")
            print("\n✨ 모든 테스트 성공!")

        elif ai_status == "unavailable":
            print("⚠️  AI API가 설정되지 않았거나 실행 중이 아닙니다")
            print("   - Hugging Face Spaces 실행 확인")
            print("   - AI_API_URL 환경 변수 확인")

        else:
            print(f"❌ AI 오류: {data.get('ai_summary', 'Unknown')}")
    else:
        print(f"❌ Error {response.status_code}: {response.text[:200]}")

except requests.exceptions.Timeout:
    print("❌ 타임아웃! API 응답이 너무 오래 걸립니다.")
    print("   (첫 요청은 cold start로 인해 느릴 수 있습니다)")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("테스트 완료!")
print("=" * 70)
