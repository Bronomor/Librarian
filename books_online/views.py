import csv
import zipfile
import codecs
from io import BytesIO
import threading
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
import time as t
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from .models import Temporary_book, Book, Shelve, BookCategory
from django.db.models import Q
from .forms import Shelve_form, BookCategory_form, Search_form, Book_form, Book_category_search_form, \
    Shelve_search_form, Shelve_change_form
from datetime import datetime
from django.db.utils import IntegrityError
from django.db.models import Count
import os
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options


# Create your views here.


def settings_site(driver, data_to_search, data_type):
    search_box = driver.find_element_by_name('st1')
    search_box.send_keys(data_to_search)

    label_data_type = driver.find_element_by_name("label1")
    for option in label_data_type.find_elements_by_tag_name('option'):
        if option.text == data_type:
            option.click()

    for element in driver.find_elements_by_name('lib_ch[]'):
        try:
            element.click()
        except WebDriverException:
            print("Element is not clickable")

    search_button = driver.find_element_by_name("szukaj")
    search_button.click()


def results_page(driver, temporary_book):
    table = driver.find_element_by_id('karo_d_content')
    links = table.find_elements_by_xpath('.//a[contains(@href,href)]')

    if links:
        links[0].click()

    data = driver.find_elements_by_class_name("pole")
    labels = driver.find_elements_by_class_name("nazwa_pola")

    if data.__len__() <= 0:
        temporary_book.details = "Nie znaleziono w bazie takiej książki o takim ISBN. Czy ona na pewno istnieje ?"
    else:
        idx = 0
        temporary_book.details = ""
        for label in labels:
            if label.text == "Hasło główne":
                temporary_book.author = data[idx].text
            elif label.text == "Tytuł":
                temporary_book.title = data[idx].text
            elif label.text == "Wydano":
                colon = data[idx].text.find(':')
                comma = data[idx].text.find(',')

                temporary_book.published_city = data[idx].text[:colon]
                temporary_book.publisher = data[idx].text[colon + 1: comma]
                temporary_book.published_year = data[idx].text[comma + 1:]
            elif label.text == "ISBN":
                pass
            elif label.text == "Hasło przedm.":
                categories = ''
                category = ''
                writing = True

                word = data[idx].text

                for i in range(0, len(word)):
                    if word[i] == '\n' or word[i] == '\r':
                        writing = True

                        categories += category + " , "

                        try:
                            BookCategory.objects.get(name=category)
                        except ObjectDoesNotExist:
                            BookCategory.objects.create(name=category)

                        category = ''

                    if word[i] == '-' and word[i + 1] == '-':
                        writing = False
                    if writing and word[i] != '\n' and word[i] != '\r':
                        category += word[i]

                if category:
                    categories += category + " , "

                temporary_book.categories = categories
            else:
                temporary_book.details += label.text + "\n" + data[idx].text + "\n\n"
            idx += 1

    temporary_book.is_complete_search = True
    temporary_book.save()


def search_in_global_library(data="9788377972298", data_type="ISBN", temporary_book=None,
                             url='https://karo.umk.pl/Karo/'):
    # driver = webdriver.Remote("http://localhost:4444/wd/hub", desired_capabilities=DesiredCapabilities.CHROME)

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get(url)

    settings_site(driver, data, data_type)
    t.sleep(33)
    results_page(driver, temporary_book)

    driver.close()


def text_category_parser(text):
    results = []
    word = ''
    used_category = set()

    def find_index():

        nonlocal results
        nonlocal word
        nonlocal used_category

        without_space_pos_start = 0
        while without_space_pos_start < len(word) and word[without_space_pos_start].isspace():
            without_space_pos_start += 1

        without_space_pos_end = len(word) - 1
        while without_space_pos_end > -1 and word[without_space_pos_end].isspace():
            without_space_pos_end -= 1
        without_space_pos_end += 1

        if word[without_space_pos_start:without_space_pos_end]:
            all_cats = BookCategory.objects.filter(name=word[without_space_pos_start:without_space_pos_end])
            for cat in all_cats:
                results.append(cat.id)
                used_category.add(word[without_space_pos_start:without_space_pos_end])

    for i in range(0, len(text)):
        if text[i] == ',' or text[i] == '.':
            find_index()
            word = ''
        elif text[i] != '\r' or text[i] != '\n':
            word += text[i]
    else:
        find_index()

    return results, used_category


