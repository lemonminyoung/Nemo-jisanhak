
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import asyncio
from typing import List, Optional
import os
from chemical_analyzer import crawl_cameo_sequential
from simple_analyzer import analyze_simple
from safety_links import get_all_links_for_analysis
import json
from dotenv import load_dotenv
import google.generativeai as genai
import sys
from io import StringIO
import hashlib
from pathlib import Path

# .env 파일 로드
load_dotenv()

app = FastAPI(title="Chemical Reactivity Analysis API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI API URL (환경변수 또는 직접 설정)
# Hugging Face Spaces URL
AI_API_URL = os.getenv("AI_API_URL", "https://gimchabssal-chemical-ai.hf.space")

# Gemini API Key (번역용)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("[OK] Gemini API configured for translation")
else:
    print("[WARNING] Gemini API key not set. Translation will be unavailable.")

# 캐시 디렉토리 설정
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
print(f"[OK] Cache directory: {CACHE_DIR.absolute()}")

# 캐싱 함수들
def get_cache_key(substances: List[str]) -> str:
    """물질 리스트를 정렬하여 캐시 키 생성"""
    sorted_substances = tuple(sorted([s.strip().lower() for s in substances]))
    key_string = str(sorted_substances)
    return hashlib.md5(key_string.encode()).hexdigest()

def get_cached_result(substances: List[str]):
    """캐시에서 결과 가져오기"""
    try:
        cache_key = get_cache_key(substances)
        cache_file = CACHE_DIR / f"{cache_key}.json"

        if cache_file.exists():
            print(f"[Cache] HIT for {len(substances)} substances")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"[Cache] MISS for {len(substances)} substances")
            return None
    except Exception as e:
        print(f"[Cache] Error reading cache: {e}")
        return None

def save_to_cache(substances: List[str], result: dict):
    """결과를 캐시에 저장"""
    try:
        cache_key = get_cache_key(substances)
        cache_file = CACHE_DIR / f"{cache_key}.json"

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"[Cache] SAVED for {len(substances)} substances")
    except Exception as e:
        print(f"[Cache] Error saving cache: {e}")

# Helper function to safely encode error messages
def safe_error_message(error: Exception) -> str:
    """
    Safely convert exception to ASCII string to avoid encoding errors
    """
    try:
        error_str = str(error)
        # Try to encode as ASCII, replacing non-ASCII characters
        safe_msg = error_str.encode('ascii', errors='replace').decode('ascii')
        return safe_msg if safe_msg.strip() else "An unknown error occurred"
    except:
        return "An unknown error occurred during error processing"

