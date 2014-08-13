# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Parser'
        db.create_table(u'crawler_parser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('engine', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('rules', self.gf('jsonfield.fields.JSONField')(default=[])),
        ))
        db.send_create_signal('crawler', ['Parser'])

        # Adding model 'SiteSlice'
        db.create_table(u'crawler_siteslice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('parser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['crawler.Parser'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('domains', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('urls', self.gf('django.db.models.fields.TextField')()),
            ('rotate_time', self.gf('interval.fields.IntervalField')(default=datetime.timedelta(1))),
        ))
        db.send_create_signal('crawler', ['SiteSlice'])

        # Adding model 'Summary'
        db.create_table(u'crawler_summary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(related_name='summary', unique=True, to=orm['crawler.SiteSlice'])),
            ('parsed_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, blank=True)),
            ('parsed_n_articles', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('warns', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('errors', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('crawler', ['Summary'])

        # Adding model 'Category'
        db.create_table(u'crawler_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['crawler.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0, unique=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('crawler', ['Category'])

        # Adding unique constraint on 'Category', fields ['parent', 'name']
        db.create_unique(u'crawler_category', ['parent_id', 'name'])

        # Adding model 'Article'
        db.create_table(u'crawler_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('headline', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body_text', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['crawler.SiteSlice'])),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255)),
            ('date_of', self.gf('django.db.models.fields.DateTimeField')()),
            ('hash', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_column='hash')),
        ))
        db.send_create_signal('crawler', ['Article'])

        # Adding M2M table for field categories on 'Article'
        m2m_table_name = db.shorten_name(u'crawler_article_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['crawler.article'], null=False)),
            ('category', models.ForeignKey(orm['crawler.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['article_id', 'category_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Category', fields ['parent', 'name']
        db.delete_unique(u'crawler_category', ['parent_id', 'name'])

        # Deleting model 'Parser'
        db.delete_table(u'crawler_parser')

        # Deleting model 'SiteSlice'
        db.delete_table(u'crawler_siteslice')

        # Deleting model 'Summary'
        db.delete_table(u'crawler_summary')

        # Deleting model 'Category'
        db.delete_table(u'crawler_category')

        # Deleting model 'Article'
        db.delete_table(u'crawler_article')

        # Removing M2M table for field categories on 'Article'
        db.delete_table(db.shorten_name(u'crawler_article_categories'))


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
            'parsed_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'parsed_n_articles': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'summary'", 'unique': 'True', 'to': "orm['crawler.SiteSlice']"}),
            'warns': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        }
    }

    complete_apps = ['crawler']