# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Summary.parsed_at'
        db.delete_column(u'crawler_summary', 'parsed_at')

        # Adding field 'Summary.last_parse_time'
        db.add_column(u'crawler_summary', 'last_parse_time',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Summary.next_parse_time'
        db.add_column(u'crawler_summary', 'next_parse_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Summary.parsed_at'
        db.add_column(u'crawler_summary', 'parsed_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Summary.last_parse_time'
        db.delete_column(u'crawler_summary', 'last_parse_time')

        # Deleting field 'Summary.next_parse_time'
        db.delete_column(u'crawler_summary', 'next_parse_time')


    models = {
        'crawler.article': {
            'Meta': {'object_name': 'Article'},
            'body_text': ('django.db.models.fields.TextField', [], {}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['crawler.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_of': ('django.db.models.fields.DateTimeField', [], {}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_column': "'hash'"}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['crawler.SiteSlice']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        },
        'crawler.category': {
            'Meta': {'ordering': "('tree_id', 'lft')", 'unique_together': "(('parent', 'name'),)", 'object_name': 'Category'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['crawler.Category']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'crawler.parser': {
            'Meta': {'object_name': 'Parser'},
            'engine': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'rules': ('jsonfield.fields.JSONField', [], {'default': '[]'})
        },
        'crawler.siteslice': {
            'Meta': {'object_name': 'SiteSlice'},
            'domains': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['crawler.Parser']"}),
            'rotate_time': ('interval.fields.IntervalField', [], {'default': 'datetime.timedelta(1)'}),
            'urls': ('django.db.models.fields.TextField', [], {})
        },
        'crawler.summary': {
            'Meta': {'object_name': 'Summary'},
            'errors': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_parse_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'next_parse_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'parsed_n_articles': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'summary'", 'unique': 'True', 'to': "orm['crawler.SiteSlice']"}),
            'warns': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        }
    }

    complete_apps = ['crawler']