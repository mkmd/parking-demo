
from django import forms
from django.utils.translation import ugettext as _
from django.utils import six
from taggit.utils import parse_tags, edit_string_for_tags


class TokenInputWidget(forms.TextInput):
    class Media:
        css = {
            'all': ('taggittokenfield/TagTokenWidget.css',),
        }
        js = ('taggittokenfield/jquery-1.7.1.min.js', 'taggittokenfield/jquery.init.js', 'tagtoken/init.js',)

    def __init__(self, attrs=None):
        default_attrs = {'class': 'vTextField', 'data-token-input': ''}
        if attrs:
            default_attrs.update(attrs)

        super(TokenInputWidget, self).__init__(default_attrs)

    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, six.string_types):
            value = edit_string_for_tags(value)
        return super(TokenInputWidget, self).render(name, value, attrs)

    #@property
    #def _media(self):
    #    css = {
    #        'all': ('taggittokenfield/TagTokenWidget.css',),
    #    }
    #    js = ('taggittokenfield/jquery-1.7.1.min.js', 'taggittokenfield/jquery.init.js', 'tagtoken/jquery.tokeninput.js', 'tagtoken/init.js',)
    #
    #    return forms.Media(css=css, js=js)


class ParserEngineChoice(forms.Select):
    class Media:
        js = ('crawler/engine-choice.js',)

    def __init__(self, target, attrs=None):
        if not target:
            raise ValueError('Target field must be passed!')

        default_attrs = {'data-target': 'id_%s' % target}
        if attrs:
            default_attrs.update(attrs)

        self.url_template = ''
        super(ParserEngineChoice, self).__init__(default_attrs)

    def render(self, name, value, attrs=None, choices=()):
        if not self.url_template:
            raise ValueError('Source url must be passed!')

        if not attrs:
            attrs = {}

        attrs["data-url-template"] = self.url_template
        return super(ParserEngineChoice, self).render(name, value, attrs, choices)