def book_object_filling(request, id='', old_idx=''):
    something_change = False
    first_add = False

    categories_set = set()

    if id:
        book = Book.objects.get(serial_key=old_idx)
    else:
        book = Book()
        id = request.POST.get("search_idx")
        old_idx = id
        first_add = True

    for obj in Temporary_book._meta.get_fields():
        try:
            book_data = book.__getattribute__(obj.name)
        except:
            book_data = 'None'

        data = request.POST.get(f"prefix{id}-{obj.name}")

        if obj.name != "id" and str(book_data) != str(data) and (book_data or data) or first_add:
            something_change = True
            if obj.name == "physical_location" and data:
                setattr(book, obj.name, Shelve.objects.get(name=data))
            elif obj.name == "price" and data == '':
                pass
            elif obj.name == "bought_date":
                if data:
                    date = datetime.strptime(data, '%d-%m-%Y').strftime('%Y-%m-%d')
                    setattr(book, obj.name, date)
            elif obj.name == "categories":
                if not first_add:
                    parsed_category, categories_set = text_category_parser(data)
                    string_categories = ''
                    for elem in categories_set:
                        string_categories += elem + ', '
                    setattr(book, obj.name, string_categories)
                    book.categories_fk.set(parsed_category)
                else:
                    setattr(book, obj.name, data)
                    categories_set.add(data)
            else:
                setattr(book, obj.name, data)

    if something_change:
        book.save()

    if first_add:
        parsed_category, categories_set = text_category_parser(request.POST.get(f"prefix{id}-categories"))
        string_categories = ''
        for elem in categories_set:
            string_categories += elem + ', '
        setattr(book,  "categories", string_categories)
        book.categories_fk.set(parsed_category)
        book.save()

    return categories_set


def add_book_view(request, *args, **kwargs):
    if request.is_ajax():
        if request.POST.get('adding'):
            idx = request.POST.get('search_idx')
            dict_copy = request.POST.copy()
            try:
                dict_copy[f'prefix{idx}-physical_location'] = Shelve.objects.get(
                    name=request.POST.get(f'prefix{idx}-physical_location'))
            except:
                pass  # todo...

            book_form = Book_form(dict_copy or None, prefix="prefix" + request.POST.get("search_idx"))
            if book_form.is_valid():
                book_object_filling(request)
                string_form = create_book_form(book_form, request.POST.get("search_idx"),
                                               dict_copy[f'prefix{idx}-physical_location'], True)
                return JsonResponse({'success': True, 'book_form': string_form}, status=200)
            else:
                string_form = create_book_form(book_form, request.POST.get("search_idx"),
                                               dict_copy[f'prefix{idx}-physical_location'], True)
                return JsonResponse({'success': False, 'book_form': string_form}, status=200)
        elif request.POST.get('delete'):
            var = Temporary_book.objects.get(search_number=request.POST.get("search_idx"))
            var.delete()
            return JsonResponse({}, status=200)
        elif request.POST.get('mode') == 'start_searching_book_g_library':
            idx = request.POST.get('search_idx')
            ISBN = request.POST.get('isbn')

            try:
                val = Temporary_book.objects.get(search_number=idx)
                if val:
                    val.delete()
            except ObjectDoesNotExist:
                pass  # if object not exist we dont need to release slot

            temporary_book = Temporary_book()
            temporary_book.search_number = idx
            temporary_book.ISBN = ISBN
            temporary_book.save()

            try:
                thread_ = threading.Thread(target=search_in_global_library(ISBN, "ISBN", temporary_book), daemon=True)
                thread_.start()
            except:
                book_form = Book_form(None, prefix="prefix" + request.POST.get("search_idx"))
                string_form = create_book_form(book_form, request.POST.get("search_idx"))
                return JsonResponse({"search_index": idx, "book_form": string_form}, status=200)
            return JsonResponse({"search_index": idx}, status=200)

        elif request.POST.get('mode') == 'searching_book_g_library_results':
            idx = request.POST.get('search_idx')
            temp_obj = Temporary_book.objects.get(search_number=idx)

            if temp_obj.is_complete_search:

                data = {"success": 1}

                book_data = Book()
                for obj in Temporary_book._meta.get_fields():
                    setattr(book_data, obj.name, temp_obj.__getattribute__(obj.name))
                book_form = Book_form(instance=book_data, prefix="prefix" + str(request.POST.get('search_idx')))
                string_form = create_book_form(book_form, idx)
                data["book_form"] = string_form

                return JsonResponse(data, status=200)
            else:
                return JsonResponse({"success": 0}, status=200)

    context = {'datalist_author': {m['author'] for m in Book.objects.values('author')},
               'datalist_location': {m['name'] for m in Shelve.objects.values('name')},
               'datalist_publisher': {m['publisher'] for m in Book.objects.values('publisher')},
               'datalist_category': {m['name'] for m in BookCategory.objects.values('name')}}

    return render(request, 'add_books.html', context)


