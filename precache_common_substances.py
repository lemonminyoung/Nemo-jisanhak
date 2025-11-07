"""
한국 생활화학제품 주요 물질 조합 사전 캐싱 스크립트

일반 가정에서 흔히 사용하는 생활화학제품의 주요 성분들을
미리 API에 요청하여 캐시를 생성합니다.
"""

import requests
import itertools
import time
import json
from datetime import datetime
from typing import List
from pathlib import Path

# API 설정
API_URL = "https://nemo-jisanhak-6lu8.onrender.com/hybrid-analyze"
TIMEOUT = 300  # 5분

# 로그 파일 설정
LOG_DIR = Path("precache_logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"precache_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# 한국 가정에서 흔히 사용하는 생활화학제품의 주요 성분 (CAS 번호)
COMMON_SUBSTANCES = [
    # 표백/살균제
    {"name": "Sodium Hypochlorite", "cas": "7681-52-9"},  # 락스(표백제)
    {"name": "Hydrogen Peroxide", "cas": "7722-84-1"},  # 과산화수소 (옥시크린)

    # 세정제
    {"name": "Ammonia", "cas": "1336-21-6"},  # 암모니아 (유리세정제)
    {"name": "Sodium Hydroxide", "cas": "1310-73-2"},  # 가성소다 (배수관 세정제)
    {"name": "Hydrochloric Acid", "cas": "7647-01-0"},  # 염산 (변기세정제)
    {"name": "Sulfuric Acid", "cas": "7664-93-9"},  # 황산 (배수관 세정제)

    # 산성 세정제
    {"name": "Acetic Acid", "cas": "64-19-7"},  # 식초
    {"name": "Citric Acid", "cas": "77-92-9"},  # 구연산

    # 세제/계면활성제
    {"name": "Sodium Lauryl Sulfate", "cas": "151-21-3"},  # 계면활성제 (주방세제, 샴푸)

    # 소독제
    {"name": "Ethanol", "cas": "64-17-5"},  # 에탄올 (소독용 알코올)
    {"name": "Isopropyl Alcohol", "cas": "67-63-0"},  # 이소프로필 알코올

    # 기타 일반 물질
    {"name": "Water", "cas": "7732-18-5"},  # 물
    {"name": "Sodium Chloride", "cas": "7647-14-5"},  # 소금
    {"name": "Sodium Bicarbonate", "cas": "144-55-8"},  # 베이킹소다
]

def log(message: str):
    """화면과 파일에 동시 출력"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")

def test_combination(cas_numbers: List[str], product_names: List[str], index: int, total: int):
    """특정 물질 조합을 API에 요청하여 캐싱 (실패 시 건너뛰고 계속 진행)"""
    log(f"\n[{index}/{total}] Testing: {product_names} (CAS: {cas_numbers})")

    max_retries = 2  # 실패 시 최대 2번 재시도

    # products 형식으로 변환
    products = []
    for i, cas in enumerate(cas_numbers):
        products.append({
            "productName": product_names[i],
            "casNumbers": [cas]
        })

    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                json={"useAi": True, "products": products},
                timeout=TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                risk_level = result.get("simple_response", {}).get("risk_level", "알 수 없음")
                log(f"  ✅ Success! Risk Level: {risk_level}")
                return True
            else:
                log(f"  ❌ Failed: HTTP {response.status_code} (Attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(5)  # 재시도 전 5초 대기
                    continue
                return False

        except requests.exceptions.Timeout:
            log(f"  ⏱️ Timeout (>5분) (Attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            return False
        except requests.exceptions.ConnectionError as e:
            log(f"  ❌ Connection Error: {e} (Attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(10)  # 연결 오류 시 10초 대기
                continue
            return False
        except Exception as e:
            log(f"  ❌ Error: {e} (Attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            return False

    return False

def main():
    """메인 실행 함수 (자동 실행, 실패 시 건너뛰기)"""
    log("=" * 60)
    log("한국 생활화학제품 물질 조합 사전 캐싱 (자동 모드)")
    log("=" * 60)
    log(f"로그 파일: {LOG_FILE}")
    log(f"\n총 물질 개수: {len(COMMON_SUBSTANCES)}")

    # 2개 조합 생성 (가장 흔한 케이스)
    combinations_2 = list(itertools.combinations(COMMON_SUBSTANCES, 2))
    log(f"2개 조합 개수: {len(combinations_2)}")

    # 3개 조합 생성 (일부만 - 너무 많으면 시간 소요)
    # 위험한 조합 위주로 선별
    dangerous_indices = [0, 1, 2, 3, 4, 5]  # Sodium Hypochlorite, Hydrogen Peroxide, Ammonia, Sodium Hydroxide, Hydrochloric Acid, Sulfuric Acid
    dangerous_substances = [COMMON_SUBSTANCES[i] for i in dangerous_indices]
    combinations_3 = list(itertools.combinations(dangerous_substances, 3))
    log(f"3개 조합 개수 (선별): {len(combinations_3)}")

    total_combinations = combinations_2 + combinations_3
    total_count = len(total_combinations)

    log(f"\n총 요청 개수: {total_count}")
    log(f"예상 소요 시간 (최악): {total_count * 4} 분 ({total_count * 4 / 60:.1f} 시간)")
    log(f"예상 소요 시간 (평균): {total_count * 2} 분 ({total_count * 2 / 60:.1f} 시간)")
    log("[주의] 이미 캐시된 조합은 1초 내로 완료됩니다!")
    log("[주의] 실패한 조합은 자동으로 건너뛰고 계속 진행됩니다.\n")

    log("[시작] 3초 후 자동 시작...")
    time.sleep(3)

    # 통계
    success_count = 0
    fail_count = 0
    failed_combinations = []
    start_time = time.time()

    # 모든 조합 테스트
    for i, combo in enumerate(total_combinations, 1):
        # combo는 substance dict들의 튜플
        cas_numbers = [substance["cas"] for substance in combo]
        product_names = [substance["name"] for substance in combo]

        success = test_combination(cas_numbers, product_names, i, total_count)

        if success:
            success_count += 1
        else:
            fail_count += 1
            failed_combinations.append({"cas": cas_numbers, "names": product_names})

        # 진행 상황
        elapsed = time.time() - start_time
        avg_time = elapsed / i if i > 0 else 0
        remaining = (total_count - i) * avg_time

        log(f"  Progress: {i}/{total_count} ({i/total_count*100:.1f}%) | Success: {success_count} | Fail: {fail_count}")
        log(f"  Elapsed: {elapsed/60:.1f}분 | Remaining: {remaining/60:.1f}분")

        # API 부하 방지를 위한 짧은 대기
        time.sleep(2)

    # 최종 결과
    total_time = time.time() - start_time
    log("\n" + "=" * 60)
    log("[완료] 캐싱 완료!")
    log("=" * 60)
    log(f"총 요청: {total_count}")
    log(f"[성공] {success_count}개 ({success_count/total_count*100:.1f}%)")
    log(f"[실패] {fail_count}개 ({fail_count/total_count*100:.1f}%)")
    log(f"[시간] 소요 시간: {total_time/60:.1f}분 ({total_time/3600:.2f}시간)")
    log(f"[속도] 평균 응답 시간: {total_time/total_count:.1f}초")

    # 실패한 조합 저장
    if failed_combinations:
        log(f"\n[실패] 실패한 조합 목록 ({len(failed_combinations)}개):")
        failed_file = LOG_DIR / f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(failed_combinations, f, ensure_ascii=False, indent=2)
        log(f"   실패 목록 저장: {failed_file}")
        for combo in failed_combinations[:10]:  # 처음 10개만 출력
            log(f"   - {combo}")
        if len(failed_combinations) > 10:
            log(f"   ... 외 {len(failed_combinations) - 10}개")

    log("\n[완료] 모든 작업 완료! 로그는 위 파일에 저장되었습니다.")

if __name__ == "__main__":
    main()
