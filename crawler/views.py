from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404

from .models import Parser
from crawler.bot import load_spider_rule_template
from contrib.utils import pretty_string


def parser_rules(request, parser):
    if not isinstance(parser, Parser):
        parser = get_object_or_404(Parser, pk=parser)

    return HttpResponse(content=pretty_string(parser.rules))


def engine_rules(request, engine):
    content = ''
    try:
        content = load_spider_rule_template(Parser.shortcut(engine))
    except IOError:
        # str(Parser._meta.get_field('rules').get_default())
        rules_field = Parser._meta.get_field('rules')
        content = rules_field.get_default()  # rules_field.dumps_for_display(rules_field.get_default())
    finally:
        return HttpResponse(content=pretty_string(content))
        #return HttpResponseNotFound()


def rules(request, parser='', engine=''):
    if not (parser and engine):
        return HttpResponseNotFound()

    parser = get_object_or_404(Parser, pk=parser)
    if parser.engine == engine and parser.rules:
        return parser_rules(request, parser)

    #raise Http404
    return engine_rules(request, engine)