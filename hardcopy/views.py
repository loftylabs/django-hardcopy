import subprocess
from tempfile import NamedTemporaryFile

from django.http import FileResponse

from hardcopy.conf import hc_settings


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

        input_file = NamedTemporaryFile()
        output_file = NamedTemporaryFile()

        input_file.write(response.content)
        input_file.flush()

        chrome_args = [
            hc_settings.PATH_TO_CHROME,
            '--headless',
            '--print-to-pdf="{}"'.format(output_file.name),
            '--disable-gpu',
        ]

        # Optional args
        if self.virtual_time_budget is not None:
            chrome_args.append('--virtual-time-budget={}'.format(self.virtual_time_budget))

        # Path to the input data
        chrome_args.append('file://{}'.format(input_file.name))
        subprocess.call(" ".join(chrome_args), shell=True)
        input_file.close()
        output_file.seek(0)


        # Return the file
        response = FileResponse(output_file, content_type="application/pdf")
        response['Content-Disposition'] = 'filename="{}"'.format(self.get_filename())
        return response