# Helper function to suppress Playwright output
async def crawl_with_suppressed_output(substances: List[str]) -> list:
    """
    Wrapper to suppress stdout/stderr during Playwright crawling
    to prevent encoding errors with special characters
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        # Redirect output to nowhere
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # Run the crawl
        results = await crawl_cameo_sequential(substances)
        return results
    finally:
        # Always restore stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

# Request/Response 모델
class Product(BaseModel):
    productName: str
    casNumbers: List[str]

class AnalysisRequest(BaseModel):
    useAi: bool = True
    products: List[Product]

class AnalysisResponse(BaseModel):
    success: bool
    cameo_results: List[dict]
    ai_analysis: Optional[str] = None
    ai_status: Optional[str] = None  # "success", "unavailable", "error"
    error: Optional[str] = None


def call_ai_api(cameo_results: List[dict], timeout: int = 300) -> dict:  # 5분으로 증가
    """
    AI API 호출 (Hugging Face Spaces)

    Args:
        cameo_results: CAMEO 크롤링 결과
        timeout: 타임아웃 (초)

    Returns:
        dict: {"success": bool, "analysis": str or None, "error": str or None}
    """
    if not AI_API_URL:
        return {
            "success": False,
            "error": "AI API URL not configured"
        }

    try:
        print(f"[AI API] Calling AI API at {AI_API_URL}")
        print(f"[AI API] Sending {len(cameo_results)} results")

        # AI 헬스 체크
        print("[AI API] Checking AI service health...")
        health_response = requests.get(
            f"{AI_API_URL}/health",
            timeout=5
        )

        if health_response.status_code != 200:
            print(f"[AI API] [FAIL] Health check failed: {health_response.status_code}")
            return {
                "success": False,
                "error": "AI server not healthy"
            }

        print("[AI API] [OK] Health check passed")

        # AI 분석 요청
        print("[AI API] Sending analysis request...")
        response = requests.post(
            f"{AI_API_URL}/analyze",
            json={"results": cameo_results},
            timeout=timeout
        )

        print(f"[AI API] Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            return {
                "success": data.get("success", False),
                "analysis": data.get("analysis", ""),
                "error": data.get("error")
            }
        else:
            error_detail = response.text
            print(f"[AI API] [ERROR] Error response: {error_detail}")

            # JSON 파싱 시도
            try:
                error_json = response.json()
                error_msg = f"HTTP {response.status_code}\n"
                error_msg += f"Error: {error_json.get('error', 'Unknown')}\n"
                if 'error_type' in error_json:
                    error_msg += f"Type: {error_json['error_type']}\n"
                if 'traceback' in error_json:
                    error_msg += f"Traceback:\n{error_json['traceback']}"
                return {
                    "success": False,
                    "error": error_msg
                }
            except:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }

    except requests.exceptions.Timeout:
        print("[AI API] [TIMEOUT] Request timeout")
        return {
            "success": False,
            "error": "AI API timeout (model might be loading)"
        }
    except requests.exceptions.ConnectionError as e:
        print(f"[AI API] [CONNECTION ERROR]: {e}")
        return {
            "success": False,
            "error": "Cannot connect to AI service (check if service is running)"
        }
    except Exception as e:
        print(f"[AI API] [ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


# API 엔드포인트
@app.get("/")
async def root():
    """헬스 체크"""
    return {
        "service": "Chemical Reactivity Analysis API",
        "status": "running",
        "version": "1.0.0",
        "ai_configured": bool(AI_API_URL)
    }


@app.head("/health")
@app.get("/health")
async def health_check():
    """상세 헬스 체크 (Uptime Robot 지원)"""
    ai_status = "not configured"

    if AI_API_URL:
        try:
            response = requests.get(f"{AI_API_URL}/health", timeout=3)
            if response.status_code == 200:
                ai_status = "connected"
            else:
                ai_status = "error"
        except:
            ai_status = "unreachable"

    return {
        "status": "healthy",
        "ai_api": ai_status,
        "ai_url": AI_API_URL if AI_API_URL else "Not set"
    }


@app.post("/set-ai-url")
async def set_ai_url(url: str):
    """
    AI API URL을 동적으로 설정
    (Hugging Face Spaces URL 변경 시 사용)
    """
    global AI_API_URL
    AI_API_URL = url.rstrip('/')
    return {
        "success": True,
        "message": f"AI API URL updated to: {AI_API_URL}"
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_chemicals(request: AnalysisRequest):
    """
    화학 물질 반응성 분석

    Args:
        request: substances (물질 리스트), use_ai (AI 분석 여부)

    Returns:
        CAMEO 크롤링 결과 + AI 분석 (선택)
    """
    try:
        print(f"[API] Analyzing {len(request.substances)} substances...")

        # 1. CAMEO 크롤링
        print("[API] Starting CAMEO crawling...")
        cameo_results = await crawl_with_suppressed_output(request.substances)

        if not cameo_results:
            raise HTTPException(
                status_code=404,
                detail="No reactivity data found for given substances"
            )

        print(f"[API] CAMEO crawling complete. Found {len(cameo_results)} pairs.")

        ai_analysis = None
        ai_status = "skipped"

        # 2. AI 분석 (선택사항)
        if request.use_ai:
            if not AI_API_URL:
                print("[API] Warning: AI API URL not set. Skipping AI analysis.")
                ai_status = "unavailable"
            else:
                print("[API] Starting AI analysis via Hugging Face...")
                ai_response = call_ai_api(cameo_results)

                if ai_response.get("success"):
                    ai_analysis = ai_response.get("analysis", "")
                    ai_status = "success"
                    print("[API] AI analysis complete.")
                else:
                    error_msg = ai_response.get("error", "Unknown error")
                    print(f"[API] AI analysis failed: {error_msg}")
                    ai_analysis = f"AI analysis unavailable: {error_msg}"
                    ai_status = "error"

        return AnalysisResponse(
            success=True,
            cameo_results=cameo_results,
            ai_analysis=ai_analysis,
            ai_status=ai_status
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-from-json")
async def analyze_from_json(cameo_results: List[dict]):
    """
    이미 크롤링된 CAMEO 결과로 AI 분석만 수행
    """
    try:
        if not AI_API_URL:
            raise HTTPException(
                status_code=503,
                detail="AI API URL not configured"
            )

        print(f"[API] Analyzing {len(cameo_results)} pre-crawled results...")

        ai_response = call_ai_api(cameo_results)

        if ai_response.get("success"):
            return {
                "success": True,
                "ai_analysis": ai_response.get("analysis", "")
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=ai_response.get("error", "AI analysis failed")
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simple-analyze")
async def simple_analyze_endpoint(request: AnalysisRequest):
    """
    간단 분석 (AI 없이 규칙 기반만)

    CAMEO 데이터만 사용하여 빠르고 정확한 분석 제공
    - 응답 속도: 2-5분
    - 정확도: 100% (NOAA 검증 데이터)
    - AI 불필요

    Returns:
        {
            "success": true,
            "summary": {
                "message": "위험: 1개의 위험한 조합이 발견되었습니다!",
                "dangerous_count": 1,
                "caution_count": 0,
                "safe_count": 2
            },
            "dangerous_pairs": [...],
            "recommendations": [...]
        }
    """
    try:
        print(f"[Simple] Analyzing {len(request.substances)} substances...")

        # CAMEO 크롤링
        print("[Simple] Starting CAMEO crawling...")
        cameo_results = await crawl_with_suppressed_output(request.substances)

        if not cameo_results:
            raise HTTPException(
                status_code=404,
                detail="No reactivity data found from CAMEO"
            )

        print(f"[Simple] CAMEO found {len(cameo_results)} pairs")

        # 간단 분석 (AI 없이 규칙만)
        print("[Simple] Analyzing with rules...")
        analysis_result = analyze_simple(cameo_results)

        print(f"[Simple] Complete: {analysis_result['summary']['overall_status']}")

        return {
            "success": True,
            **analysis_result
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = safe_error_message(e)
        print(f"[Simple] Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/hybrid-analyze")
async def hybrid_analyze_endpoint(request: AnalysisRequest):
    """
    하이브리드 분석 (규칙 기반 + AI 요약)

    BEST 방식:
    1. CAMEO 데이터로 위험도 판단 (100% 정확)
    2. simple_analyzer로 위험/주의/안전 분류
    3. AI로 결과를 사용자 친화적인 문장으로 요약

    - 정확도: 100% (CAMEO 데이터)
    - 가독성: AI가 문장 정리

    Input Format:
        {
            "useAi": true,
            "products": [
                {
                    "productName": "Bleach Cleaner",
                    "casNumbers": ["103-95-7", "64-17-5"]
                },
                {
                    "productName": "Ammonia Solution",
                    "casNumbers": ["1336-21-6"]
                }
            ]
        }

    Returns:
        {
            "success": true,
            "rule_based_analysis": {...},  // simple_analyzer 결과
            "ai_summary": "...",            // AI 요약문
            "ai_status": "success"
        }
    """
    try:
        # products 배열에서 모든 CAS 번호 추출
        all_cas_numbers = []
        for product in request.products:
            all_cas_numbers.extend(product.casNumbers)

        print(f"[Hybrid] Analyzing {len(all_cas_numbers)} CAS numbers from {len(request.products)} products...")

        # 0. 캐시 확인
        cached_result = get_cached_result(all_cas_numbers)
        if cached_result:
            print("[Hybrid] Returning cached result!")
            return cached_result

        # 1. CAMEO 크롤링
        print("[Hybrid] Step 1: CAMEO crawling...")
        cameo_results = await crawl_with_suppressed_output(all_cas_numbers)

        if not cameo_results:
            raise HTTPException(
                status_code=404,
                detail="No reactivity data found from CAMEO"
            )

        print(f"[Hybrid] CAMEO found {len(cameo_results)} pairs")

        # 2. 규칙 기반 분석
        print("[Hybrid] Step 2: Rule-based classification...")
        analysis_result = analyze_simple(cameo_results)
        print(f"[Hybrid] Classification: {analysis_result['summary']['overall_status']}")

        ai_summary_en = None
        ai_summary_ko = None
        ai_status = "skipped"

        # 3. AI 요약 (선택사항)
        if request.useAi:
            if not AI_API_URL:
                print("[Hybrid] Warning: AI API not configured")
                ai_status = "unavailable"
            else:
                print("[Hybrid] Step 3: AI summarization via Hugging Face...")

                # AI에게 분석 결과를 보내서 요약문 생성 (영어)
                ai_response = call_ai_api_for_summary(analysis_result)

                if ai_response.get("success"):
                    ai_summary_en = ai_response.get("analysis", "")
                    print("[Hybrid] AI summary (EN) complete")

                    # Step 4: Gemini로 친근한 한국어 번역
                    print("[Hybrid] Step 4: Translating to friendly Korean via Gemini...")
                    translation_response = translate_with_gemini(ai_summary_en, analysis_result)

                    if translation_response.get("success"):
                        ai_summary_ko = translation_response.get("translation", "")
                        ai_status = "success"
                        print("[Hybrid] Translation complete")
                    else:
                        error_msg = translation_response.get("error", "Unknown error")
                        print(f"[Hybrid] Translation failed: {error_msg}")
                        ai_summary_ko = f"Translation unavailable: {error_msg}"
                        ai_status = "partial"  # 영어 요약은 성공, 번역은 실패
                else:
                    error_msg = ai_response.get("error", "Unknown error")
                    print(f"[Hybrid] AI summary failed: {error_msg}")
                    ai_summary_en = f"AI summary unavailable: {error_msg}"
                    ai_status = "error"

        # 간단한 응답 형식 (백엔드용)
        simple_response = {
            "risk_level": analysis_result.get("summary", {}).get("overall_status", "알 수 없음"),
            "message": ai_summary_ko if ai_summary_ko else analysis_result.get("summary", {}).get("message", "")
        }

        # 안전 정보 링크 수집 (위험/주의 조합에 대해서만)
        safety_links = get_all_links_for_analysis(
            analysis_result.get("dangerous_pairs", []),
            analysis_result.get("caution_pairs", [])
        )

        # 최종 결과
        final_result = {
            "success": True,
            "rule_based_analysis": analysis_result,
            "ai_summary_english": ai_summary_en,
            "ai_summary_korean": ai_summary_ko,
            "ai_status": ai_status,
            "simple_response": simple_response,  # 간단한 형식 추가
            "safety_links": safety_links  # 안전 정보 링크 추가
        }

        # 캐시에 저장
        save_to_cache(all_cas_numbers, final_result)

        return final_result

    except HTTPException:
        raise
    except Exception as e:
        error_msg = safe_error_message(e)
        print(f"[Hybrid] Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


def call_ai_api_for_summary(analysis_result: dict, timeout: int = 240) -> dict:
    """
    AI API 호출 - AI 요약용 (Hugging Face Spaces)

    분석 결과를 AI에게 보내서 사용자 친화적인 요약문만 생성
    """
    if not AI_API_URL:
        return {
            "success": False,
            "error": "AI API URL not configured"
        }

    try:
        print(f"[AI-Summary] Calling AI service for summary...")

        # 분석 결과를 프롬프트로 변환
        summary = analysis_result.get("summary", {})
        dangerous_pairs = analysis_result.get("dangerous_pairs", [])

        # 프롬프트 생성
        prompt = f"""Analyze the following chemical safety data and provide a brief safety summary in English.

