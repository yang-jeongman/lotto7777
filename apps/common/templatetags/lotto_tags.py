from django import template

register = template.Library()


@register.filter
def ball_color(number):
    """로또 볼 번호 범위별 배경색 반환"""
    try:
        n = int(number)
    except (ValueError, TypeError):
        return '#666666'

    if 1 <= n <= 10:
        return '#FFC107'  # 노랑
    elif 11 <= n <= 20:
        return '#2196F3'  # 파랑
    elif 21 <= n <= 30:
        return '#F44336'  # 빨강
    elif 31 <= n <= 40:
        return '#9E9E9E'  # 회색
    elif 41 <= n <= 45:
        return '#4CAF50'  # 초록
    return '#666666'


@register.filter
def ball_text_color(number):
    """볼 번호에 따른 텍스트 색상"""
    try:
        n = int(number)
    except (ValueError, TypeError):
        return '#ffffff'

    if 1 <= n <= 10:
        return '#333333'
    return '#ffffff'


@register.filter
def intcomma_kr(value):
    """한국식 천단위 콤마"""
    try:
        return '{:,}'.format(int(value))
    except (ValueError, TypeError):
        return value
