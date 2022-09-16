from django.core.files.temp import NamedTemporaryFile
from django.http import FileResponse

from hardcopy import bytestring_to_pdf, bytestring_to_png
from hardcopy.conf import settings


class BaseMixin:
    """_summary_

    :raises NotImplementedError: Override get_file_response
    :ivar template_name: Name of template file to use
    :vartype template_name: str
    :ivar virtual_time_budget: arg for chromium CLI
    :vartype virtual_time_budget: int
    :ivar download_attachment: Whether or not to automatically download the file
    :vartype download_attachment: bool
    :ivar file_extension: extension to append to filename
    :vartype file_extension: str
    :ivar window_size: arg for chromium
    """
    template_name = None
    virtual_time_budget = None
    download_attachment = False
    file_extension = None
    window_size = None

    def get_filename(self, extension='pdf'):
        """Get filename to use for output file

        :param extension: file extension to use, defaults to 'pdf'
        :type extension: str, optional
        :return: filename
        :rtype: str
        """
        return '{}.{}'.format(
            self.template_name.replace('.html', ''),
            self.file_extension
        )

    def get_file_response(self, content, output_file, extra_args):
        """Get the Django FileResponse object to use

        :param content: html content to render
        :type content: bytes
        :param output_file: file to write rendered output to
        :type output_file: object
        :param extra_args: extra args for chromium
        :type extra_args: dict, optional
        :raises NotImplementedError: Must override this function definition in subclass
        """
        raise NotImplementedError()

    def process_html_content(self, content):
        """
        Called after the template rendering, this method can be used to change
        the HTML before converting it to PDF or PNG (for example to replace
        relative images, css, or js file pathes to absolute pathes).

        :param content: html content to render
        :type content: bytes
        :return: content to be rendered
        :rtype: bytes
        """
        return content

    def get(self, request, *args, **kwargs):
        """Render page to the specified output using the browser.

        :param request: Django request object
        :type request: object
        :return: response object
        :rtype: object
        """

        response = super().get(request, *args, **kwargs)
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
    using the headless browser.

    :param BaseMixin: Base Class with common attributes and methods
    :type BaseMixin: object
    :ivar file_extension: Extension to append to filename
    :vartype file_extension: str
    """

    file_extension = 'pdf'

    def get_file_response(self, content, output_file, extra_args):
        bytestring_to_pdf(content, output_file, **extra_args)
        return FileResponse(output_file, content_type="application/pdf")


class PNGViewMixin(BaseMixin):
    """View for rendering templates to a PNG using headless Chrome

    :param BaseMixin: Base class with common attributes and methods
    :type BaseMixin: object
    :ivar file_extension: Extension to append to filename
    :vartype file_extension: str
    :ivar width: width for png
    :vartype width: int
    :ivar height: height for png
    :vartype height: int
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
