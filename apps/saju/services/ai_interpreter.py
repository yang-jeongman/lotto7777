import json
import os

import anthropic


def interpret_saju(pillars, birth_info, ten_gods=None, elements=None):
    """Claude API로 사주 해석 + 로또 번호 생성"""

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError('ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.')

    # 사주 정보 텍스트 구성
    pillars_text = _format_pillars(pillars)
    ten_gods_text = _format_ten_gods(ten_gods) if ten_gods else ''
    elements_text = _format_elements(elements) if elements else ''
    birth_text = _format_birth(birth_info)

    prompt = f"""당신은 한국의 사주팔자(四柱八字) 전문가이자 로또 번호 추천 AI입니다.

아래 사용자의 사주팔자 정보를 분석하고, 금전운/재물운 중심으로 해석한 뒤, 사주의 오행 균형에 기반한 로또 행운번호를 추천해주세요.

## 사용자 정보
{birth_text}

## 사주팔자 (四柱八字)
{pillars_text}

{ten_gods_text}
{elements_text}

## 요청사항
아래 JSON 형식으로만 응답해주세요. 다른 텍스트 없이 JSON만 출력하세요.

{{
  "interpretation": {{
    "summary": "사주 한줄 요약 (예: 木이 강한 사주로 창의력과 성장의 기운이 넘칩니다)",
    "fortune": "금전운/재물운 해석 (3~4문장, 구체적이고 긍정적으로)",
    "element_analysis": "오행 분석 (어떤 오행이 강하고 약한지, 보완할 오행은 무엇인지)",
    "lucky_elements": ["행운의 오행1", "행운의 오행2"]
  }},
  "lucky_numbers": [
    {{
      "set_name": "오행 균형 세트",
      "numbers": [1, 2, 3, 4, 5, 6],
      "reason": "부족한 金 기운을 보충하는 번호 조합"
    }},
    {{
      "set_name": "재물운 강화 세트",
      "numbers": [7, 8, 9, 10, 11, 12],
      "reason": "정재/편재의 기운을 높이는 번호"
    }},
    {{
      "set_name": "대운 흐름 세트",
      "numbers": [13, 14, 15, 16, 17, 18],
      "reason": "현재 대운의 흐름에 맞춘 번호"
    }}
  ],
  "lucky_message": "오늘의 행운 메시지 (1줄, 사주 기반 개인화)"
}}

중요: 로또 번호는 반드시 1~45 사이의 서로 다른 숫자 6개를 정렬하여 제공하세요.
"""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model='claude-sonnet-4-5-20250929',
        max_tokens=1500,
        messages=[{'role': 'user', 'content': prompt}],
    )

    response_text = message.content[0].text.strip()

    # JSON 파싱 (```json 블록 처리)
    if response_text.startswith('```'):
        lines = response_text.split('\n')
        response_text = '\n'.join(lines[1:-1])

    return json.loads(response_text)


def _format_pillars(pillars):
    lines = []
    for key, label in [('year', '년주(年柱)'), ('month', '월주(月柱)'),
                        ('day', '일주(日柱)'), ('hour', '시주(時柱)')]:
        p = pillars.get(key, {})
        stem = p.get('stem', '?')
        branch = p.get('branch', '?')
        lines.append(f"- {label}: {stem}{branch}")
    return '\n'.join(lines)


def _format_ten_gods(ten_gods):
    if not ten_gods:
        return ''
    text = '## 십신 (十神)\n'
    for key, label in [('year', '년주'), ('month', '월주'),
                        ('day', '일주'), ('hour', '시주')]:
        god = ten_gods.get(key, '?')
        text += f"- {label}: {god}\n"
    return text


def _format_elements(elements):
    if not elements:
        return ''
    text = '## 오행 분포\n'
    for elem, count in elements.items():
        text += f"- {elem}: {count}개\n"
    return text


def _format_birth(birth_info):
    year = birth_info.get('year', '?')
    month = birth_info.get('month', '?')
    day = birth_info.get('day', '?')
    hour = birth_info.get('hour', '')
    minute = birth_info.get('minute', '')
    gender = '남성' if birth_info.get('gender') == 'M' else '여성'

    time_str = ''
    if hour != '' and hour is not None:
        time_str = f" {hour}시 {minute}분"

    return f"- 생년월일: {year}년 {month}월 {day}일{time_str}\n- 성별: {gender}"
