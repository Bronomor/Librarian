let MAX_ADDED_BOOKS = 10
let ADDED_TEMPORARY_BOOKS = 0
let AVAILABLE_SLOTS   = new Array(MAX_ADDED_BOOKS)
let myInterval_Search = new Array(MAX_ADDED_BOOKS)

for (let i=0; i<MAX_ADDED_BOOKS; i++){
    AVAILABLE_SLOTS[i] = 0
}


function add_book_slot(){

    if(ADDED_TEMPORARY_BOOKS >= MAX_ADDED_BOOKS) return

    let slots_number = parseInt(document.getElementById("slot_text_idx2").innerHTML)
    document.getElementById("slot_text_idx2").innerHTML = slots_number + 1


    let ACTUALLY_ADDING = -1

    for(let i=0; i<MAX_ADDED_BOOKS; i++){
        if(!AVAILABLE_SLOTS[i]) {
            AVAILABLE_SLOTS[i] = 1
            ACTUALLY_ADDING = i
            break
        }
    }

    if(ACTUALLY_ADDING <= -1) return

    let container_book = document.createElement('div')
        container_book.id = "container_book" + ACTUALLY_ADDING
        container_book.className = "container_book_class"
    let text_isbn = "Wpisz ISBN, aby wyszukać księżkę w globalnej bazie"

    let input_isbn = document.createElement('input')
        input_isbn.type = "text"
        input_isbn.id = "input_isbn"+ACTUALLY_ADDING
        input_isbn.placeholder = "podaj ISBN"
        input_isbn.className = "form-control"


    let button_search = document.createElement('button')
        button_search.id = "button_search" + ACTUALLY_ADDING
        button_search.addEventListener("click", function(){
            search_book_ajax();
        }, false)
        button_search.innerText = "Wyszukaj"
        button_search.className = "btn btn-info"


    let button_release = document.createElement('button')
        button_release.innerText = "Zwolnij slot"
        button_release.disabled = true
        button_release.id = "button_release"+ACTUALLY_ADDING
        button_release.addEventListener("click", function(){
            release_slot_ajax(ACTUALLY_ADDING);
        }, false)
        button_release.className = "btn btn-info"

    container_book.innerHTML = text_isbn
    container_book.appendChild(document.createElement("br"))
    container_book.appendChild(input_isbn)
    container_book.appendChild(document.createElement("br"))
    container_book.appendChild(button_search)
    container_book.appendChild(button_release)
    container_book.appendChild(document.createElement("br"))
    document.getElementById("main_article").appendChild(container_book)
    ADDED_TEMPORARY_BOOKS += 1
}

function add_book(search_idx){
    let form_name = "book_form" + search_idx

    let form = document.getElementById(form_name)

    if (!form.checkValidity()) {
        console.log('not valid');
        return
    }


    let form_data = new FormData(form)
    form_data.append('csrfmiddlewaretoken', csrfValue)
    form_data.append('search_idx', search_idx)
    form_data.append('adding', 1)

    $.ajax({
        type: 'POST',
        url: $(form_name).attr("action"),
        data: form_data,
        success: function(response) {
            console.log(response)
        },
        error: function (error){
            console.log(this.error)
        },
        cache: false,
        contentType: false,
        processData: false,
    });
}

function temporary_book_pass_data(search_idx, data){

    let div = document.getElementById("container_book"+search_idx)
    let form = document.createElement("form")
    form.id = "book_form" + search_idx

    form.insertAdjacentHTML('beforeend', data.book_form)
    $(function () {
        $('#container_book' + search_idx + ' #id_bought_date').datepicker({
            'format': 'dd-mm-yyyy',
            'autoclose': true
        });
    });

    let button_add_book = document.createElement("button")
    button_add_book.addEventListener("click", function (){
        add_book(search_idx);
    },false );
    button_add_book.type="button"
    button_add_book.innerText = "Dodaj książkę"
    button_add_book.id = "book_button_add"+search_idx
    button_add_book.className = "btn btn-info"

    form.appendChild(button_add_book)
    div.appendChild(form)
}


function wait_for_search_result(search_idx){
    fetch("/add_books", {
        method: "Post",
        headers: {
            "X-CSRFToken": csrfValue,
            "X-Requested-With": "XMLHttpRequest",
        },
        body: "wait_signal;"+search_idx
    }).then(function (response) {
        return response.json()
    }).then(function (data) {
        if(!data["status"]){
            document.getElementById("numb"+search_idx).innerText += 10
        }
        else{
            clearInterval(myInterval_Search[search_idx])
            temporary_book_pass_data(search_idx, data)
            remove_timer(search_idx)
            document.getElementById("button_release"+search_idx).disabled = false
        }
    }).catch((error) => {
        //
    })
}

function search_book_ajax(){

    let idx = event.srcElement.id.slice(-1)
    let isbn = document.getElementById("input_isbn"+idx).value
    if(isbn.length !== 13) {
        console.log("zły isbn")
        return
    }

    document.getElementById("button_search"+idx).disabled = true

    timer_own(idx)

    myInterval_Search[idx] = setInterval(wait_for_search_result, 5000, idx)

    let data = idx + ";" + isbn
    fetch("/add_books", {
        method: "Post",
        headers: {
            "X-CSRFToken": csrfValue,
            "X-Requested-With": "XMLHttpRequest",
        },
        body: data
    }).then(function (response) {
        return response.json()
    }).then(function (data) {
        //
    }).catch((error) => {
        //
    })
}

function clean_after_book_slot(search_idx){

    let container = document.getElementById("container_book"+search_idx)
    while (container.firstChild) {
        console.log("child")
        container.removeChild(container.lastChild);
    }
    container.remove()

    AVAILABLE_SLOTS[search_idx] = 0
}

function release_slot_ajax(search_idx) {

    document.getElementById("button_search"+search_idx).disabled = false
    document.getElementById("button_release"+search_idx).disabled = true

    let form_name = "book_form" + search_idx
    let form_data = new FormData()
    form_data.append('csrfmiddlewaretoken', csrfValue)
    form_data.append('search_idx', search_idx)
    form_data.append('delete', 1)

    $.ajax({
      type: 'POST',
      url: $(form_name).attr("action"),
      data: form_data,
      success: function(response) {
          console.log("usunięto")
          clean_after_book_slot(search_idx)
          console.log(response)
      },
      error: function (error){
          console.log("nie usunięto")
          console.log(this.error)
      },
      cache: false,
      contentType: false,
      processData: false,
    });
}


