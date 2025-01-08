from django.views.generic.base import TemplateView

from products.models import AllProducts


class HomePage(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = AllProducts.objects.order_by('-id')[:12]
        return context
