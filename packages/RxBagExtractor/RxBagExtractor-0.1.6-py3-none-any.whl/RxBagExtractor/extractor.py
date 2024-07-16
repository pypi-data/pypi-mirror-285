import pandas as pd
import re


def process_ocr_text(ocr_text, stopwords, patterns_exact, patterns_include):
    # OCR 텍스트를 줄바꿈 기준으로 나눈다
    lines = ocr_text.split('\n')

    # 처리된 결과를 저장할 리스트
    processed_lines = []


    # 각 줄을 순회하면서 조건에 맞는지 확인
    for line in lines:
        # 공백 제거
        # stripped_line = line.replace(" ", "")
        stripped_line = re.sub(r"[*!✓•?\s]", "", line)

        # 스탑워드 검사 후, 스탑워드가 포함되어 있으면 해당 라인을 건너뛰기
        if any(word in stripped_line for word in stopwords):
            continue
        
        # 정규 표현식을 사용하여 날짜, 숫자, 번호 패턴이 매치되면 건너뛰기
        if any(pattern.fullmatch(stripped_line) for pattern in patterns_exact):
            continue
        # 정규 표현식 포함되면
        if any(pattern.search(stripped_line) for pattern in patterns_include):
            continue
        
        # 한 글자인 경우도 건너뛰기
        if len(stripped_line) == 1:
            continue
        
        # 위험! 문제 있을시 삭제
        if stripped_line not in ['자모', '뇌선', '얄액', '티씰', '쿨정'] and len(stripped_line) == 2:
            continue

        if (re.search('[\uAC00-\uD7A3]', stripped_line) is None and 
            len(stripped_line) <= 5 and 
            stripped_line not in ['Prera', 'CTM', 'AlboQ', 'BAROS', 'Bibag', 'Vilex', 'S-Gel', 'Jamo']):
            continue

        # 위 조건에 모두 해당하지 않는 줄만 최종 결과에 추가
        processed_lines.append(line)
    # 한 줄만 남김. 순서는 달려져도 상관 없을 거 같아서 이렇게
    # return list(set(processed_lines))
    return processed_lines


