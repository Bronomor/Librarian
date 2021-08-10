from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Shelve)
admin.site.register(Book)
admin.site.register(Temporary_book)
admin.site.register(BookCategory)
admin.site.register(Library)