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


def get_number_detail_stats(number):
    """특정 번호(1~45)의 상세 통계"""
    all_draws = DrawResult.objects.order_by('-draw_no')
    total_draws = all_draws.count()

    appearances = {'total': 0, 'last_10': 0, 'last_30': 0, 'last_100': 0}
    last_appearance_draw = None
    co_occurrence = Counter()

    for i, d in enumerate(all_draws):
        nums = d.numbers
        if number in nums:
            appearances['total'] += 1
            if i < 10:
                appearances['last_10'] += 1
            if i < 30:
                appearances['last_30'] += 1
            if i < 100:
                appearances['last_100'] += 1
            if last_appearance_draw is None:
                last_appearance_draw = d
            for n in nums:
                if n != number:
                    co_occurrence[n] += 1

    rate_30 = appearances['last_30'] / 30 if total_draws >= 30 else None
    rate_100 = appearances['last_100'] / 100 if total_draws >= 100 else None

    if rate_30 is not None and rate_100 is not None:
        if rate_30 > rate_100 * 1.2:
            trend = 'increasing'
        elif rate_30 < rate_100 * 0.8:
            trend = 'decreasing'
        else:
            trend = 'stable'
    else:
        trend = 'unknown'

    top_co = co_occurrence.most_common(5)

    return {
        'number': number,
        'total_appearances': appearances['total'],
        'total_draws': total_draws,
        'last_10': appearances['last_10'],
        'last_30': appearances['last_30'],
        'last_100': appearances['last_100'],
        'last_draw_no': last_appearance_draw.draw_no if last_appearance_draw else None,
        'last_draw_date': last_appearance_draw.draw_date.strftime('%Y-%m-%d') if last_appearance_draw else None,
        'trend': trend,
        'co_occurrence': [{'number': n, 'count': c} for n, c in top_co],
    }


def get_extended_ai_recommendations(count=10):
    """10세트 다양한 전략별 AI 추천 번호 생성"""
    import random
    from datetime import date

    today_seed = date.today().toordinal()
    rng = random.Random(today_seed)

    recent_draws = DrawResult.objects.order_by('-draw_no')[:30]
    recent_counter = Counter()
    for d in recent_draws:
        for n in d.numbers:
            recent_counter[n] += 1

    hot_numbers = [n for n, _ in recent_counter.most_common(20)]
    cold_numbers = [n for n in range(1, 46) if recent_counter.get(n, 0) <= 2]
    all_nums = list(range(1, 46))
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]

    strategies = [
        ('빈출번호 조합', lambda: sorted(rng.sample(hot_numbers[:12], 6))),
        ('홀짝 3:3 균형', lambda: sorted(rng.sample([n for n in all_nums if n % 2 == 1], 3) + rng.sample([n for n in all_nums if n % 2 == 0], 3))),
        ('미출현 콜드넘버', lambda: sorted(rng.sample(cold_numbers, min(3, len(cold_numbers))) + rng.sample(hot_numbers[:10], max(3, 6 - min(3, len(cold_numbers)))))),
        ('고저 균형 (1-22 vs 23-45)', lambda: sorted(rng.sample(range(1, 23), 3) + rng.sample(range(23, 46), 3))),
        ('연번 포함 조합', lambda: _consecutive_set(rng)),
        ('구간별 균등 분배', lambda: sorted([rng.choice(range(s, e + 1)) for s, e in [(1, 9), (10, 18), (19, 27), (28, 36), (37, 45)]] + [rng.choice(all_nums)])),
        ('최근 1등 패턴 기반', lambda: sorted(rng.sample(hot_numbers[:15], 6))),
        ('소수 번호 중심', lambda: sorted(rng.sample(primes, 4) + rng.sample([n for n in all_nums if n not in primes], 2))),
        ('끝자리 분산 전략', lambda: _last_digit_spread(rng)),
        ('황금비율 간격 조합', lambda: _golden_ratio_set(rng)),
    ]

    results = []
    for i, (name, gen_fn) in enumerate(strategies[:count]):
        nums = gen_fn()
        # 중복 제거 보장
        nums = sorted(set(nums))
        while len(nums) < 6:
            extra = rng.choice(all_nums)
            if extra not in nums:
                nums.append(extra)
        nums = sorted(nums[:6])
        results.append({
            'set_name': f'AI 추천 {i + 1}세트',
            'numbers': nums,
            'confidence': rng.randint(60, 85),
            'strategy': name,
        })
    return results


def _consecutive_set(rng):
    """연번 포함 세트 생성"""
    start = rng.randint(1, 43)
    pair = sorted([start, start + 1])
    others = [n for n in range(1, 46) if n not in pair]
    return sorted(pair + rng.sample(others, 4))


def _last_digit_spread(rng):
    """끝자리 분산 (0~9 중 6개 끝자리)"""
    by_last = {}
    for n in range(1, 46):
        d = n % 10
        by_last.setdefault(d, []).append(n)
    chosen_digits = rng.sample(list(by_last.keys()), min(6, len(by_last)))
    return sorted([rng.choice(by_last[d]) for d in chosen_digits])


def _golden_ratio_set(rng):
    """황금비율 간격 (약 7간격)"""
    start = rng.randint(1, 10)
    nums = []
    n = start
    while n <= 45 and len(nums) < 6:
        nums.append(n)
        n += rng.randint(6, 8)
    while len(nums) < 6:
        extra = rng.randint(1, 45)
        if extra not in nums:
            nums.append(extra)
    return sorted(nums[:6])


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
