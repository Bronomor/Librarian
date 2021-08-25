from django.db import models

# Create your models here.


class Shelve(models.Model):
    name = models.TextField(max_length=200, unique=True, blank=False, null=False)
    details = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name

    def __unicode__(self):
        return u'%s' % self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return "%s" % self.name

    def __unicode__(self):
        return u'%s' % self.name


class Temporary_book(models.Model):
    serial_key = models.CharField(max_length=100, null=True, blank=True)
    author = models.CharField(max_length=1000, null=True)
    title = models.CharField(max_length=1000, null=True)
    ISBN = models.CharField(max_length=13)
    publisher = models.CharField(max_length=350, null=True)
    published_city = models.CharField(max_length=300, null=True)
    published_year = models.CharField(max_length=4, null=True)
    details = models.TextField(max_length=1000, null=True)
    search_number = models.IntegerField(unique=True)
    is_complete_search = models.BooleanField(default=False)
    price = models.FloatField(blank=True, null=True)
    bought_date = models.DateField(blank=True, null=True)
    physical_location = models.ForeignKey(Shelve, on_delete=models.PROTECT, blank=True, null=True)
    categories = models.TextField(max_length=1000)

    def __str__(self):
        return "%s slot" % self.search_number

    def __unicode__(self):
        return u'%s slot' % self.search_number


class Book_to_accept(models.Model):
    serial_key = models.CharField(max_length=100, null=True, blank=True)
    author = models.CharField(max_length=1000, null=True)
    title = models.CharField(max_length=1000, null=True)
    ISBN = models.CharField(max_length=13)
    publisher = models.CharField(max_length=350, null=True)
    published_city = models.CharField(max_length=300, null=True)
    published_year = models.CharField(max_length=4, null=True)
    details = models.TextField(max_length=1000, null=True)
    search_number = models.IntegerField(unique=True)
    price = models.FloatField(blank=True, null=True)
    bought_date = models.DateField(blank=True, null=True)
    physical_location = models.ForeignKey(Shelve, on_delete=models.PROTECT, blank=True, null=True)
    categories = models.TextField(max_length=1000)

    def __str__(self):
        return "%s slot" % self.search_number

    def __unicode__(self):
        return u'%s slot' % self.search_number


class Book(models.Model):
    serial_key = models.CharField(max_length=100, unique=True, blank=False, null=False)
    author = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    ISBN = models.CharField(max_length=13)
    publisher = models.CharField(max_length=350, blank=True, null=True)
    published_city = models.CharField(max_length=300, blank=True, null=True)
    published_year = models.CharField(max_length=30, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    bought_date = models.DateField(blank=True, null=True)
    details = models.TextField(max_length=1000, blank=True, null=True)
    physical_location = models.ForeignKey(Shelve, on_delete=models.PROTECT)
    categories = models.TextField(max_length=1000, blank=True, null=True)
    categories_fk = models.ManyToManyField(BookCategory, blank=True)

    def __str__(self):
        return "%s" % self.title

    def __unicode__(self):
        return u'%s' % self.title