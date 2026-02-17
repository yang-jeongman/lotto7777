import random
from datetime import date

from django.views.generic import TemplateView

from .services.mock_data import (
    CURRENT_DRAW, AI_RECOMMENDATIONS, NUMBER_STATS,
    LUCKY_STORES, USER_LEVELS, SERVICE_STAGES,
    DAILY_QUOTES, COMMUNITY_POSTS,
)


class LandingPageView(TemplateView):
    template_name = 'landing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 날짜 기반 시드로 매일 다른 행운번호 생성
        today_seed = date.today().toordinal()
        rng = random.Random(today_seed)
        daily_numbers = sorted(rng.sample(range(1, 46), 6))

        context.update({
            'current_draw': CURRENT_DRAW,
            'ai_recommendations': AI_RECOMMENDATIONS,
            'number_stats': NUMBER_STATS,
            'lucky_stores': LUCKY_STORES,
            'user_levels': USER_LEVELS,
            'service_stages': SERVICE_STAGES,
            'daily_numbers': daily_numbers,
            'daily_quote': rng.choice(DAILY_QUOTES),
            'community_posts': COMMUNITY_POSTS,
        })
        return context
