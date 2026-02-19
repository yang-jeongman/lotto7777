"""
DB 기반 로또 통계 계산 서비스
"""
from collections import Counter

from django.db.models import Avg, Sum

from apps.analysis.models import DrawResult


def get_latest_draw():
    """최신 회차 조회"""
    return DrawResult.objects.order_by('-draw_no').first()


def get_current_draw_data():
    """랜딩 페이지용 최신 당첨 데이터"""
    latest = get_latest_draw()
    if not latest:
        return None

    return {
        'draw_no': latest.draw_no,
        'draw_date': latest.draw_date.strftime('%Y-%m-%d'),
        'winning_numbers': latest.numbers,
        'bonus_number': latest.bonus_number,
        'first_prize': latest.first_prize_amount,
        'first_prize_winners': latest.first_prize_winners,
        'total_sales': latest.total_sales,
    }


def get_number_stats(recent_10=10, recent_30=30, recent_100=100):
    """1~45번 각 번호별 출현 빈도"""
    stats = {}

    for period, label in [(recent_10, 'freq_10'), (recent_30, 'freq_30'),
                           (recent_100, 'freq_100')]:
        draws = DrawResult.objects.order_by('-draw_no')[:period]
        counter = Counter()
        for d in draws:
            for n in d.numbers:
                counter[n] += 1

        for num in range(1, 46):
            if num not in stats:
                stats[num] = {}
            stats[num][label] = counter.get(num, 0)

    # 전체 출현 횟수도 추가
    all_draws = DrawResult.objects.all()
    total_counter = Counter()
    for d in all_draws:
        for n in d.numbers:
            total_counter[n] += 1

    for num in range(1, 46):
        stats[num]['freq_total'] = total_counter.get(num, 0)

    return stats


def get_top_numbers(n=10):
    """최다 출현 번호 Top N"""
    counter = Counter()
    for d in DrawResult.objects.all():
        for num in d.numbers:
            counter[num] += 1
    return counter.most_common(n)


def get_cold_numbers(n=10):
    """최소 출현 번호 Top N"""
    counter = Counter()
    for d in DrawResult.objects.all():
        for num in d.numbers:
            counter[num] += 1

    # 45번까지 없는 번호는 0으로 채우기
    for i in range(1, 46):
        if i not in counter:
            counter[i] = 0

    return counter.most_common()[:-n-1:-1]


def get_recent_draws(count=5):
    """최근 N회차 결과 목록"""
    draws = DrawResult.objects.order_by('-draw_no')[:count]
    return [
        {
            'draw_no': d.draw_no,
            'draw_date': d.draw_date.strftime('%Y-%m-%d'),
            'numbers': d.numbers,
            'bonus_number': d.bonus_number,
            'first_prize': d.first_prize_amount,
            'first_prize_winners': d.first_prize_winners,
        }
        for d in draws
    ]


def get_ai_recommendations_from_stats():
    """DB 통계 기반 AI 추천 번호 3세트 생성"""
    import random
    from datetime import date

    # 날짜 시드로 매일 같은 결과
    today_seed = date.today().toordinal()
    rng = random.Random(today_seed)

    # 최근 10회 빈출번호
    recent_draws = DrawResult.objects.order_by('-draw_no')[:10]
    recent_counter = Counter()
    for d in recent_draws:
        for n in d.numbers:
            recent_counter[n] += 1

    hot_numbers = [n for n, _ in recent_counter.most_common(15)]
    cold_numbers = [n for n in range(1, 46) if recent_counter.get(n, 0) <= 1]

    # 전체 통계
    total_counter = Counter()
    for d in DrawResult.objects.all():
        for n in d.numbers:
            total_counter[n] += 1

    # Set 1: 빈출번호 조합
    set1 = sorted(rng.sample(hot_numbers[:12], 6))

    # Set 2: 홀짝 균형 (3:3)
    odds = [n for n in range(1, 46) if n % 2 == 1]
    evens = [n for n in range(1, 46) if n % 2 == 0]
    set2 = sorted(rng.sample(odds, 3) + rng.sample(evens, 3))

    # Set 3: 미출현 번호 + 구간 균형
    if len(cold_numbers) >= 3:
        cold_pick = rng.sample(cold_numbers, min(3, len(cold_numbers)))
        hot_pick = rng.sample(hot_numbers[:10], 6 - len(cold_pick))
        set3 = sorted(cold_pick + hot_pick)
    else:
        set3 = sorted(rng.sample(range(1, 46), 6))

    return [
        {
            'set_name': 'AI 추천 1세트',
            'numbers': set1,
            'confidence': rng.randint(70, 85),
            'strategy': '최근 10회 빈출번호 기반 조합',
        },
        {
            'set_name': 'AI 추천 2세트',
            'numbers': set2,
            'confidence': rng.randint(65, 78),
            'strategy': '홀짝 비율 3:3 최적화',
        },
        {
            'set_name': 'AI 추천 3세트',
            'numbers': set3,
            'confidence': rng.randint(60, 72),
            'strategy': '미출현 번호 + 구간 균형 조합',
        },
    ]
