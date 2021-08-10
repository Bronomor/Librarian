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
from .models import Temporary_book, Book, Shelve, BookCategory, Library

from django.db.models import Q

from .forms import Shelve_form, BookCategory_form, Search_form, Book_form, Book_category_search_form, Shelve_search_form
from datetime import datetime

from django.db.utils import IntegrityError


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
                    if writing:
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
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get(url)

    settings_site(driver, data, data_type)
    t.sleep(33)
    results_page(driver, temporary_book)


def book_object_filling(request, id=''):
    if id:
        book = Book.objects.get(id=request.POST.get('id'))
    else:
        book = Book()

    for obj in Temporary_book._meta.get_fields():
        if obj.name == "physical_location":
            setattr(book, obj.name, Shelve.objects.get(name=request.POST.get("physical_location")))
        elif obj.name == "price" and request.POST.get('price') == '':
            pass
        elif obj.name == "bought_date":
            if not request.POST.get("bought_date") == '':
                date = datetime.strptime(request.POST.get(obj.name), '%d-%m-%Y').strftime('%Y-%m-%d')
                setattr(book, obj.name, date)
        else:
            setattr(book, obj.name, request.POST.get(obj.name))
    book.save()


def add_book_view(request, *args, **kwargs):
    if request.is_ajax():
        if request.POST.get('adding'):
            book_object_filling(request)
            return JsonResponse({}, status=200)
        elif request.POST.get('delete'):
            var = Temporary_book.objects.get(search_number=request.POST.get("search_idx"))
            var.delete()
            return JsonResponse({}, status=200)
        else:
            tmp_data = request.body.decode()
            comma_position = tmp_data.find(';')

            if tmp_data[:comma_position] == "wait_signal":
                idx = tmp_data[comma_position + 1:]
                temp_obj = Temporary_book.objects.get(search_number=idx)
                if temp_obj.is_complete_search:

                    data = {"status": 1}

                    book_data = Book()
                    for obj in Temporary_book._meta.get_fields():
                        setattr(book_data, obj.name, temp_obj.__getattribute__(obj.name))
                    book_form = Book_form(instance=book_data)
                    string_form = create_book_form(book_form, idx)
                    data["book_form"] = string_form

                    return JsonResponse(data, status=200)
                else:
                    return JsonResponse({"status": 0}, status=200)
            else:
                comma_position = tmp_data.find(';')
                idx = tmp_data[:comma_position]
                ISBN = tmp_data[comma_position + 1:]

                try:
                    val = Temporary_book.objects.get(search_number=idx)
                    if val:
                        val.delete()
                except ObjectDoesNotExist:
                    pass

                temporary_book = Temporary_book()
                temporary_book.search_number = idx
                temporary_book.ISBN = ISBN
                temporary_book.save()

                thread_ = threading.Thread(target=search_in_global_library(ISBN, "ISBN", temporary_book), daemon=True)
                thread_.start()

                return JsonResponse({"search_index": idx}, status=200)
    else:
        return render(request, 'add_books.html',
                      {"shelves_name": [m['name'] for m in Shelve.objects.values('name', 'details')]})


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


def create_book_form(book_form, search_idx, shelve_name=''):
    is_odd = 0
    string_form = ''
    for name, field in book_form.fields.items():

        string_representation = str(book_form[name])

        if not is_odd % 4:
            if name != 'details':
                string_form += '<div class="row g-3">'
            else:
                string_form += '<div class="row g-6">'

        if name != 'details' and name != 'categories' and name != 'physical_location':
            string_form += '<div class="col-md-3">' + f'<label for="id_{name}" class="form-label-sm"> {field.label} </label>'
        elif name == 'physical_location':
            string_form += '<div class="col-md-12">' + f'<label for="id_{name}" class="form-label-sm"> {field.label} </label>'

            idx_value_start = string_representation.find("value=")
            idx_value_end = string_representation.find(" ", 44)
            string_representation = string_representation[:idx_value_start] + "value=\"" + str(
                shelve_name) + "\"" + string_representation[idx_value_end:]
        else:
            string_form += '<div class="col-md-6">' + f'<label for="id_{name}" class="form-label-sm"> {field.label} </label>'

        string_form += string_representation + '</div>'

        if not (is_odd + 1) % 4:
            string_form += '</div>'

        is_odd += 1
    string_form += '</div> </br>'

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

    return string_form


