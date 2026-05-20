# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class PastAbstracts(models.Model):
    nid = models.IntegerField(primary_key=True)
    vid = models.IntegerField()
    uid = models.IntegerField()
    uuid = models.UUIDField(unique=True)
    revision_id = models.IntegerField()
    year = models.IntegerField()
    plenary = models.BooleanField()
    presentation_file_id = models.IntegerField(blank=True, null=True)
    section_id = models.TextField(blank=True, null=True)
    subsection_id = models.TextField(blank=True, null=True)
    status_id = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField()
    date_changed = models.DateTimeField()
    authors = models.TextField(blank=True, null=True)
    authors_organization = models.TextField(blank=True, null=True)
    scientific_director = models.TextField(blank=True, null=True)
    scientific_director_organization = models.TextField(blank=True, null=True)
    presentation_name_eng = models.TextField(blank=True, null=True)
    presentation_uri = models.TextField(blank=True, null=True)
    presentation_name_original = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'abstracts'


class PastUsers(models.Model):
    uid = models.IntegerField(primary_key=True)
    uuid = models.UUIDField(unique=True)
    username = models.TextField()
    mail = models.TextField(unique=True)
    pass_field = models.TextField(db_column='pass')  # Field renamed because it was a Python reserved word.
    first_name = models.TextField(blank=True, null=True)
    middle_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    dolzhnost = models.TextField(blank=True, null=True)
    organization = models.TextField(blank=True, null=True)
    organization_short = models.TextField(blank=True, null=True)
    citizenship = models.TextField(blank=True, null=True)
    forma0 = models.TextField(blank=True, null=True)
    forma1 = models.TextField(blank=True, null=True)
    consent = models.BooleanField()
    date_created = models.DateTimeField()
    date_changed = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'
