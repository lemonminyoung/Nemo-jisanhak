"""
Colab API 연결 테스트 스크립트
"""

import requests
import json
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

COLAB_API_URL = os.getenv("COLAB_API_URL", "")

def test_colab_connection():
    """Colab API 연결 테스트"""

    print("=" * 70)
    print("Colab API Connection Test")
    print("=" * 70)

    if not COLAB_API_URL:
        print("[ERROR] COLAB_API_URL이 .env 파일에 설정되지 않았습니다.")
        print("\n.env 파일에 다음과 같이 추가하세요:")
        print("COLAB_API_URL=https://your-ngrok-url.ngrok.io")
        return False

    print(f"\nColab URL: {COLAB_API_URL}")

    # 1. Health Check
    print("\n[1] Health Check Test...")
    try:
        response = requests.get(f"{COLAB_API_URL}/health", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Connection successful!")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Model: {data.get('model', 'Unknown')}")
        else:
            print(f"   [FAIL] Connection failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("   [FAIL] Timeout: Colab server is not responding.")
        print("   TIP: Check if Colab notebook is running.")
        return False

    except requests.exceptions.ConnectionError:
        print("   [FAIL] Connection error: Cannot connect to Colab server.")
        print("   TIPS:")
        print("      - Colab 노트북의 마지막 셀이 실행 중인지 확인")
        print("      - ngrok URL이 올바른지 확인")
        print("      - ngrok 세션이 만료되지 않았는지 확인")
        return False

    except Exception as e:
        print(f"   [FAIL] Unexpected error: {e}")
        return False

    # 2. 간단한 분석 테스트
    print("\n[2] AI Analysis Test...")

    test_data = [
        {
            "pair_id": "Pair_1",
            "chemical_1": "SODIUM HYDROXIDE",
            "chemical_2": "HYDROCHLORIC ACID",
            "status": "Incompatible",
            "descriptions": ["Heat Generation", "Gas Generation"],
            "documentation_link": "https://example.com"
        }
    ]

    try:
        print("   Sending test data...")
        response = requests.post(
            f"{COLAB_API_URL}/analyze",
            json={"results": test_data},
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                print("   [OK] AI analysis successful!")
                print(f"\n   Analysis result (first 500 chars):")
                print("   " + "-" * 66)
                analysis_text = data.get("analysis", "")
                print("   " + analysis_text[:500].replace("\n", "\n   "))
                if len(analysis_text) > 500:
                    print("   ...")
                print("   " + "-" * 66)
            else:
                print(f"   [FAIL] AI analysis failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   [FAIL] Request failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print("   [FAIL] Timeout: AI model is not responding.")
        print("   TIP: Model loading can take 5-10 minutes.")
        print("      If this is first run, wait a moment and try again.")
        return False

    except Exception as e:
        print(f"   [FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 70)
    print("[SUCCESS] All tests passed! Colab API is working.")
    print("=" * 70)

    return True


if __name__ == "__main__":
    success = test_colab_connection()

    if not success:
        print("\n" + "=" * 70)
        print("[FAILED] Test Failed")
        print("=" * 70)
        print("\nTroubleshooting Guide:")
        print("\n1. Colab 노트북 실행:")
        print("   - ChemLLM_Colab_API.ipynb를 Google Colab에서 열기")
        print("   - 모든 셀을 순서대로 실행 (Runtime > Run all)")
        print("   - 마지막 셀까지 실행되어야 함 (Flask 서버 시작)")
        print("\n2. ngrok URL 확인:")
        print("   - Colab 마지막 셀 실행 결과에서 ngrok URL 복사")
        print("   - 예: https://xxxx-xx-xx-xx-xx.ngrok.io")
        print("\n3. .env 파일 업데이트:")
        print("   - .env 파일 열기")
        print("   - COLAB_API_URL=<복사한 URL> 형식으로 업데이트")
        print("\n4. 다시 테스트:")
        print("   - python test_colab_connection.py")
        print("=" * 70)
        exit(1)
    else:
        print("\n[SUCCESS] You can now run backend_with_colab.py!")
        print("\nHow to run:")
        print("   python backend_with_colab.py")
        print("\n또는:")
        print("   uvicorn backend_with_colab:app --reload")