def main_site(request, *args, **kwargs):
    return render(request, 'main_site.html', {})


def add_shelves(request, *args, **kwargs):
    if request.method == 'POST':
        form = Shelve_form(request.POST)
        if form.is_valid():
            obj = Shelve.objects.create()
            obj.name = form.cleaned_data['name']
            obj.details = form.cleaned_data['details']
            obj.save()
    else:
        form = Shelve_form()
    return render(request, 'add_shelve.html', {'form': form})


def add_category(request, *args, **kwargs):
    if request.method == 'POST':
        form = BookCategory_form(request.POST)
        if form.is_valid():
            obj = BookCategory.objects.create()
            obj.name = form.cleaned_data['name']
            obj.save()
    else:
        form = BookCategory_form()

    return render(request, 'add_category.html', {'form': form})


def create_book_form(book_form, search_idx, shelve_name='', validate_mode=False, change_book=False, categories_set = ''):
    def validate_messages(string_repr, name):
        nonlocal string_form, error_dict, validate_mode
        if not validate_mode:
            string_form += string_repr + '</div>'
        else:
            try:
                error_text = str(error_dict[name])[26:-10]
                class_position = string_repr.find("class=")
                string_form += string_repr[
                               :class_position] + 'class="form-control input form-control is-invalid" ' + string_repr[
                                                                                                          class_position + 20:]
                string_form += f'<span id="error_1_id_prefix{search_idx}-{name}" class="invalid-feedback"><strong>{error_text}</strong></span>' + '</div>'
            except BaseException as e:
                class_position = string_repr.find("class=")
                string_form += string_repr[
                               :class_position] + 'class="form-control input form-control is-valid" ' + string_repr[
                                                                                                        class_position + 20:] + '</div>'

    string_form = '<div class="row">'
    string_form += '<div id="header_part1" onclick="switch_sub_menu(\'1\')" class="slot_sub_menu_active col-md-3"> Główne </div>' \
                   '<div id="header_part2" onclick="switch_sub_menu(\'2\')" class="slot_sub_menu_inactive col-md-3"> Opcjonalne </div>' \
                   '<div id="header_part3" onclick="switch_sub_menu(\'3\')" class="slot_sub_menu_inactive col-md-3"> Media </div>' \
                   '<div id="header_part4" onclick="switch_sub_menu(\'4\')" class="slot_sub_menu_inactive col-md-3"> Wypożyczenia </div>' \
                   '</div>'

    error_dict = {}
    for name, error in book_form.errors.items():
        error_dict[name] = error

    string_form += '<div id="part1"> <div class="row"> '
    if not change_book:
        string_form += '<div class="col-md-6">' + f'<label for="id_prefix{search_idx}-serial_key" class="form-label-sm"> {book_form["serial_key"].label} </label>'
        validate_messages(str(book_form["serial_key"]), "serial_key")
    else:
        string_form += '<div class="col-md-6">' + f'<label for="id_prefix{search_idx}-serial_key" class="form-label-sm"> Numer katalogowy </label>'
        string_form += f"<input type='text' name='prefix{search_idx}-serial_key' value='{book_form['serial_key'].value()}'" \
                       f" class='form-control input form-control is-valid' required='' autocomplete='off' maxlength='100' id='id_prefix{search_idx}-serial_key'> </div>"
    string_form += '<div class="col-md-6">' + f'<label for="id_prefix{search_idx}-ISBN" class="form-label-sm"> {book_form["ISBN"].label} </label>'
    validate_messages(str(book_form["ISBN"]), "ISBN")
    string_form += '</div>'
    string_form += '<div class="col-md-12">' + f'<label for="id_prefix{search_idx}-author" class="form-label-sm"> {book_form["author"].label} </label>'
    validate_messages(str(book_form["author"]), "author")
    string_form += '<div class="col-md-12">' + f'<label for="id_prefix{search_idx}-title" class="form-label-sm"> {book_form["title"].label} </label>'
    validate_messages(str(book_form["title"]), "title")
    string_form += '<div class="col-md-12">' + f'<label for="id_prefix{search_idx}-physical_location" class="form-label-sm"> {book_form["physical_location"].label} </label>'
    if shelve_name:
        string_representation = str(book_form["physical_location"])
        idx_value_start = string_representation.find("value=")
        if idx_value_start >= 0:
            idx_value_end = string_representation.find(" ", 44)
            string_representation = string_representation[:idx_value_start] + "value=\"" + str(shelve_name) + "\"" + string_representation[idx_value_end:]
        validate_messages(string_representation, "physical_location")
    else:
        validate_messages(str(book_form["physical_location"]), "physical_location")
    string_form += '<div class="col-md-12">' + f'<label for="id_prefix{search_idx}-categories" class="form-label-sm"> {book_form["categories"].label} </label>'
    if categories_set:
        string_form += f"<textarea name='prefix{search_idx}-categories' cols='40' rows='10' " \
                       f"class='form-control input form-control is-valid' autocomplete='off' maxlength='1000' id='id_prefix{search_idx}-categories'>"
        for elem in categories_set:
            string_form += elem + ', '
        string_form += f"</textarea>"
    else:
        validate_messages(str(book_form["categories"]), "categories")

    button_search_loc = f'<button type="button" onclick = "func_search_loc(\'{search_idx}\')" class ="btn btn-success"> Edytuj półki </button>'
    button_add_loc = f'<button type="button"  onclick = "func_add_loc(\'{search_idx}\')" class ="btn btn-success"> Dodaj półkę </button>'
    button_add_cat = f'<button type="button"  onclick = "func_add_cat(\'{search_idx}\')" class ="btn btn-success"> Dodaj kategorie </button>'
    button_search_cat = f'<button type="button"  onclick = "func_search_cat(\'{search_idx}\')" class ="btn btn-success"> Edytuj kategorie </button>'
    string_form += '<div class="row">'
    string_form += '<div class="col">' + button_add_loc + '</div>'
    string_form += '<div class="col">' + button_search_loc + '</div>'
    string_form += '<div class="col">' + button_add_cat + '</div>'
    string_form += '<div class="col">' + button_search_cat + '</div>'
    string_form += '</div>'

    string_form += '</div> </div>'

    string_form += '<div id="part2" style="display: none;"> '
    string_form += '<div class="col-md-12">' + f'<label for="id_prefix{search_idx}-publisher" class="form-label-sm"> {book_form["publisher"].label} </label>'
    validate_messages(str(book_form["publisher"]), "publisher")

    string_form += '<div class="row">'
    string_form += '<div class="col-md-6">' + f'<label for="id_prefix{search_idx}-published_city" class="form-label-sm"> {book_form["published_city"].label} </label>'
    validate_messages(str(book_form["published_city"]), "published_city")
    string_form += '<div class="col-md-6">' + f'<label for="id_prefix{search_idx}-published_year" class="form-label-sm"> {book_form["published_year"].label} </label>'
    validate_messages(str(book_form["published_year"]), "published_year")
    string_form += "</div>"

    string_form += '<div class="row">'
    string_form += '<div class="col-md-6">' + f'<label for="id_prefix{search_idx}-price" class="form-label-sm"> {book_form["price"].label} </label>'
    validate_messages(str(book_form["price"]), "price")
    string_form += '<div class="col-md-6">' + f'<label for="id_prefix{search_idx}-bought_date" class="form-label-sm"> {book_form["bought_date"].label} </label>'
    validate_messages(str(book_form["bought_date"]), "bought_date")
    string_form += "</div>"
    string_form += '<div class="col-md-12">' + f'<label for="id_prefix{search_idx}-details" class="form-label-sm"> {book_form["details"].label} </label>'
    validate_messages(str(book_form["details"]), "details")
    string_form += '</div>'

    string_form += '<div id="part3" style="display: none;"> '
    string_form += '</div>'

    string_form += '<div id="part4" style="display: none;"> '
    string_form += '</div>'

    return string_form


