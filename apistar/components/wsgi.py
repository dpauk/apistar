import json
from wsgiref.util import request_uri

import werkzeug
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.formparser import parse_form_data
from werkzeug.http import parse_options_header
from werkzeug.wsgi import get_input_stream

from apistar import exceptions, http
from apistar.interfaces import ParamName, WSGIEnviron


def get_url(environ: WSGIEnviron):
    return request_uri(environ)


def get_scheme(environ: WSGIEnviron):
    return environ['wsgi.url_scheme']


def get_host(environ: WSGIEnviron):
    return environ.get('HTTP_HOST') or environ['SERVER_NAME']


def get_port(environ: WSGIEnviron):
    if environ['wsgi.url_scheme'] == 'https':
        return int(environ.get('SERVER_PORT') or 443)
    return int(environ.get('SERVER_PORT') or 80)


def get_querystring(environ: WSGIEnviron):
    return environ.get('QUERY_STRING', '')


def get_queryparams(environ: WSGIEnviron):
    return werkzeug.urls.url_decode(environ.get('QUERY_STRING', ''))


def get_queryparam(name: ParamName, queryparams: http.QueryParams):
    return queryparams.get(name)


def get_headers(environ: WSGIEnviron):
    return werkzeug.datastructures.EnvironHeaders(environ)


def get_header(name: ParamName, headers: http.Headers):
    return headers.get(name.replace('_', '-'))


def get_body(environ: WSGIEnviron):
    return get_input_stream(environ).read()


def get_request_data(environ: WSGIEnviron):
    if not bool(environ.get('CONTENT_TYPE')):
        mimetype = None
    else:
        mimetype, _ = parse_options_header(environ['CONTENT_TYPE'])

    if mimetype is None:
        value = None
    elif mimetype == 'application/json':
        body = get_input_stream(environ).read()
        value = json.loads(body.decode('utf-8'))
    elif mimetype in ('multipart/form-data', 'application/x-www-form-urlencoded'):
        stream, form, files = parse_form_data(environ)
        value = ImmutableMultiDict(list(form.items()) + list(files.items()))
    else:
        raise exceptions.UnsupportedMediaType()

    return value
