from datetime import datetime, timedelta

# 기준 시작 시간 설정
start_time = datetime(2025, 10, 1, 9, 0, 0)

fake_articles_data = [
    # =================================================================
    # [주제: 꿈의 배터리 '인피니티 셀' 사태]
    # (출시의 환호 -> 사고 발생 -> 은폐 의혹 -> 몰락과 수습)
    # =================================================================

    # ------------------------------------------------------------------
    # [Phase 1: 화려한 등장과 기대감] (1~5)
    # ------------------------------------------------------------------
    {
        "title": "넥스트에너지, 충전 없는 배터리 '인피니티 셀' 세계 최초 공개",
        "contents": "국내 스타트업 넥스트에너지가 한 번 충전으로 일주일을 사용하는 스마트폰 배터리 '인피니티 셀'을 공개해 전 세계의 이목을 집중시켰다. 기존 리튬이온 대비 에너지 밀도가 10배에 달한다.",
        "category": "IT/과학",
        "url": "https://news.test.com/it/101",
        "company_name": "테크데일리",
        "time": start_time,
        "author": "김혁신 기자"
    },
    {
        "title": "[특징주] 넥스트에너지, 신기술 발표에 상한가 직행... 시총 10조 돌파",
        "contents": "'인피니티 셀' 발표 직후 넥스트에너지 주가가 가격제한폭까지 치솟았다. 증권가에서는 제2의 반도체 신화가 될 것이라며 목표 주가를 잇달아 상향 조정하고 있다.",
        "category": "경제",
        "url": "https://news.test.com/eco/102",
        "company_name": "파이낸스뉴스",
        "time": start_time + timedelta(hours=4),
        "author": "이주식 기자"
    },
    {
        "title": "애플·삼성, '인피니티 셀' 도입 경쟁... 스마트폰 시장 판도 바뀌나",
        "contents": "글로벌 스마트폰 제조사들이 넥스트에너지의 배터리를 차기 모델에 탑재하기 위해 치열한 물밑 협상을 벌이고 있다. 업계 관계자는 \"배터리 수명이 폰 교체 주기를 바꿀 것\"이라고 전망했다.",
        "category": "IT/과학",
        "url": "https://news.test.com/it/103",
        "company_name": "전자신문",
        "time": start_time + timedelta(days=1, hours=2),
        "author": "박모바일 기자"
    },
    {
        "title": "사전 예약 100만 대 '완판'... '인피니티 폰' 품귀 현상",
        "contents": "인피니티 셀이 탑재된 시범 모델의 사전 예약 물량이 개시 1분 만에 매진됐다. 중고 거래 사이트에서는 웃돈을 얹어 거래하겠다는 글이 쇄도하고 있다.",
        "category": "생활/문화",
        "url": "https://news.test.com/life/104",
        "company_name": "소비자저널",
        "time": start_time + timedelta(days=2, hours=5),
        "author": "최트렌드 기자"
    },
    {
        "title": "정부, 차세대 배터리 국가전략기술 지정... 세제 혜택 강화",
        "contents": "산업통상자원부는 인피니티 셀 기술을 국가 안보와 직결된 전략 기술로 지정하고, R&D 투자에 대한 파격적인 세액 공제 혜택을 부여하기로 결정했다.",
        "category": "정치",
        "url": "https://news.test.com/pol/105",
        "company_name": "정책뉴스",
        "time": start_time + timedelta(days=3, hours=1),
        "author": "강정책 기자"
    },

    # ------------------------------------------------------------------
    # [Phase 2: 균열의 시작] (6~10)
    # ------------------------------------------------------------------
    {
        "title": "인터넷 커뮤니티서 '인피니티 폰' 발열 논란... \"손 난로 수준\"",
        "contents": "제품을 수령한 초기 구매자들 사이에서 기기가 지나치게 뜨거워진다는 후기가 잇따르고 있다. 일부 사용자는 게임 구동 시 60도까지 온도가 올라간다며 불안감을 호소했다.",
        "category": "IT/과학",
        "url": "https://news.test.com/it/106",
        "company_name": "넷세상",
        "time": start_time + timedelta(days=5, hours=10),
        "author": "나유저 기자"
    },
    {
        "title": "넥스트에너지 측 \"초기 최적화 문제, 펌웨어 업데이트로 해결\"",
        "contents": "발열 논란이 확산되자 넥스트에너지는 공식 입장문을 내고 \"소프트웨어 최적화 과정의 일시적 현상\"이라며 안전에는 전혀 문제가 없다고 해명했다.",
        "category": "경제",
        "url": "https://news.test.com/eco/107",
        "company_name": "기업일보",
        "time": start_time + timedelta(days=5, hours=16),
        "author": "홍보팀 기자"
    },
    {
        "title": "[단독] 충전 중이던 '인피니티 폰' 화재 신고 접수... 소방당국 출동",
        "contents": "서울의 한 오피스텔에서 충전 중이던 신형 스마트폰에서 연기가 나고 불꽃이 튀었다는 신고가 접수됐다. 다행히 인명 피해는 없었으나 책상 일부가 그을렸다.",
        "category": "사회",
        "url": "https://news.test.com/soc/108",
        "company_name": "시티뉴스",
        "time": start_time + timedelta(days=7, hours=9),
        "author": "박사건 기자"
    },
    {
        "title": "유튜버 실험 영상 화제... \"충격 가하니 배터리 바로 폭발\"",
        "contents": "유명 IT 유튜버가 진행한 내구성 테스트에서 인피니티 셀에 약한 충격을 가하자마자 격렬한 화학 반응과 함께 폭발하는 장면이 공개돼 파장이 일고 있다.",
        "category": "IT/과학",
        "url": "https://news.test.com/it/109",
        "company_name": "튜브가이드",
        "time": start_time + timedelta(days=7, hours=14),
        "author": "김영상 기자"
    },
    {
        "title": "국토부, '인피니티 폰' 기내 반입 금지 검토 착수",
        "contents": "잇따른 발열 및 화재 신고에 국토교통부가 해당 기기의 항공기 내 반입 금지를 검토하고 있다. 항공사들은 승객들에게 기내 충전 자제를 권고하기 시작했다.",
        "category": "사회",
        "url": "https://news.test.com/soc/110",
        "company_name": "에어뉴스",
        "time": start_time + timedelta(days=8, hours=11),
        "author": "이비행 기자"
    },

    # ------------------------------------------------------------------
    # [Phase 3: 위기 확산과 은폐 의혹] (11~18)
    # ------------------------------------------------------------------
    {
        "title": "[속보] 미국 LA 쇼핑몰서 인피니티 폰 폭발... 3명 화상",
        "contents": "미국 LA의 대형 쇼핑몰 내 휴대폰 매장에서 전시 중이던 제품이 폭발해 직원과 고객 등 3명이 화상을 입고 병원으로 이송됐다. 사고 원인은 배터리 팽창으로 추정된다.",
        "category": "국제",
        "url": "https://news.test.com/wld/111",
        "company_name": "글로벌타임즈",
        "time": start_time + timedelta(days=9, hours=3),
        "author": "조아메리카 기자"
    },
    {
        "title": "넥스트에너지 주가 20% 급락... 환불 요청 쇄도",
        "contents": "해외 폭발 사고 소식이 전해지자 넥스트에너지 주가가 장 시작과 동시에 폭락했다. 대리점에는 환불을 요구하는 소비자들의 전화가 빗발치고 있다.",
        "category": "경제",
        "url": "https://news.test.com/eco/112",
        "company_name": "머니투데이",
        "time": start_time + timedelta(days=9, hours=10),
        "author": "황개미 기자"
    },
    {
        "title": "내부 고발자 등장 \"사측, 배터리 결함 알고도 출시 강행\"",
        "contents": "넥스트에너지 전 연구원이 익명 커뮤니티에 \"경영진이 테스트 단계에서 발생한 발화 문제를 묵살하고 출시 일정을 맞추라고 지시했다\"는 충격적인 글을 게시했다.",
        "category": "사회",
        "url": "https://news.test.com/soc/113",
        "company_name": "진실탐사",
        "time": start_time + timedelta(days=10, hours=8),
        "author": "김내부 기자"
    },
    {
        "title": "검찰, 넥스트에너지 본사 전격 압수수색... '결함 은폐' 수사",
        "contents": "검찰이 배터리 결함 은폐 의혹을 수사하기 위해 넥스트에너지 판교 본사와 연구소에 대한 압수수색에 들어갔다. 개발 일지와 이사회 회의록 확보에 주력하고 있다.",
        "category": "사회",
        "url": "https://news.test.com/soc/114",
        "company_name": "법률신문",
        "time": start_time + timedelta(days=11, hours=10),
        "author": "이검사 기자"
    },
    {
        "title": "미국 소비자안전위원회(CPSC), 인피니티 셀 '리콜 권고'",
        "contents": "미국 소비자 제품 안전 위원회가 넥스트에너지의 배터리에 대해 화재 위험이 크다며 즉각적인 사용 중단과 리콜을 공식 권고했다.",
        "category": "국제",
        "url": "https://news.test.com/wld/115",
        "company_name": "US리포트",
        "time": start_time + timedelta(days=11, hours=22),
        "author": "박워싱턴 기자"
    },
    {
        "title": "통신 3사, 인피니티 폰 판매 전면 중단 결정",
        "contents": "SK텔레콤, KT, LG유플러스 등 국내 이동통신 3사는 고객 안전을 위해 온·오프라인 매장에서 해당 제품의 판매를 즉시 중단한다고 밝혔다.",
        "category": "IT/과학",
        "url": "https://news.test.com/it/116",
        "company_name": "통신뉴스",
        "time": start_time + timedelta(days=12, hours=9),
        "author": "최통신 기자"
    },
    {
        "title": "공정위, 넥스트에너지 '허위 과장 광고' 조사 착수",
        "contents": "공정거래위원회는 넥스트에너지가 배터리 성능과 안전성을 부풀려 광고했는지 여부를 조사하기로 했다. 위반 사실이 확인되면 천문학적인 과징금이 부과될 수 있다.",
        "category": "경제",
        "url": "https://news.test.com/eco/117",
        "company_name": "경제감시",
        "time": start_time + timedelta(days=12, hours=14),
        "author": "나공정 기자"
    },
    {
        "title": "학계 분석 \"분리막 설계 결함이 원인... 100% 폭발 가능성\"",
        "contents": "배터리 전문가들이 사고 제품을 분석한 결과, 양극과 음극을 나누는 분리막 두께가 너무 얇아 미세한 충격에도 합선이 일어나는 치명적 설계 결함이 발견됐다고 주장했다.",
        "category": "IT/과학",
        "url": "https://news.test.com/sci/118",
        "company_name": "사이언스랩",
        "time": start_time + timedelta(days=13, hours=10),
        "author": "강박사 기자"
    },

    # ------------------------------------------------------------------
    # [Phase 4: 경영진 사퇴와 대규모 리콜] (19~24)
    # ------------------------------------------------------------------
    {
        "title": "넥스트에너지 CEO 대국민 사과 \"모든 제품 리콜하겠다\"",
        "contents": "박철수 넥스트에너지 대표가 기자회견을 열고 고개를 숙였다. 그는 \"모든 책임을 통감한다\"며 전 세계에 판매된 200만 대 전량을 리콜하고 환불하겠다고 발표했다.",
        "category": "경제",
        "url": "https://news.test.com/eco/119",
        "company_name": "종합뉴스",
        "time": start_time + timedelta(days=14, hours=11),
        "author": "이대표 기자"
    },
    {
        "title": "넥스트에너지 주식 거래 정지... 상장 폐지 심사 위기",
        "contents": "한국거래소는 경영진의 횡령 배임 혐의와 대규모 손실 발생 가능성을 이유로 넥스트에너지 주권 매매 거래를 정지시켰다. 소액 주주들의 피해가 우려된다.",
        "category": "경제",
        "url": "https://news.test.com/eco/120",
        "company_name": "주식데일리",
        "time": start_time + timedelta(days=14, hours=16),
        "author": "김증권 기자"
    },
    {
        "title": "피해자 집단 소송 모집 하루 만에 5만 명 돌파",
        "contents": "법무법인 '정의'가 주도하는 손해배상 집단소송에 피해자들이 구름처럼 몰려들었다. 소송 가액만 수천억 원에 달할 것으로 보여 국내 최대 규모의 소비자 소송이 예상된다.",
        "category": "사회",
        "url": "https://news.test.com/soc/121",
        "company_name": "시사매거진",
        "time": start_time + timedelta(days=15, hours=9),
        "author": "박변호 기자"
    },
    {
        "title": "경찰, 넥스트에너지 대표 구속 영장 신청 \"증거 인멸 우려\"",
        "contents": "수사당국은 박 대표가 내부 보고서를 파기하라고 지시한 정황을 포착하고 구속 영장을 신청했다. 기술총괄 부사장 등 임원 3명도 함께 입건됐다.",
        "category": "사회",
        "url": "https://news.test.com/soc/122",
        "company_name": "폴리스라인",
        "time": start_time + timedelta(days=16, hours=10),
        "author": "최형사 기자"
    },
    {
        "title": "리콜 비용만 3조 원... 넥스트에너지 파산설 '솔솔'",
        "contents": "전량 회수 및 폐기 비용, 피해보상금 등을 합치면 넥스트에너지의 현금 보유액을 훨씬 초과한다는 분석이 나왔다. 업계에서는 법정관리 신청이 임박했다는 소문이 돌고 있다.",
        "category": "경제",
        "url": "https://news.test.com/eco/123",
        "company_name": "비즈니스워치",
        "time": start_time + timedelta(days=17, hours=14),
        "author": "장회계 기자"
    },
    {
        "title": "협력 업체들의 눈물... \"부품 대금 못 받아 줄도산 위기\"",
        "contents": "넥스트에너지 1차 벤더들이 대금을 정산받지 못해 흑자 부도를 낼 처지에 놓였다. 정부는 피해 기업들을 위한 긴급 경영 안정 자금 지원을 검토 중이다.",
        "category": "경제",
        "url": "https://news.test.com/eco/124",
        "company_name": "중소기업뉴스",
        "time": start_time + timedelta(days=18, hours=10),
        "author": "이공장 기자"
    },

    # ------------------------------------------------------------------
    # [Phase 5: 사후 처리 및 시장의 변화] (25~30)
    # ------------------------------------------------------------------
    {
        "title": "삼성SDI·LG엔솔 반사이익... \"안전한 배터리 주문 폭주\"",
        "contents": "인피니티 셀 사태의 반사 효과로 기존 배터리 3사의 수주 잔고가 급증했다. 글로벌 완성차 및 IT 기업들이 '혁신'보다는 '검증된 안전'을 택하는 분위기다.",
        "category": "경제",
        "url": "https://news.test.com/eco/125",
        "company_name": "이데일리",
        "time": start_time + timedelta(days=20, hours=9),
        "author": "김시장 기자"
    },
    {
        "title": "환경부, '리콜 배터리' 폐기 대책 고심... 환경 오염 우려",
        "contents": "수거된 수백만 대의 배터리를 어떻게 처리할지가 새로운 문제로 떠올랐다. 매립 시 유해 물질 유출이 우려되어 특수 소각 처리가 필요하지만 시설이 부족한 실정이다.",
        "category": "사회",
        "url": "https://news.test.com/soc/126",
        "company_name": "그린뉴스",
        "time": start_time + timedelta(days=21, hours=11),
        "author": "나환경 기자"
    },
    {
        "title": "[사설] '빨리빨리'가 부른 참사, 제2의 넥스트에너지는 없어야",
        "contents": "이번 사태는 기초 기술 검증을 소홀히 한 채 성과주의에만 매몰된 한국 벤처 업계의 민낯을 보여주었다. 실패를 교훈 삼아 안전 규제를 대폭 강화해야 한다.",
        "category": "오피니언",
        "url": "https://news.test.com/opi/127",
        "company_name": "대한일보",
        "time": start_time + timedelta(days=22, hours=6),
        "author": "논설위원실"
    },
    {
        "title": "국회 '배터리 안전법' 본회의 통과... 인증 절차 대폭 강화",
        "contents": "이른바 '넥스트에너지 방지법'이 국회 본회의를 통과했다. 앞으로 신소재 배터리는 최소 1년 이상의 가혹 테스트를 거쳐야만 시장 출시가 허용된다.",
        "category": "정치",
        "url": "https://news.test.com/pol/128",
        "company_name": "국회일보",
        "time": start_time + timedelta(days=25, hours=15),
        "author": "박법안 기자"
    },
    {
        "title": "넥스트에너지, 결국 법정관리 신청... \"회생 노력하겠다\"",
        "contents": "감당할 수 없는 채무를 이기지 못한 넥스트에너지가 서울회생법원에 기업회생절차를 신청했다. 한때 시총 10조를 넘보던 유니콘 기업의 씁쓸한 퇴장이다.",
        "category": "경제",
        "url": "https://news.test.com/eco/129",
        "company_name": "경제투데이",
        "time": start_time + timedelta(days=28, hours=10),
        "author": "최마감 기자"
    },
    {
        "title": "전문가들 \"혁신 기술에 대한 '공포' 경계해야... R&D 위축 우려\"",
        "contents": "이번 사태로 인해 배터리 스타트업에 대한 투자가 얼어붙고 있다. 전문가들은 옥석 가리기와 함께 건전한 도전 정신마저 꺾여서는 안 된다고 조언했다.",
        "category": "IT/과학",
        "url": "https://news.test.com/it/130",
        "company_name": "테크인사이트",
        "time": start_time + timedelta(days=30, hours=9),
        "author": "이미래 기자"
    }
]