"""Librarian URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from books_online.views import add_book_view, main_site, add_shelves, add_category, search_books_view, search_shelves_view, search_category_view, \
create_backup_view, load_backup_view, statistic_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_site),
    path('add_books', add_book_view),
    path('add_shelve', add_shelves),
    path('add_category', add_category),

    path('search_books', search_books_view),
    path('search_shelve', search_shelves_view),
    path('search_category', search_category_view),

    path('create_backup_view', create_backup_view),
    path('load_backup_view', load_backup_view),

    path('statistic_view', statistic_view),

]
