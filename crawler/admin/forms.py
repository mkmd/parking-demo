# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from ckeditor.fields import RichTextFormField

from crawler.admin.widgets import TokenInputWidget, ParserEngineChoice
from crawler.models import Parser, SiteSlice, Article
from crawler.bot import discover_spiders
from contrib.utils import pretty_string, make_shortcut


def _engine_choices():
    def make_choice(name):
        return name, make_shortcut(name)

    package_of = lambda cls: '.'.join([cls.__module__, cls.__name__])
    choices = [make_choice(package_of(spider)) for spider in discover_spiders()]

    return choices, choices[0][0] if choices else None


class ParserForm(forms.ModelForm):
    class Meta:
        model = Parser
        widgets = {
            'engine': ParserEngineChoice(target='rules')
        }

    def __init__(self, *args, **kwargs):
        super(ParserForm, self).__init__(*args, **kwargs)

        self.setup_engine_field()
        self.setup_rules_field()

    def setup_engine_field(self):
        model_field = self._meta.model._meta.get_field('engine')

        url_params = {"engine": '<engine>'}
        if self.instance.pk:
            url_params["parser"] = self.instance.pk

        self.fields['engine'].widget.url_template = reverse(
            'parser-rules',
            kwargs=url_params,
            current_app='crawler'
        )  # 'crawler.views.rules'

        choices, default = _engine_choices()

        if model_field.choices:
            model_field.choices[:] = []

        model_field.default = default
        model_field.choices.extend(choices)

        form_field = self.fields['engine']
        form_field.initial = model_field.default
        form_field.widget.choices = model_field.choices

    def setup_rules_field(self):
        if self.instance.rules:
            return

        model_field = self._meta.model._meta.get_field('rules')
        form_field = self.fields['rules']
        form_field.initial = pretty_string(self.instance.rules_template)


class SiteSliceForm(forms.ModelForm):
    class Meta:
        model = SiteSlice

    def __init__(self, *args, **kwargs):
        super(SiteSliceForm, self).__init__(*args, **kwargs)
        self.fields['urls'].widget = TokenInputWidget()
        self.fields['domains'].widget = TokenInputWidget()


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article

    body_text = RichTextFormField()