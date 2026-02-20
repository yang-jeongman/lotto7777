import random
from datetime import date

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from apps.analysis.models import DrawResult
from .services.lotto_stats import (
    get_current_draw_data,
    get_number_stats,
    get_ai_recommendations_from_stats,
    get_recent_draws,
    get_number_detail_stats,
    get_extended_ai_recommendations,
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

        # 커뮤니티 최신 게시글 (실데이터 or mock)
        community_posts = COMMUNITY_POSTS
        try:
            from apps.community.models import Post
            real_posts = Post.objects.select_related('board', 'author__profile').all()[:3]
            if real_posts.exists():
                community_posts = real_posts
        except Exception:
            pass

        context.update({
            'current_draw': current_draw,
            'ai_recommendations': ai_recommendations,
            'number_stats': number_stats,
            'lucky_stores': LUCKY_STORES,
            'user_levels': USER_LEVELS,
            'service_stages': SERVICE_STAGES,
            'daily_numbers': daily_numbers,
            'daily_quote': rng.choice(DAILY_QUOTES),
            'community_posts': community_posts,
            'recent_draws': recent_draws,
        })
        return context


class NumberDetailAPIView(View):
    """번호별 상세 통계 JSON API"""
    def get(self, request, number):
        if not (1 <= number <= 45):
            return JsonResponse({'error': 'Invalid number'}, status=400)
        stats = get_number_detail_stats(number)
        return JsonResponse(stats)


class MoreRecommendationsView(TemplateView):
    template_name = 'landing/more_recommendations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recommendations'] = get_extended_ai_recommendations(10)
        return context
