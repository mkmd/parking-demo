# -*- coding: utf-8 -*-

from django.contrib import admin
from taggit.managers import TaggableManager
from taggittokenfield.forms import TagTokenWidget
from categories.admin import CategoryBaseAdmin

from crawler.models import Parser, SiteSlice, Summary, Category, Article
from .forms import ParserForm, SiteSliceForm, ArticleForm


class ParserAdmin(admin.ModelAdmin):
    form = ParserForm

    list_display = ['label', 'engine']
    search_fields = ['label', 'engine']
    #list_filter = ['engine']


class ParseSummaryAdmin(admin.ModelAdmin):
    pass


class SiteSliceAdmin(admin.ModelAdmin):
    form = SiteSliceForm

    list_display = ['label', 'parser', 'domains', 'rotate_time', 'short_summary', 'enabled']
    search_fields = ['urls', 'parser']  # 'tags'
    list_filter = ['enabled', 'parser']
    readonly_fields = ('short_summary',)
    fieldsets = [
        ('Base information', {'fields': [
            'enabled',
            'label',
            'parser',
            'rotate_time',
            'urls',
            'domains',
        ]}),
        ('Additional information', {
            'classes': ('collapse',),
            'fields': ['tagline']
        }),
        ('Statistics', {
            'classes': ('collapse',),
            'fields': ['short_summary']
        }),
    ]
    formfield_overrides = {
        TaggableManager: {'widget': TagTokenWidget}
    }
    actions = ['deactivate', 'activate']
    # todo: embed own articles list

    def deactivate(self, request, queryset):
        # selected = self.model.objects.filter(
        #     pk__in=[int(x) for x in request.POST.getlist('_selected_action')])

        # for item in queryset:
        [item.deactivate() for item in queryset]


    deactivate.short_description = 'Deactivate selected slices'

    def activate(self, request, queryset):
        [item.activate() for item in queryset]
    activate.short_description = 'Activate selected slices'


class CategoryAdmin(CategoryBaseAdmin):
    # todo: inline articles
    # todo: batch delete action

    # note: to override the "Media" it's possible use dynamic attribute copy from derived class
    #class Media:
    #    js = ('category/initialize-tree.js',)

    actions = ['tree_delete_selected',]

    #def get_actions(self, request):
    #    actions = super(CategoryBaseAdmin, self).get_actions(request)
    #    extra_actions = super(CategoryAdmin, self).get_actions(request)
    #    if extra_actions:
    #        actions.update(extra_actions)
    #    return actions

    def tree_delete_selected(self, request, queryset):
        selected_cats = self.model.objects.filter(
            pk__in=[int(x) for x in request.POST.getlist('_selected_action')])

        for item in selected_cats:
            if not item.pk:
                continue

            for subitem in item.get_descendants():
                subitem.delete()
            item.delete()

    tree_delete_selected.short_description = 'Delete selected in tree'


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm

    list_per_page = 50
    list_display = ['headline', 'url', 'site', 'created_at']
    search_fields = ['headline', 'body_text', 'url']  # 'tags'
    list_filter = ['site']
    readonly_fields = ('site',)
    filter_horizontal = ('categories',)
    fieldsets = [
        ('Base information', {'fields': [
            'site',
            'date_of',
            'url',
            'headline',
            'body_text',
        ]}),
        ("Additional information", {
            'classes': ('collapse',),
            'fields': [
                #'created_at',
                #'categories',
                'tagline',
            ]}),
    ]
    formfield_overrides = {
        TaggableManager: {'widget': TagTokenWidget}
    }


admin.site.register(Parser, ParserAdmin)
# admin.site.register(Summary, ParseSummaryAdmin)
admin.site.register(SiteSlice, SiteSliceAdmin)
#admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)

