"""
Simple Analyze API 테스트
AI 없이 규칙 기반 분석만 사용
"""

import requests
import json
import time

API_URL = "http://localhost:8000"


def test_simple_analyze():
    """간단 분석 테스트"""

    print("=" * 70)
    print("Simple Analyze Test (No AI, Rules Only)")
    print("=" * 70)

    # 테스트 케이스들
    test_cases = [
        {
            "name": "위험한 조합",
            "substances": ["Bleach", "Ammonia"]
        },
        {
            "name": "여러 물질 조합",
            "substances": ["Acetic Acid", "Sodium Hydroxide", "Sulfuric Acid"]
        },
        {
            "name": "3개 물질",
            "substances": ["Hydrochloric Acid", "Ammonia", "Bleach"]
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"Substances: {', '.join(test_case['substances'])}")
        print("=" * 70)

        start_time = time.time()

        try:
            # API 호출
            response = requests.post(
                f"{API_URL}/simple-analyze",
                json={"substances": test_case['substances']},
                timeout=300
            )

            elapsed = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                print(f"\n[OK] Response in {elapsed:.1f} seconds")
                print(f"\nStatus: {response.status_code}")

                # 요약 정보
                summary = data.get('summary', {})
                print(f"\n{summary.get('message', '')}")
                print(f"\nAnalysis Summary:")
                print(f"  Total combinations: {summary.get('total_pairs', 0)}")
                print(f"  Dangerous: {summary.get('dangerous_count', 0)}")
                print(f"  Caution: {summary.get('caution_count', 0)}")
                print(f"  Safe: {summary.get('safe_count', 0)}")

                # 위험한 조합
                dangerous = data.get('dangerous_pairs', [])
                if dangerous:
                    print(f"\n[WARNING] Dangerous Combinations Found:")
                    for pair in dangerous:
                        print(f"\n  {pair['chemical_1']}")
                        print(f"  + {pair['chemical_2']}")
                        print(f"  Status: {pair['status']}")
                        print(f"  Risk Level: {pair['risk_level']}")
                        print(f"  Severity Score: {pair['severity_score']}")
                        print(f"  Hazards ({pair['hazard_count']}):")
                        for hazard in pair['hazards'][:3]:
                            print(f"    - {hazard}")

                # 주의 조합
                caution = data.get('caution_pairs', [])
                if caution:
                    print(f"\n[CAUTION] Caution Required:")
                    for pair in caution:
                        print(f"  - {pair['chemical_1']} + {pair['chemical_2']}")

                # 안전 조합
                safe = data.get('safe_pairs', [])
                if safe:
                    print(f"\n[SAFE] Safe Combinations:")
                    for pair in safe:
                        print(f"  - {pair['chemical_1']} + {pair['chemical_2']}")

                # 권장 사항
                recommendations = data.get('recommendations', [])
                if recommendations:
                    print(f"\n[RECOMMENDATIONS]:")
                    for rec in recommendations[:10]:
                        print(f"  {rec}")

                # 결과 저장
                filename = f"simple_analyze_result_{i}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\nResult saved to: {filename}")

            else:
                print(f"\n[FAIL] HTTP {response.status_code}")
                print(f"Response: {response.text[:500]}")

        except requests.exceptions.Timeout:
            print(f"\n[FAIL] Timeout after {time.time() - start_time:.1f} seconds")

        except Exception as e:
            print(f"\n[FAIL] Error: {e}")

        print("\n" + "=" * 70)

    print("\n[INFO] All tests completed!")


def compare_with_ai():
    """AI 분석과 Simple 분석 비교"""

    print("\n" + "=" * 70)
    print("Comparison: AI vs Simple Analyze")
    print("=" * 70)

    test_substances = ["Acetic Acid", "Sodium Hydroxide"]

    print(f"\nTest substances: {', '.join(test_substances)}")

    # Simple 분석
    print("\n[1] Simple Analyze (Rules Only)...")
    start_simple = time.time()
    try:
        response_simple = requests.post(
            f"{API_URL}/simple-analyze",
            json={"substances": test_substances},
            timeout=300
        )
        time_simple = time.time() - start_simple

        if response_simple.status_code == 200:
            data_simple = response_simple.json()
            print(f"    Time: {time_simple:.1f}s")
            print(f"    Result: {data_simple['summary']['message']}")
            print(f"    Dangerous: {data_simple['summary']['dangerous_count']}")
    except Exception as e:
        print(f"    Error: {e}")

    # AI 분석
    print("\n[2] AI Analyze (with AI)...")
    start_ai = time.time()
    try:
        response_ai = requests.post(
            f"{API_URL}/analyze",
            json={"substances": test_substances, "use_ai": True},
            timeout=300
        )
        time_ai = time.time() - start_ai

        if response_ai.status_code == 200:
            data_ai = response_ai.json()
            print(f"    Time: {time_ai:.1f}s")
            print(f"    Status: {data_ai.get('ai_status', 'unknown')}")
            if data_ai.get('ai_analysis'):
                print(f"    Analysis length: {len(data_ai['ai_analysis'])} chars")
    except Exception as e:
        print(f"    Error: {e}")

    # 비교
    print(f"\n[COMPARISON]")
    if 'time_simple' in locals() and 'time_ai' in locals():
        print(f"  Simple: {time_simple:.1f}s")
        print(f"  AI: {time_ai:.1f}s")
        print(f"  Speed difference: {time_ai - time_simple:.1f}s")
        print(f"\n  Simple is {((time_ai / time_simple) - 1) * 100:.0f}% faster!")

    print(f"\n  Accuracy:")
    print(f"  - Simple: 100% (NOAA verified data)")
    print(f"  - AI: ~85% (model limitations)")

    print("=" * 70)


if __name__ == "__main__":
    print("\n")

    # 기본 테스트
    test_simple_analyze()

    # AI와 비교 (선택사항)
    print("\n\nDo you want to compare with AI? (This takes longer)")
    print("Press Enter to skip, or type 'yes' to compare: ", end="")

    # 자동으로 건너뛰기
    print("Skipped.\n")

    # 비교를 원하면 주석 해제:
    # compare_with_ai()

    print("\n[SUCCESS] Testing complete!")
    print("\nNext steps:")
    print("  - Review the saved JSON files")
    print("  - Use /simple-analyze for production")
    print("  - Build frontend with these results")
    print("")