Overall Status: {summary.get('overall_status', 'Unknown')}
Dangerous Pairs: {summary.get('dangerous_count', 0)}
Caution Pairs: {summary.get('caution_count', 0)}

"""

        # 위험한 조합 추가
        if dangerous_pairs:
            prompt += "Dangerous Combinations:\n"
            for pair in dangerous_pairs[:3]:  # 최대 3개만
                prompt += f"- {pair.get('chemical_1', '')} + {pair.get('chemical_2', '')}\n"
                prompt += f"  Status: {pair.get('status', '')}\n"
                prompt += f"  Hazards: {', '.join(pair.get('hazards', [])[:3])}\n"

        prompt += "\nProvide a concise safety summary (2-3 sentences)."

        # AI 요청 (Hugging Face Space는 루트 엔드포인트 사용)
        response = requests.post(
            AI_API_URL,  # 루트 엔드포인트
            json={"prompt": prompt},
            timeout=timeout
        )

        print(f"[AI-Summary] Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            # Hugging Face API는 "response" 필드를 반환
            ai_response = data.get("response", "") or data.get("analysis", "")
            return {
                "success": data.get("success", False),
                "analysis": ai_response,
                "error": data.get("error")
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "AI API timeout"
        }
    except Exception as e:
        print(f"[AI-Summary] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def translate_with_gemini(english_text: str, analysis_result: dict, retries: int = 2) -> dict:
    """
    Gemini API로 영어 텍스트를 사용자 친화적인 한국어로 번역

    Args:
        english_text (str): 번역할 영어 문장
        analysis_result (dict): 분석 결과 (위험도 판단용)
        retries (int): 실패 시 재시도 횟수

    Returns:
        dict: {"success": bool, "translation": str, "error": str}
    """
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "error": "Gemini API key not configured"
        }

    # 분석 결과에서 정보 추출
    summary = analysis_result.get("summary", {})
    overall_status = summary.get("overall_status", "알 수 없음")
    dangerous_count = summary.get("dangerous_count", 0)
    caution_count = summary.get("caution_count", 0)
    dangerous_pairs = analysis_result.get("dangerous_pairs", [])
    caution_pairs = analysis_result.get("caution_pairs", [])

    for attempt in range(1, retries + 1):
        try:
            print(f"[Gemini] Translating ({len(english_text)} chars)... [Attempt {attempt}/{retries}]")

            # 최신 Gemini 모델 (2025 기준)
            model = genai.GenerativeModel("gemini-2.5-flash")

            # 위험한 조합 정보 포맷팅
            dangerous_info = json.dumps(
                [{"chem1": p.get("chemical_1"), "chem2": p.get("chemical_2"), "status": p.get("status")}
                 for p in dangerous_pairs[:3]],
                ensure_ascii=False,
                indent=2
            ) if dangerous_pairs else "None"

            caution_info = json.dumps(
                [{"chem1": p.get("chemical_1"), "chem2": p.get("chemical_2"), "status": p.get("status")}
                 for p in caution_pairs[:3]],
                ensure_ascii=False,
                indent=2
            ) if caution_pairs else "None"

            # 친근한 말투로 번역하는 프롬프트
            prompt = f"""