def search_books_view(request, *args, **kwargs):
    context = {'form': Search_form()}
    if request.is_ajax():
        if request.POST.get('mode') == "search_book":
            book_object = Book.objects.get(serial_key=request.POST.get('serial_key'))
            book_form = Book_form(instance=book_object, prefix="prefix" + str(request.POST.get('serial_key')))
            shelve_name = book_object.physical_location
            string_form = create_book_form(book_form, request.POST.get('serial_key'), shelve_name)
            return JsonResponse({"book_form": string_form}, status=200)
        elif request.POST.get('mode') == "change_book":

            container_slot = request.POST.get("container_slot")
            old_idx = request.POST.get("old_serial_key")
            idx = request.POST.get(f"prefix{container_slot}-serial_key")

            dict_copy = request.POST.copy()

            if dict_copy.get(f'prefix{container_slot}-physical_location', False):
                dict_copy[f'prefix{container_slot}-physical_location'] = Shelve.objects.get(name=request.POST.get(f'prefix{container_slot}-physical_location'))

            book_form = Book_form(dict_copy or None, prefix="prefix" + str(container_slot))

            if book_form.is_valid():
                categories_set = book_object_filling(request, container_slot, old_idx)
                string_form = create_book_form(book_form, container_slot, dict_copy[f'prefix{container_slot}-physical_location'], True, False, categories_set)
                return JsonResponse({'success': True, "changed_title": request.POST.get(f'prefix{container_slot}-title'), "new_idx": idx,
                                     'string_form': string_form}, status=200)
            elif idx == old_idx and len(book_form.errors) == 1:
                categories_set = book_object_filling(request, container_slot , old_idx)
                string_form = create_book_form(book_form, container_slot, dict_copy[f'prefix{container_slot}-physical_location'], True, True, categories_set)
                return JsonResponse({'success': True, "changed_title": request.POST.get(f'prefix{container_slot}-title'), "new_idx": idx,
                                     'string_form': string_form}, status=200)
            elif idx == old_idx:
                book_object = Book.objects.get(serial_key=old_idx)
                shelve_name = book_object.physical_location
                string_form = create_book_form(book_form, container_slot, shelve_name, True, True)
                return JsonResponse({'success': False, 'string_form': string_form}, status=200)
            else:
                book_object = Book.objects.get(serial_key=old_idx)
                shelve_name = book_object.physical_location
                string_form = create_book_form(book_form, container_slot, shelve_name, True)
                return JsonResponse({'success': False, 'string_form': string_form}, status=200)
        else:
            Book.objects.get(serial_key=request.POST.get('serial_key')).delete()
            return JsonResponse({}, status=200)

    elif request.method == 'POST':
        author = request.POST.get('author')
        title = request.POST.get('title')
        ISBN = request.POST.get('ISBN')
        publisher = request.POST.get('publisher')
        published_city = request.POST.get('published_city')
        published_year = request.POST.get('published_year')

        bought_date_1 = request.POST.get('bought_date1')
        if not bought_date_1:
            bought_date_1 = ""

        bought_date_2 = request.POST.get('bought_date2')
        if not bought_date_2:
            bought_date_2 = ""

        localization = request.POST.get('localization')
        category = request.POST.get('category')

        sort_option = request.POST.get("sort_options")

        if sort_option == 'title_asc':
            tmp_res = {m['serial_key']: m['title'] for m in Book.objects.filter(
                Q(author__contains=author), Q(title__contains=title),
                Q(ISBN__contains=ISBN), Q(publisher__contains=publisher),
                Q(published_city__contains=published_city), Q(published_year__contains=published_year),
                Q(physical_location__name__contains=localization), Q(categories__contains=category)
            ).values('title', 'serial_key').order_by("title")}
        elif sort_option == 'title_desc':
            tmp_res = {m['serial_key']: m['title'] for m in Book.objects.filter(
                Q(author__contains=author), Q(title__contains=title),
                Q(ISBN__contains=ISBN), Q(publisher__contains=publisher),
                Q(published_city__contains=published_city), Q(published_year__contains=published_year),
                Q(physical_location__name__contains=localization), Q(categories__contains=category)
            ).values('title', 'serial_key').order_by("-title")}
        elif sort_option == 'selve_asc':
            tmp_res = {m['serial_key']: m['title'] for m in Book.objects.filter(
                Q(author__contains=author), Q(title__contains=title),
                Q(ISBN__contains=ISBN), Q(publisher__contains=publisher),
                Q(published_city__contains=published_city), Q(published_year__contains=published_year),
                Q(physical_location__name__contains=localization), Q(categories__contains=category)
            ).values('title', 'serial_key').order_by("physical_location")}
        elif sort_option == 'selve_desc':
            tmp_res = {m['serial_key']: m['title'] for m in Book.objects.filter(
                Q(author__contains=author), Q(title__contains=title),
                Q(ISBN__contains=ISBN), Q(publisher__contains=publisher),
                Q(published_city__contains=published_city), Q(published_year__contains=published_year),
                Q(physical_location__name__contains=localization), Q(categories__contains=category)
            ).values('title', 'serial_key').order_by("-physical_location")}
        else:
            tmp_res = {m['serial_key']: m['title'] for m in Book.objects.filter(
                Q(author__contains=author), Q(title__contains=title),
                Q(ISBN__contains=ISBN), Q(publisher__contains=publisher),
                Q(published_city__contains=published_city), Q(published_year__contains=published_year),
                Q(physical_location__name__contains=localization), Q(categories__contains=category)
            ).values('title', 'serial_key')}

        context["results"] = [*tmp_res.values()]
        context["results2"] = [*tmp_res.keys()]

        # to show user in form what exactly is searching
        context["author"] = author
        context["title"] = title
        context["ISBN"] = ISBN
        context["publisher"] = publisher
        context["published_city"] = published_city
        context["published_year"] = published_year
        context["bought_date_1"] = bought_date_1
        context["bought_date_2"] = bought_date_2
        context["localization"] = localization
        context["category"] = category
        context["sort_option"] = sort_option

    context['datalist_author'] = {m['author'] for m in Book.objects.values('author')}
    context['datalist_location'] = {m['name'] for m in Shelve.objects.values('name')}
    context['datalist_publisher'] = {m['publisher'] for m in Book.objects.values('publisher')}
    context['datalist_category'] = {m['name'] for m in BookCategory.objects.values('name')}

    return render(request, 'search_books.html', context)


