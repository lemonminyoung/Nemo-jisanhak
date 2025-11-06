
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import asyncio
from typing import List, Optional
import os
from chemical_analyzer import crawl_cameo_sequential
from simple_analyzer import analyze_simple
import json
from dotenv import load_dotenv
import google.generativeai as genai
import sys
from io import StringIO

# .env 파일 로드
load_dotenv()

app = FastAPI(title="Chemical Reactivity Analysis API")

@app.head("/health")
@app.get("/health")
async def health_check(): #uptime robot 용
    return {"status": "healthy"}
    
# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Colab API URL (환경변수 또는 직접 설정)
# Colab에서 ngrok URL을 받으면 여기 설정
AI_API_URL = os.getenv("AI_API_URL", "https://gimchabssal-chemical-ai.hf.space")  # 예: https://xxxx.ngrok.io

# Gemini API Key (번역용)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("[OK] Gemini API configured for translation")
else:
    print("[WARNING] Gemini API key not set. Translation will be unavailable.")

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
class AnalysisRequest(BaseModel):
    substances: List[str]
    use_ai: bool = True

class AnalysisResponse(BaseModel):
    success: bool
    cameo_results: List[dict]
    ai_analysis: Optional[str] = None
    ai_status: Optional[str] = None  # "success", "unavailable", "error"
    error: Optional[str] = None


def call_colab_api(cameo_results: List[dict], timeout: int = 300) -> dict:  # 5분으로 증가
    """
    Colab API 호출

    Args:
        cameo_results: CAMEO 크롤링 결과
        timeout: 타임아웃 (초)

    Returns:
        dict: {"success": bool, "analysis": str or None, "error": str or None}
    """
    if not AI_API_URL:
        return {
            "success": False,
            "error": "Colab API URL not configured"
        }

    try:
        print(f"[AI API] Calling Colab API at {AI_API_URL}")
        print(f"[AI API] Sending {len(cameo_results)} results")

        # Colab 헬스 체크
        print("[AI API] Checking Colab health...")
        health_response = requests.get(
            f"{AI_API_URL}/health",
            timeout=5
        )

        if health_response.status_code != 200:
            print(f"[AI API] [FAIL] Health check failed: {health_response.status_code}")
            return {
                "success": False,
                "error": "Colab server not healthy"
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
            "error": "Colab API timeout (model might be loading)"
        }
    except requests.exceptions.ConnectionError as e:
        print(f"[AI API] [CONNECTION ERROR]: {e}")
        return {
            "success": False,
            "error": "Cannot connect to Colab (check if Colab is running)"
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
        "colab_configured": bool(AI_API_URL)
    }


@app.get("/health")
async def health_check():
    """상세 헬스 체크"""
    colab_status = "not configured"

    if AI_API_URL:
        try:
            response = requests.get(f"{AI_API_URL}/health", timeout=3)
            if response.status_code == 200:
                colab_status = "connected"
            else:
                colab_status = "error"
        except:
            colab_status = "unreachable"

    return {
        "status": "healthy",
        "colab_api": colab_status,
        "colab_url": AI_API_URL if AI_API_URL else "Not set"
    }


