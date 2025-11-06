"""
Full API Test - CAMEO crawling + AI analysis
"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def test_full_pipeline():
    """전체 파이프라인 테스트"""

    print("=" * 70)
    print("Full API Test - CAMEO + AI")
    print("=" * 70)

    # 테스트 데이터
    test_substances = ["Acetic Acid", "Sodium Hydroxide"]

    print(f"\nTesting substances: {', '.join(test_substances)}")
    print(f"Expected pairs: 1 (Acetic Acid + Sodium Hydroxide)")

    # API 요청
    print("\n[1] Sending request to /analyze endpoint...")
    print("    This will:")
    print("    - Crawl CAMEO website for reactivity data")
    print("    - Send data to AI service for analysis")
    print("    - Return comprehensive safety report")

    start_time = time.time()

    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json={
                "substances": test_substances,
                "use_ai": True
            },
            timeout=300  # 5 minutes timeout
        )

        elapsed = time.time() - start_time

        print(f"\n[2] Response received in {elapsed:.1f} seconds")
        print(f"    Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print("\n[OK] Success!")
            print(f"\n    CAMEO Results: {len(data.get('cameo_results', []))} pairs found")

            # CAMEO 결과 출력
            if data.get('cameo_results'):
                for i, pair in enumerate(data['cameo_results'], 1):
                    print(f"\n    Pair {i}:")
                    print(f"      Chemical 1: {pair.get('chemical_1', 'N/A')}")
                    print(f"      Chemical 2: {pair.get('chemical_2', 'N/A')}")
                    print(f"      Status: {pair.get('status', 'N/A')}")
                    print(f"      Hazards: {len(pair.get('descriptions', []))} found")

            # AI 분석 상태
            ai_status = data.get('ai_status', 'unknown')
            print(f"\n    AI Analysis Status: {ai_status}")

            if ai_status == "success" and data.get('ai_analysis'):
                analysis_text = data['ai_analysis']
                print(f"\n    AI Analysis Preview (first 300 chars):")
                print("    " + "-" * 66)
                print("    " + analysis_text[:300].replace("\n", "\n    "))
                if len(analysis_text) > 300:
                    print("    ...")
                print("    " + "-" * 66)

                # 전체 결과 파일로 저장
                output_file = "test_full_api_result.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n    Full result saved to: {output_file}")

                # AI 분석 텍스트만 따로 저장
                analysis_file = "test_full_api_analysis.txt"
                with open(analysis_file, "w", encoding="utf-8") as f:
                    f.write("=" * 70 + "\n")
                    f.write("CHEMICAL SAFETY ANALYSIS BY AI\n")
                    f.write("=" * 70 + "\n\n")
                    f.write(analysis_text)
                    f.write("\n\n" + "=" * 70 + "\n")
                print(f"    AI analysis saved to: {analysis_file}")

            elif ai_status == "unavailable":
                print("\n    [WARNING] AI analysis was not available")
                print("    Check if AI API URL is configured correctly")

            elif ai_status == "error":
                print(f"\n    [FAIL] AI analysis failed")
                print(f"    Error: {data.get('ai_analysis', 'Unknown error')}")

            print("\n" + "=" * 70)
            print("[SUCCESS] Full pipeline test completed!")
            print("=" * 70)

            return True

        else:
            print(f"\n[FAIL] Request failed")
            print(f"    Response: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print("\n[FAIL] Request timeout")
        print("    The request took longer than 5 minutes")
        print("    CAMEO crawling can take 2-5 minutes")
        print("    AI analysis can take 30s-2 minutes")
        return False

    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    success = test_full_pipeline()

    if not success:
        print("\n" + "=" * 70)
        print("[FAILED] Test failed")
        print("=" * 70)
        print("\nTroubleshooting:")
        print("1. Check if backend is running: http://localhost:8000/health")
        print("2. Check if AI service is still running")
        print("3. Check network connection")
        print("=" * 70)
        exit(1)

    print("\n[INFO] Next steps:")
    print("  - Review the analysis in test_full_api_analysis.txt")
    print("  - Try with different substances")
    print("  - Integrate with your frontend")
    print("")