def shelves_form_string(form, search_idx, first_form=False):
    error_dict = {}
    for name, error in form.errors.items():
        error_dict[name] = error

    if not first_form:
        string_form = '<div class ="row">'
        for name, field in form.fields.items():
            string_representation = str(form[name])
            string_form += '<div class ="col">'
            string_form += f'<label for="id_prefix{search_idx}-{name}" class="form-label"> {field.label} </label>'
            try:
                error_text = error_dict[name]
                class_position = string_representation.find("class=")
                string_form += string_representation[
                               :class_position] + 'class="form-control input form-control is-invalid" ' \
                               + string_representation[class_position + 20:]
                string_form += f'<span id="error_1_id_prefix{search_idx}-{name}" class="invalid-feedback"><strong>{error_text}</strong></span>'
            except:
                class_position = string_representation.find("class=")
                string_form += string_representation[
                               :class_position] + 'class="form-control input form-control is-valid" ' \
                               + string_representation[class_position + 20:]
            string_form += '</div>'
    else:
        string_form = '<div class ="row">'
        for name, field in form.fields.items():
            string_form += '<div class ="col">'
            string_form += f'<label for="id_input_{name}{search_idx}" class="form-label"> {field.label} </label>'
            string_form += str(form[name])
            string_form += '</div>'
    return string_form