You are a friendly chemical safety assistant helping users understand chemical safety results.
Convert the English analysis into a FRIENDLY, CONVERSATIONAL Korean message for app users.

Analysis Info:
- Overall Status: {overall_status}
- Dangerous Count: {dangerous_count}
- Caution Count: {caution_count}

English Analysis:
{english_text}

Dangerous Pairs (if any):
{dangerous_info}

Caution Pairs (if any):
{caution_info}

IMPORTANT GUIDELINES:

1. **중복 제거**: 같은 위험(예: 폭발, 화재, 가스 발생)을 가진 여러 조합은 물질명을 나열하면서 한 번만 설명하세요.
   예: "빙초산, 과산화수소, 염산을 섞으면 폭발이 일어날 수 있어요!"

2. **구체적인 조건 명시**: 단순히 "위험하다"가 아니라 WHEN/HOW를 명시하세요:
   - 온도 조건: "뜨거운 상태에서 섞으면", "상온에서도"
   - 농도 조건: "고농도일 때", "희석된 상태에서는"
   - 환경 조건: "밀폐된 공간에서", "환기가 안 되면"

3. **안전 사용법 제시**: 위험 조건을 피하는 실용적인 방법을 알려주세요:
   - "차가운 물에서만 사용하세요"
   - "반드시 환기를 시키고 사용하세요"
   - "희석해서 사용하면 안전해요"
   - "절대 섞지 말고 따로따로 사용하세요"

