import subprocess
from tempfile import NamedTemporaryFile

from hardcopy.conf import hc_settings


def file_to_pdf(input_file, output_file, **extra_args):
    """
    Given an input file(HTML) and an output file, render the HTML as a PDF and save it to output_file
    input_file and output_file are both (open) file-like objects.
    :param html_data:  file like object to read from
    :param output_file: file like object to write to
    :param extra_args: additional command line arguments to chrome
    :return:
    """
    chrome_args = [
        hc_settings.CHROME_PATH,
        '--headless',
        '--print-to-pdf="{}"'.format(output_file.name),
        '--disable-gpu',  # Required by chrome's headless mode for now
    ]

    # Optional args
    for k, v in extra_args.items():
        if v is not None:
            chrome_args.append('--{}={}'.format(k, v))
        else:
            chrome_args.append('--{}'.format(k))

    # Path to the input data
    chrome_args.append('file://{}'.format(input_file.name))
    subprocess.call(" ".join(chrome_args), shell=True)
    output_file.seek(0)

    return True


def bytestring_to_pdf(html_data, output_file, **extra_args):
    """
    Given a bytestring of html data as input (like a rendered django template response), render a PDF
    and write the output to output_file
    :param html_data:  bytestring of html data
    :param output_file: file like object to write to
    :param extra_args: additional command line arguments to chrome
    :return:
    """
    input_file = NamedTemporaryFile()

    input_file.write(html_data)
    input_file.flush()

    file_to_pdf(input_file, output_file, **extra_args)

    return True