def search_shelves_view(request, *args, **kwargs):
    if request.is_ajax():
        if request.POST.get('mode') == "change_book":
            form = Shelve_change_form(request.POST or None, prefix='prefix' + request.POST.get('id'))
            if form.is_valid():
                shelve = Shelve.objects.get(id=request.POST.get('id'))
                setattr(shelve, 'name', request.POST.get(f"prefix{request.POST.get('id')}-name"))
                setattr(shelve, 'details', request.POST.get(f"prefix{request.POST.get('id')}-details"))
                shelve.save()
                form_html = shelves_form_string(form, request.POST.get('id'))
                return JsonResponse({"success": True, "changed_name": shelve.name, "form_html": form_html},
                                    status=200)
            else:
                form_html = shelves_form_string(form, request.POST.get('id'))
                return JsonResponse({"success": False, "form_html": form_html}, status=200)

        elif request.POST.get('mode') == "search_chosen":
            idx = [m['id'] for m in Shelve.objects.filter(
                Q(name__contains=request.POST.get('name')), Q(details__contains=request.POST.get('details'))).values(
                'id')]

            names = [m['name'] for m in Shelve.objects.filter(
                Q(name__contains=request.POST.get('name')), Q(details__contains=request.POST.get('details'))).values(
                'name')]

            details = [m['details'] for m in Shelve.objects.filter(
                Q(name__contains=request.POST.get('name')), Q(details__contains=request.POST.get('details'))).values(
                'details')]

            return JsonResponse({"idx": idx, "names": names, "details": details, "length": len(idx)}, status=200)

        else:
            Shelve.objects.get(id=request.POST.get('id')).delete()
            return JsonResponse({}, status=200)

    else:
        form = Shelve_search_form()
        objects = Shelve.objects.values()

        return render(request, 'search_shelve.html',
                      {"form____": form,
                       "idx": [m['id'] for m in objects.values("id")],
                       "names": [m['name'] for m in objects.values("name")],
                       "details": [m['details'] for m in objects.values("details")]})


