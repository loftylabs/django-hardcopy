import subprocess

from django.core.files.temp import NamedTemporaryFile

from hardcopy.conf import settings


def get_chrome_args():
    return [
        settings.CHROME_PATH,
        '--no-sandbox',  # Avoids permission issues while dockerized.
        '--headless',
        '--disable-extensions',  # Reduces startup overhead.
        '--disable-gpu',  # Required by chrome's headless mode for now.
    ]


def file_to(fmt, input_file, output_file, **extra_args):
    """
    Given an input file(HTML) and an output file,
    render the HTML as a file with the given format and save it to
    output_file input_file and output_file are both (open) file-like objects.

    :param fmt: string, the format of the output file (pdf, png)
    :param html_data: file like object to read from
    :param output_file: file like object to write to
    :param extra_args: additional command line arguments to chrome
    :return:
    """
    chrome_args = get_chrome_args()
    if fmt == 'pdf':
        chrome_args.append(
            '--print-to-pdf="{}"'.format(output_file.name),
        )
    elif fmt == 'png':
        chrome_args.append(
            '--screenshot="{}"'.format(output_file.name),
        )
    else:
        raise ValueError('Unsupported output format "{}"'.format(fmt))

    # Optional arguments.
    for k, v in extra_args.items():
        if v is not None:
            chrome_args.append('--{}={}'.format(k, v))
        else:
            chrome_args.append('--{}'.format(k))

    # Path to the input data.
    chrome_args.append('file://{}'.format(input_file.name))
    subprocess.call(" ".join(chrome_args), shell=True)
    output_file.seek(0)

    return True


def bytestring_to(converter, html_data, output_file, **extra_args):
    """Given a bytestring of html data as input
    (like a rendered django template response),
    render a PDF and write the output to output_file

    :param html_data: converter function
    :param html_data: bytestring of html data
    :param output_file: file like object to write to
    :param extra_args: additional command line arguments to chrome
    :return:
    """
    input_file = NamedTemporaryFile(suffix='.html')
    input_file.write(html_data)
    input_file.flush()
    converter(input_file, output_file, **extra_args)

    return True


def file_to_pdf(input_file, output_file, **extra_args):
    """
    Given an input file(HTML) and an output file,
    render the HTML as a PDF and save it to output_file
    input_file and output_file are both (open) file-like objects.

    :param html_data: file like object to read from
    :param output_file: file like object to write to
    :param extra_args: additional command line arguments to chrome
    :return:
    """
    return file_to('pdf', input_file, output_file, **extra_args)


def bytestring_to_pdf(html_data, output_file, **extra_args):
    """Given a bytestring of html data as input
    (like a rendered django template response),
    render a PDF and write the output to output_file

    :param html_data: bytestring of html data
    :param output_file: file like object to write to
    :param extra_args: additional command line arguments to chrome
    :return:
    """
    return bytestring_to(file_to_pdf, html_data, output_file, **extra_args)


def file_to_png(input_file, output_file,
                width=None, height=None, **extra_args):
    """
    Given an input file(HTML) and an output file,
    render the HTML as a PNG and save it to output_file.
    input_file and output_file are both (open) file-like objects.

    :param html_data:  file like object to read from
    :param output_file: file like object to write to
    :param width: width of the viewport in pixels
    :param height: height of the viewport in pixels
    :param extra_args: additional command line arguments to chrome
    :return:
    """
    if width is not None and height is not None:
        extra_args.update({'window-size': '{},{}'.format(width, height)})
    return file_to('png', input_file, output_file, **extra_args)


def bytestring_to_png(html_data, output_file,
                      width=None, height=None, **extra_args):
    """
    Given a bytestring of html data as input,
    (like a rendered django template response),
    render a PNG and write the output to output_file.

    :param html_data:  bytestring of html data
    :param output_file: file like object to write to
    :param width: width of the viewport in pixels
    :param height: height of the viewport in pixels
    :param extra_args: additional command line arguments to chrome
    :return:
    """
    if width is not None and height is not None:
        extra_args.update({'window-size': '{},{}'.format(width, height)})
    return bytestring_to(file_to_png, html_data, output_file, **extra_args)
