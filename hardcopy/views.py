from tempfile import NamedTemporaryFile
from django.http import FileResponse

from hardcopy import bytestring_to_pdf, bytestring_to_png


class PDFViewMixin(object):
    """View for rendering templates with context, to a pdf file
    using the headless browser."""

    template_name = None
    virtual_time_budget = None
    download_attachment = False
    template_context = {}

    def get_context_data(self, **kwargs):
        """Evaluate context if available, before rendering takes place."""
        if 'view' not in kwargs:
            kwargs['view'] = self
        if self.template_context:
            for k, v in self.template_context.items():
                kwargs[k] = v
        return kwargs

    def get_filename(self):
        return '{}.pdf'.format(self.template_name).replace('.html', '')

    def get(self, request, *args, **kwargs):
        """Render page to the specified output using the browser."""

        response = super(PDFViewMixin, self).get(request, *args, **kwargs)
        if 'html' in request.GET:
            return response

        response.render()
        output_file = NamedTemporaryFile()

        extra_args = {}
        if self.virtual_time_budget is not None:
            extra_args.update(
                {'virtual-time-budget': self.virtual_time_budget}
            )

        bytestring_to_pdf(response.content, output_file, **extra_args)

        # Return the file.
        response = FileResponse(output_file, content_type="application/pdf")

        atc = 'attachment;' if self.download_attachment else ''
        response['Content-Disposition'] = '{}filename="{}"'.format(
            atc, self.get_filename()
        )

        return response


class PNGViewMixin(object):
    """
    View for rendering templates to a PNG using headless Chrome
    """
    template_name = None
    virtual_time_budget = None
    download_attachment = False

    def get_filename(self):
        return '{}.png'.format(self.template_name).replace('.html', '')

    def get(self, request, *args, **kwargs):
        """
        Render page to the specified output filename using headless browser
        """
        response = super(PNGViewMixin, self).get(request, *args, **kwargs)
        if 'html' in request.GET:
            return response

        response.render()
        output_file = NamedTemporaryFile()

        extra_args = {}
        if self.virtual_time_budget is not None:
            extra_args.update({'virtual-time-budget': self.virtual_time_budget})

        bytestring_to_png(response.content, output_file, self.width, self.height, **extra_args)

        # Return the file
        response = FileResponse(output_file, content_type="image/png")

        atc = 'attachment;' if self.download_attachment else ''
        response['Content-Disposition'] = '{}filename="{}"'.format(atc, self.get_filename())

        return response
