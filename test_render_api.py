"""
Render API Test - Simple version without emojis
"""
import requests
import json

RENDER_URL = "https://chemical-analyzer-api.onrender.com"

print("\n" + "=" * 70)
print("Testing API:", RENDER_URL)
print("=" * 70)

# Test 1: Health Check
print("\n[1] Health Check...")
print("Waiting for server to wake up... (may take 30-60 seconds)")
try:
    response = requests.get(f"{RENDER_URL}/", timeout=90)
    print("SUCCESS:", response.json())
except Exception as e:
    print("ERROR:", e)
    exit(1)

# Test 2: Simple Analyze
print("\n[2] Simple Analyze (Hydrogen Peroxide + Acetic Acid)...")
print("Crawling CAMEO... (30-60 seconds)")

try:
    response = requests.post(
        f"{RENDER_URL}/simple-analyze",
        json={"substances": ["Hydrogen Peroxide", "Acetic Acid"]},
        timeout=120
    )

    if response.status_code == 200:
        data = response.json()
        summary = data['summary']
        print("\nSUCCESS!")
        print("  Total pairs:", summary['total_pairs'])
        print("  Dangerous:", summary['dangerous_count'])
        print("  Status:", summary['overall_status'])
        print("  Message:", summary['message'][:100], "...")
    else:
        print("ERROR", response.status_code, ":", response.text[:200])

except Exception as e:
    print("ERROR:", e)

# Test 3: Hybrid Analyze (AI)
print("\n[3] Hybrid Analyze (Rules + AI Summary)...")
print("WARNING: This requires AI API to be running!")
print("Analyzing... (1-3 minutes)")

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

        # Rule-based results
        summary = data['rule_based_analysis']['summary']
        print("\nRule-based analysis SUCCESS!")
        print("  Risk level:", summary['overall_status'])
        print("  Dangerous pairs:", summary['dangerous_count'])

        # AI summary
        ai_status = data['ai_status']
        print("\nAI Summary Status:", ai_status)

        if ai_status == "success":
            ai_message = data['ai_summary_korean']
            print("\nKorean Summary:")
            print(ai_message)

            # Save simple JSON for backend
            simple = {
                "risk_level": summary['overall_status'],
                "message": ai_message
            }

            with open("api_result.json", "w", encoding="utf-8") as f:
                json.dump(simple, f, indent=2, ensure_ascii=False)

            print("\nResult saved to: api_result.json")
            print("\nALL TESTS PASSED!")

        elif ai_status == "unavailable":
            print("WARNING: AI API not configured or not running")
            print("  - Check Hugging Face Spaces is running")
            print("  - Check AI_API_URL environment variable")

        else:
            print("AI ERROR:", data.get('ai_summary', 'Unknown'))
    else:
        print("ERROR", response.status_code, ":", response.text[:200])

except requests.exceptions.Timeout:
    print("TIMEOUT! API took too long to respond")
    print("(First request may be slow due to cold start)")
except Exception as e:
    print("ERROR:", e)

print("\n" + "=" * 70)
print("Testing complete!")
print("=" * 70)
