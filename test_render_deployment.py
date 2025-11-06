"""
Render 배포 API 테스트
"""
import requests
import json
import time

# ⚠️ 여기에 Render URL을 입력하세요!
RENDER_URL = "https://your-app.onrender.com"  # 이 부분을 수정하세요!

def test_health():
    """헬스 체크 (서버가 살아있는지 확인)"""
    print("=" * 70)
    print("[1] Health Check Test")
    print("=" * 70)

    try:
        response = requests.get(f"{RENDER_URL}/", timeout=30)
        print(f"✅ Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_simple_analyze():
    """간단한 분석 테스트 (2개 물질)"""
    print("\n" + "=" * 70)
    print("[2] Simple Analyze Test (2 substances)")
    print("=" * 70)

    substances = ["Hydrogen Peroxide", "Acetic Acid"]
    print(f"Testing with: {substances}")

    start = time.time()

    try:
        response = requests.post(
            f"{RENDER_URL}/simple-analyze",
            json={"substances": substances},
            timeout=120  # 2분 타임아웃
        )

        elapsed = time.time() - start
        print(f"\n✅ Status: {response.status_code}")
        print(f"⏱️  Time: {elapsed:.1f} seconds")

        if response.status_code == 200:
            data = response.json()
            summary = data.get('summary', {})
            print(f"\n📊 Results:")
            print(f"  Total pairs: {summary.get('total_pairs')}")
            print(f"  Dangerous: {summary.get('dangerous_count')}")
            print(f"  Overall: {summary.get('overall_status')}")
            print(f"  Message: {summary.get('message', '')[:100]}...")
            return True
        else:
            print(f"❌ Error: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_hybrid_analyze():
    """하이브리드 분석 테스트 (규칙 + AI)"""
    print("\n" + "=" * 70)
    print("[3] Hybrid Analyze Test (Rules + AI)")
    print("=" * 70)

    substances = ["Hydrogen Peroxide", "Acetic Acid"]
    print(f"Testing with: {substances}")
    print("⚠️  This requires AI API to be running!")

    start = time.time()

    try:
        response = requests.post(
            f"{RENDER_URL}/hybrid-analyze",
            json={
                "substances": substances,
                "use_ai": True
            },
            timeout=300  # 5분 타임아웃 (크롤링 + AI 분석)
        )

        elapsed = time.time() - start
        print(f"\n✅ Status: {response.status_code}")
        print(f"⏱️  Time: {elapsed:.1f} seconds")

        if response.status_code == 200:
            data = response.json()

            # Rule-based 결과
            analysis = data.get('rule_based_analysis', {})
            summary = analysis.get('summary', {})
            print(f"\n📊 Rule-Based Results:")
            print(f"  Overall: {summary.get('overall_status')}")
            print(f"  Dangerous: {summary.get('dangerous_count')}")

            # AI 요약
            ai_status = data.get('ai_status', 'unknown')
            print(f"\n🤖 AI Summary Status: {ai_status}")

            if ai_status == "success":
                ai_summary = data.get('ai_summary_korean', '')
                print(f"\n한국어 요약:")
                print(f"{ai_summary[:200]}...")

                # 간단한 JSON 저장
                simple_output = {
                    "risk_level": summary.get('overall_status'),
                    "message": ai_summary
                }

                with open("render_test_result.json", "w", encoding="utf-8") as f:
                    json.dump(simple_output, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Saved to: render_test_result.json")

            elif ai_status == "unavailable":
                print("⚠️  AI API not configured or not running")
            elif ai_status == "error":
                print(f"❌ AI Error: {data.get('ai_summary', 'Unknown')}")

            return ai_status == "success"
        else:
            print(f"❌ Error: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ Timeout after {time.time() - start:.1f} seconds")
        print("   API took too long to respond. This might be normal on first request (cold start)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n")
    print("🚀 Render Deployment Test")
    print("=" * 70)
    print(f"Target URL: {RENDER_URL}")
    print("=" * 70)

    # URL 확인
    if "your-app" in RENDER_URL:
        print("\n❌ ERROR: Please update RENDER_URL with your actual Render URL!")
        print("   1. Open this file in an editor")
        print("   2. Change RENDER_URL to your Render service URL")
        print("   3. Run this script again")
        exit(1)

    # 테스트 실행
    results = []

    # Test 1: Health Check
    results.append(("Health Check", test_health()))

    # Test 2: Simple Analyze
    results.append(("Simple Analyze", test_simple_analyze()))

    # Test 3: Hybrid Analyze (requires AI API)
    print("\n⚠️  Next test requires AI API to be running!")
    print("Press Enter to continue, or Ctrl+C to skip...")
    try:
        input()
        results.append(("Hybrid Analyze", test_hybrid_analyze()))
    except KeyboardInterrupt:
        print("\nSkipped Hybrid Analyze test")
        results.append(("Hybrid Analyze", None))

    # 결과 요약
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        print(f"{status}  {name}")

    print("\n✨ Testing complete!")
    print("\nNext steps:")
    print("  1. If tests passed, your API is ready!")
    print("  2. Share the Render URL with your backend team")
    print("  3. They can use POST /hybrid-analyze endpoint")
    print("")
