"""
화학물질 안전 정보 링크 데이터베이스
위험/주의 조합에 대한 관련 기사 및 안전 정보 링크
"""

# 주요 물질 조합별 안전 정보 링크
CHEMICAL_SAFETY_LINKS = {
    # 락스 + 암모니아 (매우 위험)
    ("bleach", "ammonia"): [
        {
            "title": "락스와 암모니아 혼합 사고 예방",
            "url": "https://www.kosha.or.kr/kosha/data/musafetydata.do?mode=view&articleNo=430945",
            "source": "안전보건공단",
            "type": "사고예방"
        },
        {
            "title": "염소계 표백제 안전사용 지침",
            "url": "https://www.kosha.or.kr",
            "source": "안전보건공단",
            "type": "안전지침"
        }
    ],

    # 락스 + 식초/산성 세제 (매우 위험)
    ("bleach", "acid"): [
        {
            "title": "락스와 산성세제 혼합 사고 주의",
            "url": "https://www.kosha.or.kr",
            "source": "안전보건공단",
            "type": "사고예방"
        }
    ],

    # 과산화수소 + 산 (위험)
    ("peroxide", "acid"): [
        {
            "title": "과산화수소 취급 안전 지침",
            "url": "https://www.kosha.or.kr",
            "source": "안전보건공단",
            "type": "안전지침"
        }
    ],
}

# 공식 안전자료 링크
OFFICIAL_SAFETY_RESOURCES = [
    {
        "title": "MSDS 통합검색 (안전보건공단)",
        "url": "https://msds.kosha.or.kr/",
        "description": "모든 화학물질의 물질안전보건자료(MSDS) 검색"
    },
    {
        "title": "화학물질 안전정보 (환경부)",
        "url": "https://ncis.nier.go.kr/",
        "description": "국가 화학물질 정보시스템"
    },
    {
        "title": "화학물질 배출이동량 정보",
        "url": "https://tri.me.go.kr/",
        "description": "화학물질 배출량 및 유해성 정보"
    },
]


def normalize_chemical_name(name):
    """
    화학물질 이름을 정규화 (링크 검색용)
    """
    name = name.lower().strip()

    # 일반적인 별칭 매핑
    aliases = {
        "sodium hypochlorite": "bleach",
        "sodium hydroxide": "lye",
        "acetic acid": "acid",
        "glacial acetic acid": "acid",
        "hydrochloric acid": "acid",
        "sulfuric acid": "acid",
        "nitric acid": "acid",
        "hydrogen peroxide": "peroxide",
        "ammonia": "ammonia",
        "ammonium hydroxide": "ammonia",
    }

    for key, value in aliases.items():
        if key in name:
            return value

    return name


def get_safety_links(chemical_1, chemical_2):
    """
    두 화학물질 조합에 대한 안전 정보 링크 반환

    Args:
        chemical_1: 첫 번째 화학물질 이름
        chemical_2: 두 번째 화학물질 이름

    Returns:
        list: 안전 정보 링크 리스트
    """
    norm_1 = normalize_chemical_name(chemical_1)
    norm_2 = normalize_chemical_name(chemical_2)

    # 순서 상관없이 검색
    pair_key_1 = (norm_1, norm_2)
    pair_key_2 = (norm_2, norm_1)

    links = []

    # 특정 조합 링크 찾기
    if pair_key_1 in CHEMICAL_SAFETY_LINKS:
        links.extend(CHEMICAL_SAFETY_LINKS[pair_key_1])
    elif pair_key_2 in CHEMICAL_SAFETY_LINKS:
        links.extend(CHEMICAL_SAFETY_LINKS[pair_key_2])

    return links


def get_msds_search_url(chemical_name):
    """
    특정 화학물질의 MSDS 검색 URL 생성

    Args:
        chemical_name: 화학물질 이름

    Returns:
        str: MSDS 검색 URL
    """
    # URL 인코딩을 위한 간단한 처리
    encoded_name = chemical_name.replace(" ", "+")
    return f"https://msds.kosha.or.kr/MSDSInfo/kcic/msdsSearch.do?menuId=13&msdsEname={encoded_name}"


def get_all_links_for_analysis(dangerous_pairs, caution_pairs):
    """
    분석 결과에 대한 모든 안전 링크 수집

    Args:
        dangerous_pairs: 위험한 조합 리스트
        caution_pairs: 주의가 필요한 조합 리스트

    Returns:
        dict: 링크 정보
    """
    result = {
        "specific_links": [],  # 특정 조합에 대한 링크
        "msds_links": [],      # MSDS 링크
        "general_resources": OFFICIAL_SAFETY_RESOURCES  # 공식 자료
    }

    # 위험한 조합과 주의 조합 모두 처리
    all_pairs = dangerous_pairs + caution_pairs

    # 중복 제거를 위한 set
    seen_links = set()
    seen_chemicals = set()

    for pair in all_pairs:
        chem1 = pair.get("chemical_1", "")
        chem2 = pair.get("chemical_2", "")

        # 특정 조합 링크
        specific_links = get_safety_links(chem1, chem2)
        for link in specific_links:
            link_key = (link["title"], link["url"])
            if link_key not in seen_links:
                result["specific_links"].append(link)
                seen_links.add(link_key)

        # 각 화학물질의 MSDS 링크
        for chem in [chem1, chem2]:
            if chem and chem not in seen_chemicals:
                result["msds_links"].append({
                    "chemical": chem,
                    "url": get_msds_search_url(chem),
                    "title": f"{chem} 물질안전보건자료(MSDS)"
                })
                seen_chemicals.add(chem)

    return result


if __name__ == "__main__":
    # 테스트
    print("=== 안전 링크 테스트 ===\n")

    # 테스트 1: 락스 + 암모니아
    print("[테스트 1] Bleach + Ammonia")
    links = get_safety_links("SODIUM HYPOCHLORITE", "AMMONIA, ANHYDROUS")
    for link in links:
        print(f"  - {link['title']}")
        print(f"    {link['url']}")

    # 테스트 2: MSDS URL 생성
    print("\n[테스트 2] MSDS URL")
    msds_url = get_msds_search_url("HYDROGEN PEROXIDE")
    print(f"  {msds_url}")

    # 테스트 3: 전체 링크 수집
    print("\n[테스트 3] 전체 링크 수집")
    dangerous = [
        {"chemical_1": "BLEACH", "chemical_2": "AMMONIA"},
        {"chemical_1": "ACETIC ACID", "chemical_2": "HYDROGEN PEROXIDE"}
    ]
    all_links = get_all_links_for_analysis(dangerous, [])

    print(f"  특정 조합 링크: {len(all_links['specific_links'])}개")
    print(f"  MSDS 링크: {len(all_links['msds_links'])}개")
    print(f"  공식 자료: {len(all_links['general_resources'])}개")
