import random
from datetime import date

from django.views.generic import TemplateView

from apps.analysis.models import DrawResult
from .services.lotto_stats import (
    get_current_draw_data,
    get_number_stats,
    get_ai_recommendations_from_stats,
    get_recent_draws,
)
from .services.mock_data import (
    CURRENT_DRAW, AI_RECOMMENDATIONS, NUMBER_STATS,
    LUCKY_STORES, USER_LEVELS, SERVICE_STAGES,
    DAILY_QUOTES, COMMUNITY_POSTS,
)


class LandingPageView(TemplateView):
    template_name = 'landing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today_seed = date.today().toordinal()
        rng = random.Random(today_seed)
        daily_numbers = sorted(rng.sample(range(1, 46), 6))

        # DB에 데이터가 있으면 실데이터, 없으면 mock 폴백
        has_data = DrawResult.objects.exists()

        if has_data:
            current_draw = get_current_draw_data()
            number_stats = get_number_stats()
            ai_recommendations = get_ai_recommendations_from_stats()
            recent_draws = get_recent_draws(5)
        else:
            current_draw = CURRENT_DRAW
            number_stats = NUMBER_STATS
            ai_recommendations = AI_RECOMMENDATIONS
            recent_draws = []

        context.update({
            'current_draw': current_draw,
            'ai_recommendations': ai_recommendations,
            'number_stats': number_stats,
            'lucky_stores': LUCKY_STORES,
            'user_levels': USER_LEVELS,
            'service_stages': SERVICE_STAGES,
            'daily_numbers': daily_numbers,
            'daily_quote': rng.choice(DAILY_QUOTES),
            'community_posts': COMMUNITY_POSTS,
            'recent_draws': recent_draws,
        })
        return context
