import json
import logging

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from .services.ai_interpreter import interpret_saju

logger = logging.getLogger(__name__)


class SajuPageView(TemplateView):
    template_name = 'saju/index.html'


class SajuInterpretAPIView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

        pillars = data.get('pillars')
        birth_info = data.get('birth_info')
        ten_gods = data.get('ten_gods')
        elements = data.get('elements')

        if not pillars or not birth_info:
            return JsonResponse({'error': '사주 정보가 필요합니다.'}, status=400)

        try:
            result = interpret_saju(
                pillars=pillars,
                birth_info=birth_info,
                ten_gods=ten_gods,
                elements=elements,
            )
            return JsonResponse(result)
        except Exception as e:
            logger.exception('사주 해석 API 오류')
            return JsonResponse({'error': '해석 중 오류가 발생했습니다.'}, status=500)
