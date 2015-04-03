# coding=utf8
from urlparse import urljoin
from coffin.template import Library
from jinja2.ext import Extension
from jinja2 import nodes
from django.utils.encoding import iri_to_uri
from django.conf import settings
from models import StaticFile


register = Library()


class PrefixExtension(Extension):

    def parse(self, parser):
        stream = parser.stream
        lineno = stream.next().lineno

        call_node = self.call_method('render')

        if stream.next_if('name:as'):
            var = nodes.Name(stream.expect('name').value, 'store')
            return nodes.Assign(var, call_node).set_lineno(lineno)
        else:
            return nodes.Output([call_node]).set_lineno(lineno)

    def render(self, name):
        raise NotImplementedError()

    @classmethod
    def get_uri_setting(cls, name):
        return iri_to_uri(getattr(settings, name, ''))


class CdnExtension(PrefixExtension):
    tags = set(['cdn'])

    def parse(self, parser):
        stream = parser.stream
        lineno = stream.next().lineno

        path = parser.parse_expression()
        call_node = self.call_method('get_statc_url', args=[path])

        if stream.next_if('name:as'):
            var = nodes.Name(stream.expect('name').value, 'store')
            return nodes.Assign(var, call_node).set_lineno(lineno)
        else:
            return nodes.Output([call_node]).set_lineno(lineno)

    @classmethod
    def get_statc_url(cls, path):
        if settings.DEBUG:
            return path
        f = StaticFile(path)
        return f.cdn_path


register.tag(CdnExtension)


def static(path):
    return CdnExtension.get_static_url(path)
