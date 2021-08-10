from django import forms
import floppyforms
from rest_framework import serializers

from . import models
from .models import Book, Shelve, BookCategory


class DateInput(forms.DateInput):
    input_type = 'date'
    input_formats = '%Y-%m-%d'


class Shelve_form(forms.ModelForm):
    class Meta:
        model = models.Shelve
        fields = ('name', 'details')
        labels = {
            'name': 'Nazwa półki',
            'details': 'Opis',
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "required": "True", "autocomplete": "off"}),
            "details": forms.Textarea(attrs={"class": "form-control", "required": "True", "rows": 5 , "autocomplete": "off"}),
        }


class BookCategory_form(forms.ModelForm):
    class Meta:
        model = models.BookCategory
        fields = ('name',)
        labels = {
            'name': 'Nazwa kategorii',
        }
        widgets = {"name": forms.TextInput(attrs={"class": "form-control", "required": "True", "autocomplete": "off"})}


class Search_form(forms.Form):
    author = forms.CharField(label='Autor', required=False, max_length=100, widget=floppyforms.widgets.Input(
        datalist={m['author'] for m in Book.objects.values('author')},
        attrs={'autocomplete': 'off', "class": "form-control"}))
    title = forms.CharField(label='Tytuł', required=False, max_length=100,
                            widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}))
    ISBN = forms.CharField(label='ISBN', required=False, max_length=13,
                           widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}))
    publisher = forms.CharField(label='Wydawca', required=False, max_length=100, widget=floppyforms.widgets.Input(
        datalist={m['publisher'] for m in Book.objects.values('publisher')},
        attrs={'autocomplete': 'off', "class": "form-control"}))
    published_city = forms.CharField(label='Miasto wydawcy', required=False, max_length=100,
                                     widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}))
    published_year = forms.CharField(label='Rok publikacji', required=False, max_length=100,
                                     widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}))
    bought_date1 = forms.DateField(label="Od kiedy", widget=DateInput(attrs={"class": "form-control", "autocomplete": "off"}), required=False)
    bought_date2 = forms.DateField(label="Do kiedy", widget=DateInput(attrs={"class": "form-control", "autocomplete": "off"}), required=False)
    localization = forms.CharField(label='Lokalizacja', required=False, max_length=100,
                                   widget=floppyforms.widgets.Input(
                                       datalist={m['name'] for m in Shelve.objects.values('name')},
                                       attrs={'autocomplete': 'off', "class": "form-control"}))
    category = forms.CharField(label='Kategorie', required=False, max_length=100, widget=floppyforms.widgets.Input(
        datalist={m['name'] for m in BookCategory.objects.values('name')},
        attrs={'autocomplete': 'off', "class": "form-control"}))


class Book_form(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ("id", "author", "title", "ISBN", "publisher", "published_city", "published_year", "price",
                  "bought_date", "details", "categories", "physical_location")
        labels = {"author": "Autor",
                  "title": "Tytuł",
                  "ISBN": "ISBN",
                  "publisher": "Wydawca",
                  "published_city": "Miasto wydawcy",
                  "published_year": "Rok publikacji",
                  "price": "Cena",
                  "bought_date": "Data zakupu",
                  "details": "Opis",
                  "categories": "Kategorie",
                  "physical_location": "Półka"
                  }
        widgets = {
            "author": floppyforms.widgets.Input(datalist={m['author'] for m in Book.objects.values('author')},
                                                attrs={'autocomplete': 'off', 'class': 'form-control',
                                                       'required': "True"}),
            "physical_location": floppyforms.widgets.Input(datalist=[m['name'] for m in Shelve.objects.values('name')],
                                                           attrs={'autocomplete': 'off', 'class': 'form-control',
                                                                  'required': "True"}),

            "title": forms.TextInput(attrs={"class": "form-control", "required": "True", "autocomplete": "off"}),
            "ISBN": forms.TextInput(attrs={"class": "form-control", "required": "True", "autocomplete": "off"}),
            "publisher": floppyforms.widgets.Input(datalist={m['publisher'] for m in Book.objects.values('publisher')},
                                                   attrs={'autocomplete': 'off', "class": "form-control"}),
            "published_city": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "published_year": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),

            "price": forms.NumberInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "bought_date": forms.DateInput(format='%m-%d-%Y', attrs={"class": "form-control", "autocomplete": "off"}),
            "details": forms.Textarea(attrs={"class": "form-control", "autocomplete": "off"}),
            "categories": forms.Textarea(attrs={"class": "form-control", "autocomplete": "off"}),
        }


class Shelve_search_form(forms.ModelForm):
    class Meta:
        model = models.Shelve
        fields = ("name", "details")
        labels = {"name": "nazwa",
                  "details": "Opis"}
        widgets = {
            "details": forms.Textarea(attrs={"class": "form-control", 'rows': 1, "autocomplete": "off"}),
            "name": floppyforms.widgets.Input(datalist={m['name'] for m in Shelve.objects.values('name')},
                                              attrs={'autocomplete': 'off', 'class': 'form-control',
                                                     'required': "True"}),
        }


class Book_category_search_form(forms.ModelForm):
    class Meta:
        model = models.BookCategory
        fields = ("name",)
        labels = {"name": "nazwa", }
        widgets = {
            "name": floppyforms.widgets.Input(datalist={m['name'] for m in BookCategory.objects.values('name')},
                                              attrs={'autocomplete': 'off', 'class': 'form-control',
                                                     'required': "True"}),
        }