def extractor(ocr_text, stopwords_customize=[], patterns_exact_customize=[], patterns_include_customize=[]):

    stopwords = ['약국','약사','병원','복용','용법','TEL.','처방전','번호','야간', '공휴일', '조제약',
    '복약', '안내', '아침','점심','저녁','취침','식사','식전', '식후','공복','계산서','영수증','경수중','약제비','투여','보험',
	# '비급', '급여','금여',
	'수납금액', '투약', '업장','약품명','횟수','흡연법','주으','두세요',
    '서울시','대전시','구미시','둔산','강남구','성남','하남','고양','충주','마포','노원구','울산광역','용인','부산시','강릉','일산','충청남도','경상북도','전라남도', '제주특', '전북특','원내동','전라북도','전라도','당산로',
    '스마트폰','안내문','청구', '나이', '성별','이름','성명','내방일','내원일',
    'KIOSK','키오스크','주의사항','약품사진','사업자','의원','조제일자','부담금','전•간후','씩','시간마다','봉투','비정상적',
    '공휴','조제일','환자','전문가','천천히','감염','치료제','없습니','말합니','들어있는','전액본인','발행','증상','Image',
    '냉장','냉동','별지','개선','용량','있습니','불립니','금액','기상후','신문','zZZ',
    '일분','입니','국민건강','건강보','조제','처방의약품','명칭','보호하고','으로써','으로서','약효',
    '시행규칙','본인','현금','총액','제일자','임산부','상의하세','운전','영업소','기분','장애',
    '발진주의','부족주의','[앞]','[뒤]','군업을','이미지','개선하는','의사지시','의사의지시','호흡곤란',
    '상온','실온','완화시켜','혈관','통해','만료일','결핍증','영양소','성분으로',
    '일어나세','효능','부당금','습기가','서늘한','면역력','어지러','좋습니','장시간',
    '주의하','중단하','피임하','받으세','부작용','갑작스','시간에','가급적','나타날','십시오','시오.',
    '심하','유해한','만약','스캔하','구토','경우,','름:','두통','홍동','동맥폐색증','시분','카드:',
    '홈페이지','www','합니','이다.','수량','첨가된','/남','/여','경감','가기',
    '차광재','정장제','습기','피하여','가려움','두드러기','질환',
    '먹는','과립상','녹여','순서대','표시대','통증','상가','바이러스의',
    '국세에','마세요','졸음','차광','보관','금주','가능','수있','일자','확인',
    '자성','현원','굶','특례','공제','신청','증빙','발급','접촉','정출','입구','자세한','합계','합겨',
    '나요','정확','상호','현-금','자르는','약은','나:','일사:','(남)','(여)','(녀)','대표','전화',
    '시럽은','기간','보건고','구분','요구','기호','월일','시각','번길','주세요','확장','부남',
    '가장','안양','일황','치료','주의력','망상','환각','교부','영수종',
    '강박','공황','습니다','접기','유지비','곤란','유발','작용','특이','사법','해소하',
    '체온','의료인','참고','mail','e-tmil','여백','대체시','내역','조재','보힘','치방전','의약품의',
    '면허','기준','보건복지','부약','번호','분류','의료보','정보인','시럽은','기관','약당','서식',
    '원외',')일간','기방','수납','법호','원금','사용활','의료비','수당','후수-',
    '의표','주소','쳠누','약일수','형칭','명칭','달콤','쓴','쓰면','색의','내지','다.',
    '끝','소제','차단','장방','약중','기한','은전','IR조작','것수','특용','계신서','역북',
    '수출에','비용을','평상','소아과','청소년','분비','목적','음주','흡연','삼가세','약품사','책시','착시','섭취','한승','로운','질병','서명',
    '불가','명청','명칭','시식','QR','임신','즉시','진료','관리','비뇨의학','총량','좋고'
    # '감기','중추','천식', '진해', '비염','콧물','간질','항생제','항히스타민','성기능','설사','항알러지','염증','아토피','진통제','거담제','안정제','비만','수면','기관지','호흡','위장운동','객담
    '종별','내용등','월말','ㆀ0',"사:","Galaxy","①","②","③","ww","1/1","『","』",
    "부속","처방의","소재","부담률","변경","원내","KD코드","문의","안됨","연라처",
    "외래","내과","유형","의학과",".com","naver","약품의","압니다","제출","처방일",".kr",
    "피부과","대의","약제","전속","든지","투값","진단코드","24시간","rescription","요양",'특별시','책임','백상지'
    "따로","포장",'비뇨','용이하','E-Mai','부과'

    ] + stopwords_customize
    
    patterns_exact = [
        re.compile(r"^\d+(회|일)$"),
        re.compile(r"^(카드|주사제|의사|일수|시럽|아연|침전|납은|조시|팩스면호|하루|정차|대체|구문|처방|약품|페이지|급여|비급여|ltab)$"),
        re.compile(r"\(.+\)"),
        re.compile(r"[\d+,.]+\s*원"),
        #re.compile(r"^[^\uAC00-\uD7A3]*$"),
        # re.compile(r"\d{4}년\d{2}\.월\d{2}일"),
        re.compile(r"\d{1,2}월"),
        re.compile(r"\d{1,2}일/"),
        re.compile(r"^것이$"),
        re.compile(r"[\uAC00-\uD7A3]+\)"),
        re.compile(r"[\uAC00-\uD7A3]+\),"),
        re.compile(r"제\d+호?"),
        re.compile(r"\d+(\.\d+)?\s*tab", re.IGNORECASE),
        re.compile(r"itab", re.IGNORECASE),
        re.compile(r'IT', re.IGNORECASE),
        re.compile(r"년\d{1,2}월"),
        re.compile(r"\d{1,2}T", re.IGNORECASE),
        re.compile(r"1일총"),
        re.compile(r"\d{1,2}?비급여"),
        re.compile(r"\d{1,2}?급여"),
        re.compile(r"[\uAC00-\uD7A3]{2}정제")

        # 한글이 1자만 포함됨 (약물명이 잘못 인식되어서 한 글자만 있을 때 많음)
        # re.compile(r"^(?:[^\uAC00-\uD7A3]*)([\uAC00-\uD7A3])(?:[^\uAC00-\uD7A3]*)$")

    ] + patterns_exact_customize
    
    patterns_include = [
        re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{4}\d{2}\d{2}-\d{4}$|^\d+-\d+-\d+$|^[0-9,.]+$"),
        re.compile(r"^[a-zA-Z]*\.?\d{2,3}-\d{3,4}-\d{4}$"),
        re.compile(r"\d{4}년"),
        re.compile(r"\d+층"),
        re.compile(r"만\d+세"),
        re.compile(r"\d{4}-\d{2}-\d{2}"),
        re.compile(r"\d{6}-\d{1}"),
        re.compile(r"\d{4}-\d{4}"),
        re.compile(r"\d{3}-\d{3}-\d{4}"),
        re.compile(r"\d{2,4}년\d{1,2}월?\d{1,2}일"),
        re.compile(r"\d+일+\d+(회|호)"),
        re.compile(r"\d+회+\d+(정|일)"),
        re.compile(r"대로\d+"),
        re.compile(r"\d+([-.]\d+)*호"),
        re.compile(r"\d+제+\d"),
        re.compile(r"\(?[0-9]{2,3}\)[0-9]{3}-[0-9]{4}"),
        re.compile(r"[\uAC00-\uD7A3]+도+[\uAC00-\uD7A3]+시"),
        re.compile(r"[\uAC00-\uD7A3]+동+[0-9]+-[0-9]+번지"),
        re.compile(r"[\uAC00-\uD7A3]+(?:특별시|광역시)+[\uAC00-\uD7A3]+구"),
        re.compile(r"[\uAC00-\uD7A3]로+[0-9]+"),
        re.compile(r"\d{4}/\d{2}/\d{2}"),
        re.compile(r"\d{3,4}(_|-)\d{2,4}(_|-)\d{2,4}"),
        re.compile(r"\d{3,4}(_|-)\d{4}"),
        re.compile(r"\d{2,4}mmx\d{2,4}mm")
    ] + patterns_include_customize


    processed_ocr_text = process_ocr_text(ocr_text, stopwords, patterns_exact, patterns_include)
    return "\n".join(processed_ocr_text)
