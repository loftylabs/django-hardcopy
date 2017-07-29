# django-hardcopy:  Render PDFs in Django with headless Chrome

Chrome [introduced headless mode in v59](https://developers.google.com/web/updates/2017/04/headless-chrome) opening the possibility of using Chrome as a fast and elegant way of generating PDF data programatically via HTML.  `django-hardcopy` is an alternative to other projects which leverage `wkhtmltopdf`, a great tool but one that lacks the portability, ease of installation, the performance, and reliability of Chrome.


## Requirements
- Django
- Chrome, Chromium, or Chrome Canary >= v59
- Currently only tested against Django 1.10+ and Python 3.6 (other versions may be supported, submit an issue if not!)

## Installation

Install the library:

    pip install django-hardcopy
    
Install Chrome or a derivative:

    apt-get install chromium-browser
    
Set your Chrome path (optional)

    # settings.py
    
    CHROME_PATH = '/path/to/chrome-or-chromium'
    
This can be useful if you want to use `chrome-canary` or `chromium-browser` (available by default in Ubuntu).  Django-hardcopy will attempt to smartly default the appropriate chrome path for your os.  
 
If you're on Mac OSX, just upgrade to the latest Chrome and you're good to go!

## Usage

The easiest way to use `django-hardcopy` is to use its CBV mixin:

```python
from django.views.generic import TemplateView
from hardcopy.views import PDFViewMixin


class MyView(PDFViewMixin, TemplateView):
    template_name = "pdf_me.html"

```

It works with any Django Class Based View, and implements PDF rendering on the `GET` HTTP method. Further, if the `?html` querystring variable is provided the mixin will render the view normally for designing and debugging of PDF views.  The CBV mixin supports several options for extension and customization covered in the FAQ section.

There are two methods which implement a lower level API which can be used directly:

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


## FAQ

- How do I configure a view to download the PDF file?
  
  Set the `download_attachment` property to `True`:
  ```python
  class MyView(PDFViewMixin, TemplateView):
      download_attachment = True
  ```
- How do I customize the file name of the generated PDF?
  
  Override the `get_filename` method of your view:
  ```python
  class MyView(PDFViewMixin, TemplateView):
      def get_filename(self):
          return "my_file_{}.pdf".format(now().strftime('Y-m-d'))
  ```
  
 ## Caveats
 
 ### Static files
Under the hood, django-hardcopy writes HTML content to a temporary file which is loaded in chrome via the `file://` protocol. This does no magic on handling static files, and since Django is not necessarily serving static files at the URL rendered in the template (say if `STATIC_URL` is set to a relative path like most development envirnoments).  In production environments where static assets are served via a media server or s3 bucket at an absoulte URL, this is probably fine.

In local development however, Chrome will recieve a connection refused error on attempts to load static files in templates included like `<link href="{% static 'style.css' %}" rel="stylesheet">`.   The best workaround for this is to include static assets inline in PDF templates.

A nice feature for the roadmap of `django-hardcopy` would be dynamic parsing of templates to convert linked static assets to inline assets automatically.  (PRs welcome :))