def search_category_view(request, *args, **kwargs):
    if request.is_ajax():
        if request.POST.get('mode') == "change_book":
            category = BookCategory.objects.get(id=request.POST.get('id'))

            for obj in BookCategory._meta.get_fields():
                setattr(category, obj.name, request.POST.get(obj.name))
            category.save()

            return JsonResponse({"changed_name": request.POST.get('name')}, status=200)

        elif request.POST.get('mode') == "search_chosen":
            idx = [m['id'] for m in BookCategory.objects.filter(name__contains=request.POST.get('name')).values('id')]
            names = [m['name'] for m in
                     BookCategory.objects.filter(name__contains=request.POST.get('name')).values('name')]

            return JsonResponse({"idx": idx, "names": names, "length": len(idx)}, status=200)

        else:
            objects = Book.objects.filter(categories_fk=request.POST.get('id'))
            if len(objects):
                return JsonResponse({'success': False}, status=200)
            else:
                BookCategory.objects.get(id=request.POST.get('id')).delete()
                return JsonResponse({'success': True}, status=200)

    else:
        form = Book_category_search_form()
        objects = BookCategory.objects.values()

        return render(request, 'search_category.html',
                      {"form____": form,
                       "idx": [m['id'] for m in objects.values("id")],
                       "names": [m['name'] for m in objects.values("name")]})


def handle_object(mode, idx):
    if mode == 'Book':
        obj_handle = Book.objects.get(id=idx)
    elif mode == 'BookCategory':
        obj_handle = BookCategory.objects.get(id=idx)
    elif mode == 'Shelve':
        obj_handle = Shelve.objects.get(id=idx)
    else:
        obj_handle = None

    if mode == 'Book':
        labels = ["serial_key", "author", "title", "ISBN", "publisher", "published_city", "published_year",
                  "price", "bought_date", "details", "physical_location", "categories"]
        source = [obj_handle.serial_key, obj_handle.author, obj_handle.title, obj_handle.ISBN, obj_handle.publisher,
                  obj_handle.published_city, obj_handle.published_year, obj_handle.price,
                  obj_handle.bought_date, obj_handle.details, obj_handle.physical_location, obj_handle.categories]
    elif mode == 'BookCategory':
        labels = ["name"]
        source = [obj_handle.name]
    elif mode == 'Shelve':
        labels = ["name", "details"]
        source = [obj_handle.name, obj_handle.details]
    else:
        labels = ['Error']
        source = ['Error']
    return obj_handle, labels, source


