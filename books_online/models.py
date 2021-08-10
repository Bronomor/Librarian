from django.db import models

# Create your models here.


class Library(models.Model):
    name = models.CharField(max_length=50)
    book_count = models.IntegerField(default=0)
    shelve_count = models.IntegerField(default=0)
    category_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Shelve(models.Model):
    name = models.TextField(max_length=200, unique=True)
    details = models.TextField(max_length=500, blank=True, null=True)
    library = models.ForeignKey(Library, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name

    def __unicode__(self):
        return u'%s' % self.name

    def save(self, **kwargs):
        super().save()
        self.update_shelve_count()

    def delete(self, **kwargs):
        super().delete()
        self.update_shelve_count()

    def update_shelve_count(self):
        if self.library:
            self.library.shelve_count = self.library.shelve_set.count()
            self.library.save()


class BookCategory(models.Model):
    name = models.CharField(max_length=100)
    library = models.ForeignKey(Library, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name

    def __unicode__(self):
        return u'%s' % self.name

    def save(self, **kwargs):
        super().save()
        self.update_category_count()

    def delete(self, **kwargs):
        super().delete()
        self.update_category_count()

    def update_category_count(self):
        if self.library:
            self.library.category_count = self.library.bookcategory_set.count()
            self.library.save()


class Temporary_book(models.Model):
    author = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=True)
    ISBN = models.CharField(max_length=13)
    publisher = models.CharField(max_length=150, null=True)
    published_city = models.CharField(max_length=100, null=True)
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


class Book(models.Model):
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    ISBN = models.CharField(max_length=13)
    publisher = models.CharField(max_length=150, blank=True, null=True)
    published_city = models.CharField(max_length=100, blank=True, null=True)
    published_year = models.CharField(max_length=30, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    bought_date = models.DateField(blank=True, null=True)
    details = models.TextField(max_length=1000, blank=True, null=True)
    physical_location = models.ForeignKey(Shelve, on_delete=models.PROTECT)
    categories = models.TextField(max_length=1000, blank=True, null=True)
    library = models.ForeignKey(Library, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return "%s" % self.title

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, **kwargs):
        super().save()
        self.update_book_count()

    def delete(self, **kwargs):
        super().delete()
        self.update_book_count()

    def update_book_count(self):
        if self.library:
            self.library.book_count = self.library.book_set.count()
            self.library.save()



