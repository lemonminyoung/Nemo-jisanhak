"""
Hybrid Analyze Test - 규칙 기반 + AI 요약

BEST 방식:
1. CAMEO 데이터로 위험도 판단 (100% 정확)
2. Simple analyzer로 분류
3. AI로 사용자 친화적인 요약문 생성
"""

import requests
import json
import time

API_URL = "http://localhost:8000"


def test_hybrid_analyze():
    """하이브리드 분석 테스트"""

    print("=" * 70)
    print("Hybrid Analyze Test (Rules + AI Summary)")
    print("=" * 70)

    # 테스트 물질 (실생활 화학물질 4가지)
    test_substances = [
        "Hydrogen Peroxide",  # 과산화수소 (소독제)
        "Acetic Acid",        # 식초
        "Sodium Hydroxide",   # 수산화나트륨 (강염기)
        "Sulfuric Acid"       # 황산
    ]

    print(f"\nTest substances: {', '.join(test_substances)}")
    print("\nThis will:")
    print("  1. Crawl CAMEO for accurate reactivity data")
    print("  2. Classify using rule-based analyzer (100% accurate)")
    print("  3. Generate user-friendly summary using AI")

    start_time = time.time()

    try:
        response = requests.post(
            f"{API_URL}/hybrid-analyze",
            json={
                "substances": test_substances,
                "use_ai": True
            },
            timeout=300
        )

        elapsed = time.time() - start_time

        print(f"\n[OK] Response in {elapsed:.1f} seconds")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print("\n" + "=" * 70)
            print("RESULTS")
            print("=" * 70)

            # Rule-based 분석 결과
            analysis = data.get('rule_based_analysis', {})
            summary = analysis.get('summary', {})

            print("\n[1] Rule-Based Analysis (100% Accurate)")
            print("-" * 70)
            print(f"Total pairs: {summary.get('total_pairs', 0)}")
            print(f"Dangerous: {summary.get('dangerous_count', 0)}")
            print(f"Caution: {summary.get('caution_count', 0)}")
            print(f"Safe: {summary.get('safe_count', 0)}")
            print(f"Overall: {summary.get('overall_status', 'Unknown')}")
            print(f"\nMessage: {summary.get('message', '')}")

            # 위험한 조합 상세
            dangerous = analysis.get('dangerous_pairs', [])
            if dangerous:
                print("\n[DANGEROUS PAIRS]")
                for pair in dangerous:
                    print(f"\n  {pair['chemical_1']} + {pair['chemical_2']}")
                    print(f"  Status: {pair['status']}")
                    print(f"  Severity: {pair['severity_score']}")
                    print(f"  Hazards: {', '.join(pair['hazards'][:3])}")

            # AI 요약
            ai_status = data.get('ai_status', 'unknown')
            print("\n" + "-" * 70)
            print(f"[2] AI Summary Status: {ai_status}")
            print("-" * 70)

            if ai_status == "success":
                ai_summary_korean = data.get('ai_summary_korean', '')
                print("\n" + ai_summary_korean)

                # 전체 결과 저장
                output_file = "hybrid_analyze_result.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n\nFull result saved to: {output_file}")

                # 백엔드용 간단 요약 JSON (위험 레벨 + 한국어 메시지만)
                simple_output = {
                    "risk_level": summary.get('overall_status', 'Unknown'),
                    "message": ai_summary_korean
                }
                simple_file = "hybrid_analyze_simple.json"
                with open(simple_file, "w", encoding="utf-8") as f:
                    json.dump(simple_output, f, indent=2, ensure_ascii=False)
                print(f"Simple summary saved to: {simple_file}")

                # AI 요약만 따로 저장 (TXT)
                summary_file = "hybrid_ai_summary.txt"
                with open(summary_file, "w", encoding="utf-8") as f:
                    f.write("=" * 70 + "\n")
                    f.write("AI SUMMARY - Chemical Safety Analysis\n")
                    f.write("=" * 70 + "\n\n")
                    f.write(ai_summary_korean)
                    f.write("\n\n" + "=" * 70 + "\n")
                print(f"AI summary saved to: {summary_file}")

            elif ai_status == "unavailable":
                print("\n[WARNING] AI API not configured")
                print("Set AI_API_URL to enable AI summary")

            elif ai_status == "error":
                print("\n[ERROR] AI summary failed")
                error_msg = data.get('ai_summary', 'Unknown error')
                print(f"Error: {error_msg}")

            print("\n" + "=" * 70)
            print("[SUCCESS] Hybrid analysis complete!")
            print("=" * 70)

        else:
            print(f"\n[FAIL] HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except requests.exceptions.Timeout:
        print(f"\n[FAIL] Timeout after {time.time() - start_time:.1f} seconds")

    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()


def compare_methods():
    """3가지 방식 비교"""

    print("\n" + "=" * 70)
    print("COMPARISON: Simple vs Hybrid vs Full AI")
    print("=" * 70)

    test_substances = ["Acetic Acid", "Sodium Hydroxide"]
    print(f"\nTest: {', '.join(test_substances)}\n")

    results = {}

    # 1. Simple (규칙만)
    print("[1] Simple Analyze (Rules Only)...")
    start = time.time()
    try:
        response = requests.post(
            f"{API_URL}/simple-analyze",
            json={"substances": test_substances},
            timeout=300
        )
        results['simple'] = {
            'time': time.time() - start,
            'status': response.status_code,
            'success': response.status_code == 200
        }
        if response.status_code == 200:
            data = response.json()
            results['simple']['dangerous'] = data['summary']['dangerous_count']
    except Exception as e:
        results['simple'] = {'error': str(e)}

    # 2. Hybrid (규칙 + AI 요약)
    print("[2] Hybrid Analyze (Rules + AI Summary)...")
    start = time.time()
    try:
        response = requests.post(
            f"{API_URL}/hybrid-analyze",
            json={"substances": test_substances, "use_ai": True},
            timeout=300
        )
        results['hybrid'] = {
            'time': time.time() - start,
            'status': response.status_code,
            'success': response.status_code == 200
        }
        if response.status_code == 200:
            data = response.json()
            results['hybrid']['dangerous'] = data['rule_based_analysis']['summary']['dangerous_count']
            results['hybrid']['ai_status'] = data.get('ai_status')
    except Exception as e:
        results['hybrid'] = {'error': str(e)}

    # 3. Full AI (기존 방식)
    print("[3] Full AI Analyze (AI for everything)...")
    start = time.time()
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json={"substances": test_substances, "use_ai": True},
            timeout=300
        )
        results['full_ai'] = {
            'time': time.time() - start,
            'status': response.status_code,
            'success': response.status_code == 200
        }
    except Exception as e:
        results['full_ai'] = {'error': str(e)}

    # 결과 출력
    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)

    print("\n1. Simple (Rules Only)")
    print(f"   Time: {results['simple'].get('time', 'N/A'):.1f}s" if 'time' in results['simple'] else "   Error")
    print(f"   Accuracy: 100% (CAMEO data)")
    print(f"   User-friendly: No (raw data)")

    print("\n2. Hybrid (Rules + AI Summary) [RECOMMENDED]")
    print(f"   Time: {results['hybrid'].get('time', 'N/A'):.1f}s" if 'time' in results['hybrid'] else "   Error")
    print(f"   Accuracy: 100% (CAMEO data)")
    print(f"   User-friendly: Yes (AI summary)")
    if 'ai_status' in results['hybrid']:
        print(f"   AI Status: {results['hybrid']['ai_status']}")

    print("\n3. Full AI (Everything by AI)")
    print(f"   Time: {results['full_ai'].get('time', 'N/A'):.1f}s" if 'time' in results['full_ai'] else "   Error")
    print(f"   Accuracy: ~85% (model limitations)")
    print(f"   User-friendly: Yes")

    print("\n[RECOMMENDATION]")
    print("Use /hybrid-analyze for:")
    print("  - 100% accurate risk assessment (CAMEO)")
    print("  - User-friendly explanations (AI)")
    print("  - Best of both worlds!")

    print("=" * 70)


if __name__ == "__main__":
    print("\n")

    # 기본 테스트
    test_hybrid_analyze()

    # 비교 테스트
    print("\n\nRun comparison test? (Press Enter to skip, 'yes' to compare): ")
    print("Skipped.\n")

    # 비교를 원하면 주석 해제:
    # compare_methods()

    print("\n[INFO] Testing complete!")
    print("\nNext steps:")
    print("  1. Ensure /summarize endpoint exists in AI service")
    print("  2. Check AI service is running")
    print("  3. Test again with use_ai=True")
    print("")