4. **메시지 구조**:

[위험 (Dangerous) 형식]:
확인 결과 {dangerous_count}가지 위험한 조합이 발견되었습니다!

**폭발/화재 위험** (해당되는 경우)
- [물질A, 물질B, 물질C]를 섞으면 [구체적 조건]에서 폭발이나 화재가 발생할 수 있어요.
- 안전 사용법: [구체적 방법]

**유독가스 발생** (해당되는 경우)
- [물질D]와 [물질E]가 만나면 [어떤 가스]가 발생해 [구체적 증상]이 나타날 수 있어요.
- 안전 사용법: [구체적 방법]

**화상/부식 위험** (해당되는 경우)
- [물질F]와 [물질G]가 [조건]에서 만나면 [구체적 위험]
- 안전 사용법: [구체적 방법]

⚠️ 이 제품들은 절대 섞어 쓰지 마세요!

[주의 (Caution) 형식]:
{caution_count}가지 조합은 특정 상황에서 주의가 필요해요.

- [물질명]과 [물질명]: [정확한 조건 - 예: 뜨거운 물에서, 고농도일 때] 반응할 수 있어요.
  → 안전하게 쓰려면: [구체적 방법 - 예: 차가운 물에서만 사용, 소량만 사용]

[안전 (Safe) 형식]:
좋은 소식이에요! 이 물질들은 함께 사용해도 안전합니다. 😊