@app.post("/set-colab-url")
async def set_colab_url(url: str):
    """
    Colab URL을 동적으로 설정
    (Colab 세션 재시작 시 사용)
    """
    global AI_API_URL
    AI_API_URL = url.rstrip('/')
    return {
        "success": True,
        "message": f"Colab URL updated to: {AI_API_URL}"
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
                print("[API] Warning: Colab API URL not set. Skipping AI analysis.")
                ai_status = "unavailable"
            else:
                print("[API] Starting AI analysis via Colab...")
                colab_response = call_colab_api(cameo_results)

                if colab_response.get("success"):
                    ai_analysis = colab_response.get("analysis", "")
                    ai_status = "success"
                    print("[API] AI analysis complete.")
                else:
                    error_msg = colab_response.get("error", "Unknown error")
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
                detail="Colab API URL not configured"
            )

        print(f"[API] Analyzing {len(cameo_results)} pre-crawled results...")

        colab_response = call_colab_api(cameo_results)

        if colab_response.get("success"):
            return {
                "success": True,
                "ai_analysis": colab_response.get("analysis", "")
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=colab_response.get("error", "AI analysis failed")
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

    Returns:
        {
            "success": true,
            "rule_based_analysis": {...},  // simple_analyzer 결과
            "ai_summary": "...",            // AI 요약문
            "ai_status": "success"
        }
    """
    try:
        print(f"[Hybrid] Analyzing {len(request.substances)} substances...")

        # 1. CAMEO 크롤링
        print("[Hybrid] Step 1: CAMEO crawling...")
        cameo_results = await crawl_with_suppressed_output(request.substances)

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
        if request.use_ai:
            if not AI_API_URL:
                print("[Hybrid] Warning: Colab API not configured")
                ai_status = "unavailable"
            else:
                print("[Hybrid] Step 3: AI summarization via Colab...")

                # AI에게 분석 결과를 보내서 요약문 생성 (영어)
                colab_response = call_colab_api_for_summary(analysis_result)

                if colab_response.get("success"):
                    ai_summary_en = colab_response.get("analysis", "")
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
                    error_msg = colab_response.get("error", "Unknown error")
                    print(f"[Hybrid] AI summary failed: {error_msg}")
                    ai_summary_en = f"AI summary unavailable: {error_msg}"
                    ai_status = "error"

        return {
            "success": True,
            "rule_based_analysis": analysis_result,
            "ai_summary_english": ai_summary_en,
            "ai_summary_korean": ai_summary_ko,
            "ai_status": ai_status
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = safe_error_message(e)
        print(f"[Hybrid] Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


def call_colab_api_for_summary(analysis_result: dict, timeout: int = 120) -> dict:
    """
    Colab API 호출 - AI 요약용

    분석 결과를 AI에게 보내서 사용자 친화적인 요약문만 생성
    """
    if not AI_API_URL:
        return {
            "success": False,
            "error": "Colab API URL not configured"
        }

    try:
        print(f"[Colab-Summary] Calling Colab for summary...")

        # AI에게 보낼 프롬프트 데이터
        summary_request = {
            "task": "summarize",  # 요약 작업임을 명시
            "analysis": analysis_result
        }

        response = requests.post(
            f"{AI_API_URL}/summarize",  # 새로운 엔드포인트
            json=summary_request,
            timeout=timeout
        )

        print(f"[Colab-Summary] Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            return {
                "success": data.get("success", False),
                "analysis": data.get("summary", ""),
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
            "error": "Colab API timeout"
        }
    except Exception as e:
        print(f"[Colab-Summary] Error: {e}")
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

IMPORTANT: Write in FRIENDLY, USER-FRIENDLY Korean tone following these formats:

[If 위험 (Dangerous)]:
{dangerous_count}가지 위험 결과가 발견되었습니다!
[각 위험한 조합에 대해] 물질명과 물질명이 만날 경우 [구체적인 위험 설명]이 발생할 수 있습니다.
제가 분석하기로는 이 제품들을 섞어 쓰는 건 매우 위험하다고 판단됩니다.

[If 주의 (Caution)]:
{caution_count}가지 주의 결과가 발견되었습니다!
물질명과 물질명이 만날 경우 특정 조건에서 위험이 생길 수 있습니다. 주의해서 사용해야 하는 물질입니다!
제가 분석하기로는 이 제품들을 섞어 쓰는 건 주의가 필요하다고 판단됩니다.

[If 안전 (Safe)]:
제가 분석한 결과 이 제품들은 섞어 써도 아무런 문제가 없군요!

Use proper chemical names in Korean (무수 암모니아, 차아염소산나트륨, etc.).
Be specific about hazards. Sound like a friendly expert helping the user.

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
        print(f"[OK] Colab API URL configured: {AI_API_URL}")
    else:
        print("[WARNING] Colab API URL not set. AI analysis will be unavailable.")
        print("         Set AI_API_URL in .env or use POST /set-colab-url")

    uvicorn.run(app, host="0.0.0.0", port=8000)
