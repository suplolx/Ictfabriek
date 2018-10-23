from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.conf import settings
from .models import Factuur
import os

from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), dest=result, link_callback=fetch_recources)
    if not pdf.err:
        if 'factuur_nummer' in context_dict: 
            f = Factuur.objects.get(pk=context_dict['factuur_nummer'])
            pdf_file = ContentFile(result.getvalue())
            f.factuur_pdf_file.save(str(context_dict['factuur_nummer']) + '.pdf', pdf_file)
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def fetch_recources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path
