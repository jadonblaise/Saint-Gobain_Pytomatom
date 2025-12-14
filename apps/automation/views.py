from django.conf import settings
from django.urls import reverse
from django.views.generic import TemplateView

from core.views.mixins import CacheMixin


class VueAutomationFrontendInDjangoView(CacheMixin, TemplateView):
    template_name = "automation/frontend.html.djt"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["django_message"] = "Welcome to Pytomatom Order Management Automation"
        context[
            "url_download_orderbooks"
        ] = f'{settings.PROJECT_FQDN.geturl()}{reverse("orderbooks:automation-download")}'
        context[
            "url_download_demandforecast"
        ] = f'{settings.PROJECT_FQDN.geturl()}{reverse("demandforecast:automation-download")}'
        return context