def create_backup_view(request, *args, **kwargs):
    if request.method == "POST":
        context = {
            "Book": serializers.serialize("python", Book.objects.all()),
            "BookCategory": serializers.serialize("python", BookCategory.objects.all()),
            "Shelve": serializers.serialize("python", Shelve.objects.all()),
        }

        zipped_file = BytesIO()
        with zipfile.ZipFile(zipped_file, 'a', zipfile.ZIP_DEFLATED) as zipped:

            for object_type in context:
                file_name = object_type + ".csv"
                with open(file_name, 'w+', newline='', encoding='utf-8') as csv_data:

                    writer = csv.writer(csv_data, delimiter=';')
                    writer.writerow('')

                    objects = context[object_type]

                    for obj in objects:
                        obj_handle, labels, source = handle_object(object_type, obj['pk'])

                        for i in range(len(labels)):
                            writer.writerow([labels[i], source[i]])
                        writer.writerow("")

                    csv_data.seek(0)
                    zipped.writestr("{}.csv".format(object_type), csv_data.read())

        zipped_file.seek(0)
        response = HttpResponse(zipped_file, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=kopia_calej_bazy.zip'

        return response

    return render(request, 'create_backup.html', {})


def load_backup_view(request, *args, **kwargs):

    if request.method == "POST":
        if request.FILES:
            shelve_reader = csv.reader(codecs.iterdecode(request.FILES['shelve_input'], 'utf-8', errors='replace'),
                                       delimiter=';')
            bookcategory_reader = csv.reader(
                codecs.iterdecode(request.FILES['bookcategory_input'], 'utf-8', errors='replace'), delimiter=';')
            book_reader = csv.reader(codecs.iterdecode(request.FILES['book_input'], 'utf-8', errors='replace'),
                                     delimiter=';')

            failed = []

            shelve = Shelve()
            for row in shelve_reader:
                if row:
                    setattr(shelve, row[0], row[1])
                else:
                    try:
                        Shelve.objects.get(name=shelve.name)
                    except Shelve.DoesNotExist as error:
                        if shelve.name:
                            shelve.save()
                    except IntegrityError as e:
                        failed.append(shelve)
                    shelve = Shelve()

            bookcategory = BookCategory()
            for row in bookcategory_reader:
                if row:
                    setattr(bookcategory, row[0], row[1])
                else:
                    if bookcategory.name:
                        try:
                            BookCategory.objects.get(name=bookcategory.name)
                        except BookCategory.DoesNotExist as error:
                            bookcategory.save()
                        except IntegrityError as e:
                            failed.append(shelve)
                    bookcategory = BookCategory()

            book = Book()
            for row in book_reader:
                if row:
                    if row[0] == 'physical_location':
                        shelve_instance = Shelve.objects.get(name=row[1])
                        setattr(book, row[0], shelve_instance)
                    else:
                        if row[1]:
                            setattr(book, row[0], row[1])
                else:
                    if book.title:
                        try:
                            Book.objects.get(serial_key=book.serial_key)
                        except Book.DoesNotExist as error:
                            book.save()
                        except IntegrityError as e:
                            failed.append(book)
                    book = Book()

        return render(request, 'load_backup.html', {"upload_files": True, "failed": failed})

    return render(request, 'load_backup.html', {"upload_files": False})


def statistic_view(request, *args, **kwargs):
    counter_field = 'ISBN'
    page = 1

    if request.method == 'POST':
        page = int(request.POST.get("page"))

    dict = Book.objects.values(counter_field).annotate(the_count=Count(counter_field)).order_by('-the_count')
    slots = min(20, len(dict) - ((page - 1) * 20))

    total_val = (len(dict) - 1) // 20
    all_pages = 1 if total_val < 0 else total_val + 1
    small_dict = dict[(page - 1) * 20: (page - 1) * 20 + slots]

    results = {}

    for obj in small_dict:
        data = Book.objects.filter(ISBN=obj['ISBN'])[:1].values()
        results[obj['ISBN']] = {'author': data[0]['author'], "title": data[0]['title'], 'ISBN': data[0]['ISBN'],
                                "the_count": obj['the_count']}

    context = {
        "results": results,
        "page": page,
        "all_pages": all_pages
    }

    return render(request, 'statistic.html', context)


def test_view(request, *args, **kwargs):
    # if request.method == "POST":
    # if request.FILES:
    # shelve_reader = csv.reader(codecs.iterdecode(request.FILES['shelve_input'], 'utf-8', errors='replace'),
    #                           delimiter=';')

    return render(request, 'test.html', {})
