from tempfile import NamedTemporaryFile
from django.http import FileResponse

from hardcopy import bytestring_to_pdf


class PDFViewMixin(object):
    """
    View for rendering templates to a pdf using headless Chrome
    """
    template_name = None
    virtual_time_budget = None

    def get_filename(self):
        return '{}.pdf'.format(self.template_name).replace('.html', '')

    def get(self, request, *args, **kwargs):
        """
        Render page to the specified output filename using headless browser
        """
        response = super(PDFViewMixin, self).get(request, *args, **kwargs)
        if 'html' in request.GET:
            return response

        response.render()
        output_file = NamedTemporaryFile()

        extra_args = {}
        if self.virtual_time_budget is not None:
            extra_args.update({'virtual-time-budget': self.virtual_time_budget})

        bytestring_to_pdf(response.content, output_file, **extra_args)

        # Return the file
        response = FileResponse(output_file, content_type="application/pdf")

        atc = 'attachment;' if self.download_attachment else ''
        response['Content-Disposition'] = '{}filename="{}"'.format(atc, self.get_filename())

        return response
