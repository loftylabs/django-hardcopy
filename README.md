# django-hardcopy:  Render PDFs and PNGs in Django with headless Chrome

Chrome [introduced headless mode in v59](https://developers.google.com/web/updates/2017/04/headless-chrome) opening the possibility of using Chrome as a fast and elegant way of generating PDF data or PNG screenshots programatically via HTML.  `django-hardcopy` is an alternative to other projects which leverage `wkhtmltopdf`, a great tool but one that lacks the portability, ease of installation, the performance, and reliability of Chrome.


## Requirements
- Django
- Chrome, Chromium, or Chrome Canary >= v59
- Currently only tested against Django 1.10+ and Python 3.6 (other versions may be supported, submit an issue if not!)

## Installation

Install the library:

    pip install django-hardcopy
    
Install Chrome or a derivative:

    apt-get install chromium-browser
    
Set your Chrome path (optional):

    # settings.py
    
    CHROME_PATH = '/path/to/chrome-or-chromium'
    
This can be useful if you want to use `chrome-canary` or `chromium-browser` (available by default in Ubuntu).  Django-hardcopy will attempt to smartly default the appropriate chrome path for your os. If you're on Mac OSX, just upgrade to the latest Chrome and you're good to go!

Set the rendering window size (optional, default: 1280,720):
 
    # settings.py
    
    CHROME_WINDOW_SIZE = '800,600'

## Usage

The easiest way to use `django-hardcopy` is to use its CBV mixin:

```python
from django.views.generic import TemplateView
from hardcopy.views import PDFViewMixin, PNGViewMixin


class MyPDFView(PDFViewMixin, TemplateView):
    template_name = "pdf_me.html"

class MyPNGView(PNGViewMixin, TemplateView):
    template_name = "png_me.html"
    height = '1080'
    width = '1920'

```

It works with any Django Class Based View, and implements PDF or PNG rendering on the `GET` HTTP method. Further, if the `?html` querystring variable is provided the mixin will render the view normally for designing and debugging of the raw HTML.  The CBV mixin supports several options for extension and customization covered in the FAQ section.

There are two methods which implement a lower level API which can be used directly for PDFs:

### file_to_pdf(input_file, output_file, **extra_args)

Arguments:
- `input_file`:  An open for reading "file-like" object to read HTML from for rendering
- `output_file`: An open for writing "file-like" object to write the PDF to after rendering
- `**extra_args`:  See below

This function will read the contents of `input_file` (an HTML bytestring), render it with Chrome and store the binary PDF data in `output_file`.  Any `kwargs` are translated as commandline arguments to chrome when starting the headless browser for rendering, i.e.:

```python
from hardcopy import file_to_pdf

extra_args = {
    'virtual-time-budget': 6000
}

file_to_pdf(open('myfile.html'), open('myfile.pdf'), **extra_args)
# translates to --virtual-time-budget=6000 when starting chrome

extra_args = {
    'disable-gpu': None
}

file_to_pdf(open('myfile.html'), open('myfile.pdf'), **extra_args)
# translates to --disable-gpu when starting chrome (currently on by default and required by Chrome)

```

### bytestring_to_pdf(html_data, output_file, **extra_args)

Arguments:
- `html_data`:  A bytestring of HTML data. _Note: We use bytestrings because the most common execution path is to generate a PDF from a rendered Django template response_
- `output_file`: An open for writing "file-like" object to write the PDF to after rendering
- `**extra_args`:  See below

This render the contents of `html_data` with Chrome and store the binary PDF data in `output_file`.  Any `kwargs` are translated as commandline arguments to chrome when starting the headless browser for rendering, i.e.:


```python
from hardcopy import bytestring_to_pdf

extra_args = {
    'virtual-time-budget': 6000
}

bytestring_to_pdf(b"<html><h1>Hello Chrome!</h1></html>", open('myfile.pdf'), **extra_args)
# translates to --virtual-time-budget=6000 when starting chrome

extra_args = {
    'disable-gpu': None
}

bytestring_to_pdf(b"<html><h1>Hello Chrome!</h1></html>", open('myfile.pdf'), **extra_args)
# translates to --disable-gpu when starting chrome (currently on by default and required by Chrome)
```

Similar functions are available for PNG generation:

### file_to_png(input_file, output_file, width, height, **extra_args)

Arguments:
- `input_file`:  An open for reading "file-like" object to read HTML from for rendering
- `output_file`: An open for writing "file-like" object to write the PNG to after rendering
- `width`: width of the viewport in pixels
- `height`: height of the viewport in pixels
- `**extra_args`:  See above

### bytestring_to_png(html_data, output_file, width, height, **extra_args)

Arguments:
- `html_data`:  A bytestring of HTML data. _Note: We use bytestrings because the most common execution path is to generate a PNG from a rendered Django template response_
- `output_file`: An open for writing "file-like" object to write the PNG to after rendering
- `width`: width of the viewport in pixels
- `height`: height of the viewport in pixels
- `**extra_args`:  See below

## FAQ

- How do I configure a view to download the PDF/PNG file?
  
  Set the `download_attachment` property to `True`:
  ```python
  class MyView(PDFViewMixin, TemplateView):
      download_attachment = True

- How do I override the chrome window size defined in a view?
  
  Set the `chrome_window_size` property to a string of your choice:
  ```python
  class MyView(PDFViewMixin, TemplateView):
      chrome_window_size = '1920,1600'
  ```
- How do I customize the file name of the generated PDF/PNG?
  
  Override the `get_filename` method of your view:
  ```python
  class MyView(PDFViewMixin, TemplateView):
      def get_filename(self):
          return "my_file_{}.pdf".format(now().strftime('Y-m-d'))
  ```
- How do I add context data with django-hardcopy ?

  There's no magic here, simply override the `TemplateView.get_context_data` method,
  like you would do in a normal view:
  ```python
  class MyView(PDFViewMixin, TemplateView):
      def get_context_data(self, **kwargs):
          context = super(MyView, self).get_context_data(**kwargs)
          context['example_data'] = self.request.GET.get('example')
          return context
  ```
- I want to process the rendered HTML content before it is converted to PDF or PNG, how to do this ?

  Just override the mixin method `process_html_content` in your view:
  ```python
  class MyView(PDFViewMixin, TemplateView):
      def process_html_content(self, content):
          return make_absolute_paths(content)
  ```

 ## Caveats
 
 ### Static files
Under the hood, django-hardcopy writes HTML content to a temporary file which is loaded in chrome via the `file://` protocol. This does no magic on handling static files, and since Django is not necessarily serving static files at the URL rendered in the template (say if `STATIC_URL` is set to a relative path like most development envirnoments).  In production environments where static assets are served via a media server or s3 bucket at an absoulte URL, this is probably fine.

In local development however, Chrome will recieve a connection refused error on attempts to load static files in templates included like `<link href="{% static 'style.css' %}" rel="stylesheet">`.   The best workaround for this is to include static assets inline in PDF/PNG templates.

A nice feature for the roadmap of `django-hardcopy` would be dynamic parsing of templates to convert linked static assets to inline assets automatically.  (PRs welcome :))
