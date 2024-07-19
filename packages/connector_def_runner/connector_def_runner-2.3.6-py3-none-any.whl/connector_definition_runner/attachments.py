import io
import re
import cgi
import urllib.parse


FILENAME_HEADER_KEY = 'Content-Disposition'
FILENAME_REGEX = """filename=['"]?([^"']*)['"]"""


def get_filename(response):
    """ 
    Gets filename from Content-Disposition Header.
    """
    cd_string = response.headers[FILENAME_HEADER_KEY]
    _, params = cgi.parse_header(cd_string)
    if 'filename' in params:
        fname = params['filename']
    elif 'filename*' in params:
        fname = params['filename*']
    else:
        fname = "unknown"
    if "utf-8''" in fname.lower():
        fname = re.sub("utf-8''", '', fname, flags=re.IGNORECASE)
        fname = urllib.parse.unquote(fname)
    # clean space and double quotes
    return fname.strip().strip('"')


def get_file_object(response):
    return {
        'filename': get_filename(response),
        'file_data': io.BytesIO(response.content)
    }


def parse_attachment_output(response, manifest):
    if 'file' not in manifest['output'].get('properties', {}):
        return

    if manifest['output']['properties']['file']['type'] == 'array':
        return [get_file_object(response)]
    else:
        return get_file_object(response)