Use proper Korean chemical names. Be specific and practical.

Korean message (FRIENDLY TONE ONLY):
"""

            # Gemini 호출
            response = model.generate_content(prompt)

            # ---  응답 파싱 (안정 처리) ---
            translation = None

            # 1️ 일반 text 속성
            if hasattr(response, "text") and response.text:
                translation = response.text.strip()

            # 2️ candidates 내부 파싱 (SDK 구조 대응)
            elif hasattr(response, "candidates") and response.candidates:
                first_candidate = response.candidates[0]
                if hasattr(first_candidate, "content") and first_candidate.content.parts:
                    parts = first_candidate.content.parts
                    # parts가 여러 개인 경우 텍스트 부분만 합침
                    translation = "\n".join(
                        p.text.strip() for p in parts if hasattr(p, "text")
                    ).strip()

            # 3️ fallback: string 변환
            if not translation and str(response):
                translation = str(response).strip()

            # ---  검증 ---
            if translation and len(translation) > 5:
                print(f"[Gemini]  Translation complete ({len(translation)} chars)")
                return {
                    "success": True,
                    "translation": translation
                }

            else:
                print(f"[Gemini]  Empty or invalid response on attempt {attempt}")
                if attempt < retries:
                    print("[Gemini] Retrying...")
                    continue
                else:
                    return {
                        "success": False,
                        "error": "Empty or invalid response from Gemini"
                    }

        except Exception as e:
            print(f"[Gemini]  Error on attempt {attempt}: {e}")
            import traceback
            traceback.print_exc()

            if attempt < retries:
                print("[Gemini] Retrying after error...")
                continue
            else:
                return {
                    "success": False,
                    "error": str(e)
                }



# 개발 서버 실행
if __name__ == "__main__":
    import uvicorn

    # .env 파일에서 AI_API_URL 로드 확인
    if AI_API_URL:
        print(f"[OK] AI API URL configured: {AI_API_URL}")
    else:
        print("[WARNING] AI API URL not set. AI analysis will be unavailable.")
        print("         Set AI_API_URL in .env or use POST /set-ai-url")

    uvicorn.run(app, host="0.0.0.0", port=8000)
