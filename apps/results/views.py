from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from apps.analysis.models import DrawResult


class ResultListView(ListView):
    model = DrawResult
    template_name = 'results/list.html'
    context_object_name = 'draws'
    paginate_by = 20
    ordering = ['-draw_no']


class ResultDetailView(DetailView):
    model = DrawResult
    template_name = 'results/detail.html'
    context_object_name = 'draw'

    def get_object(self):
        return get_object_or_404(DrawResult, draw_no=self.kwargs['draw_no'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        draw = self.object

        # 이전/다음 회차
        context['prev_draw'] = DrawResult.objects.filter(
            draw_no=draw.draw_no - 1
        ).first()
        context['next_draw'] = DrawResult.objects.filter(
            draw_no=draw.draw_no + 1
        ).first()

        return context