def search_books_view(request, *args, **kwargs):
    context = {'form': Search_form()}

    if request.is_ajax():
        if request.POST.get('mode') == "search_book":
            book_object = Book.objects.get(id=request.POST.get('id'))
            book_form = Book_form(instance=book_object)
            shelve_name = book_object.physical_location
            string_form = create_book_form(book_form, request.POST.get('id'), shelve_name)
            return JsonResponse({"book_form": string_form}, status=200)
        elif request.POST.get('mode') == "change_book":
            book_object_filling(request, request.POST.get("id"))
            return JsonResponse({"changed_title": request.POST.get('title')}, status=200)
        else:
            Book.objects.get(id=request.POST.get('id')).delete()
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

        tmp_res = {m['id']: m['title'] for m in Book.objects.filter(
            Q(author__contains=author), Q(title__contains=title),
            Q(ISBN__contains=ISBN), Q(publisher__contains=publisher),
            Q(published_city__contains=published_city), Q(published_year__contains=published_year),
            Q(physical_location__name__contains=localization), Q(categories__contains=category)
        ).values('title', 'id')}

        context["results"] = [*tmp_res.values()]
        context["results2"] = [*tmp_res.keys()]

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

    return render(request, 'search_books.html', context)


def search_shelves_view(request, *args, **kwargs):
    if request.is_ajax():
        if request.POST.get('mode') == "change_book":
            shelve = Shelve.objects.get(id=request.POST.get('id'))

            for obj in Shelve._meta.get_fields():
                setattr(shelve, obj.name, request.POST.get(obj.name))
            shelve.save()

            return JsonResponse({"changed_name": request.POST.get('name')}, status=200)

        elif request.POST.get('mode') == "search_chosen":
            print(request.POST)

            idx = [m['id'] for m in Shelve.objects.filter(
                Q(name__contains=request.POST.get('name')), Q(details__contains=request.POST.get('details'))).values('id')]

            names = [m['name'] for m in Shelve.objects.filter(
                Q(name__contains=request.POST.get('name')), Q(details__contains=request.POST.get('details'))).values('name')]

            details = [m['details'] for m in Shelve.objects.filter(
                Q(name__contains=request.POST.get('name')), Q(details__contains=request.POST.get('details'))).values('details')]

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
    form = Book_category_search_form()
    return render(request, 'search_category.html', {"form": form})


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
        labels = ["id", "author", "title", "ISBN", "publisher", "published_city", "published_year",
                  "price", "bought_date", "details", "physical_location", "categories"]
        source = [obj_handle.id, obj_handle.author, obj_handle.title, obj_handle.ISBN, obj_handle.publisher,
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
        print(request.FILES)
        print(request.POST)
        print("asdsa")
        if request.FILES:
            shelve_reader = csv.reader(codecs.iterdecode(request.FILES['shelve_input'], 'utf-8', errors='replace'),
                                       delimiter=';')
            bookcategory_reader = csv.reader(
                codecs.iterdecode(request.FILES['bookcategory_input'], 'utf-8', errors='replace'), delimiter=';')
            book_reader = csv.reader(codecs.iterdecode(request.FILES['book_input'], 'utf-8', errors='replace'),
                                     delimiter=';')

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
                        print("error")
                        print(shelve)
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
                            print("error")
                            print(bookcategory)
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
                            Book.objects.get(id=book.pk)
                        except Book.DoesNotExist as error:
                            book.save()
                        except IntegrityError as e:
                            print("error")
                            print(book)
                    book = Book()

    return render(request, 'load_backup.html', {})
