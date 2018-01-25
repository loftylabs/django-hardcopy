from django.core.files.temp import NamedTemporaryFile
from django.http import FileResponse

from hardcopy import bytestring_to_pdf, bytestring_to_png
from hardcopy.conf import settings


class BaseMixin(object):
    template_name = None
    virtual_time_budget = None
    download_attachment = False
    file_extension = None
    window_size = None

    def get_filename(self, extension='pdf'):
        return '{}.{}'.format(
            self.template_name.replace('.html', ''),
            self.file_extension
        )

    def get_file_response(self, content, output_file, extra_args):
        raise NotImplementedError()

    def process_html_content(self, content):
        """
        Called after the template rendering, this method can be used to change
        the HTML before converting it to PDF or PNG (for example to replace
        relative images, css, or js file pathes to absolute pathes).
        """
        return content

    def get(self, request, *args, **kwargs):
        """Render page to the specified output using the browser."""

        response = super(BaseMixin, self).get(request, *args, **kwargs)
        if 'html' in request.GET:
            return response

        response.render()
        content = self.process_html_content(response.content)

        # Get the file response
        extra_args = {}
        if self.virtual_time_budget is not None:
            extra_args.update(
                {'virtual-time-budget': self.virtual_time_budget}
            )

        if 'window_size' not in extra_args:
            if self.window_size:
                window_size = self.window_size
            else:
                window_size = settings.CHROME_WINDOW_SIZE
            extra_args.update({'window-size': window_size})

        output_file = NamedTemporaryFile()
        response = self.get_file_response(content, output_file, extra_args)

        atc = 'attachment;' if self.download_attachment else ''
        response['Content-Disposition'] = '{}filename="{}"'.format(
            atc, self.get_filename()
        )

        return response


class PDFViewMixin(BaseMixin):
    """View for rendering templates with context, to a pdf file
    using the headless browser."""

    file_extension = 'pdf'

    def get_file_response(self, content, output_file, extra_args):
        bytestring_to_pdf(content, output_file, **extra_args)
        return FileResponse(output_file, content_type="application/pdf")


class PNGViewMixin(BaseMixin):
    """
    View for rendering templates to a PNG using headless Chrome
    """
    file_extension = 'png'
    width = 1920
    height = 1080

    def get_file_response(self, content, output_file, extra_args):
        if self.width and self.height:
            extra_args.update({
                'window-size': '{},{}'.format(self.width, self.height)
            })
        bytestring_to_png(content, output_file, **extra_args)
        return FileResponse(output_file, content_type="image/png")
