class Node {
    constructor(prev, value, next) {
        this.value = value
        this.next = next
        this.prev = prev
    }
}

class List{
    constructor() {
        this.root = null;
        this.end_node = null;
    }
    set_root(node){
        this.root = node;
        this.end_node = node;
    }
    get_root(){
        return this.root;
    }
    find(value){
        let node = this.root
        while(node.next){
            if(node.value === value) return node
            else node = node.next
        }
        return null
    }

    add_node(value){
        if(this.root){
            let new_node = new Node(this.end_node, value, null)
            this.end_node.next = new_node
            this.end_node = new_node
        }
        else {
            let new_node = new Node(null, value, null)
            this.set_root(new_node)
        }
    }

    delete_node(node){
        if(node === this.root) {
            let next = node.next
            if(next) {
                next.prev = null
                this.root = next
            }
            else {
                this.set_root(null)
            }
            node = null;
            return null
        }
        else if (node === this.end_node){
            let prev = node.prev
            prev.next = null
            this.end_node = prev
            node = null;
            return this.end_node
        }
        else {
            let prev = node.prev
            let next = node.next
            prev.next = next
            next.prev = prev
            node = null;
            return prev
        }
    }
}


class Basic_stuff {
    constructor() {
        this.max_books_slot = 10
        this.active_slots = 0
        this.available_slots   = new Array(this.max_books_slot)
        for (let i=0; i<this.max_books_slot; i++){
            this.available_slots[i] = 0
        }
        this.book_slot_timer_progress = new Array(this.max_books_slot)
        this.list = new List()
        this.actual_list_node = null
    }
}

function add_book_slot(){

    if(organiser.active_slots >= organiser.max_books_slot) return

    let slots_number = parseInt(document.getElementById("slot_text_idx2").innerHTML)
    document.getElementById("slot_text_idx2").innerHTML = slots_number + 1


    let ACTUALLY_ADDING = -1

    for(let i=0; i<organiser.max_books_slot; i++){
        if(organiser.available_slots[i] === 0) {
            organiser.available_slots[i] = 1
            ACTUALLY_ADDING = i
            break
        }
    }


    if(ACTUALLY_ADDING <= -1) return

    organiser.list.add_node(ACTUALLY_ADDING)


    let container_book = document.createElement('div')
        container_book.id = "container_book" + ACTUALLY_ADDING
        container_book.className = "container_book_class"
    let text_isbn = "Wpisz ISBN, aby wyszukać księżkę w globalnej bazie"

    let input_isbn = document.createElement('input')
        input_isbn.type = "text"
        input_isbn.id = "input_isbn"+ACTUALLY_ADDING
        input_isbn.placeholder = "podaj ISBN"
        input_isbn.className = "form-control"
        input_isbn.maxlength = 13
        input_isbn.minLength = 13

    let button_search = document.createElement('button')
        button_search.id = "button_search" + ACTUALLY_ADDING
        button_search.addEventListener("click", function(){
            search_book_ajax(ACTUALLY_ADDING);
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

    let row = document.createElement("div")
    row.className = "row justify-content-center"

    let col1 = document.createElement("div")
    col1.className = "col-md-6"

    let col2 = document.createElement("div")
    col1.className = "col-md-6"

    container_book.innerHTML = text_isbn
    container_book.appendChild(document.createElement("br"))


    col1.appendChild(input_isbn)
    row.appendChild(col1)

    col2.appendChild(button_search)
    col2.appendChild(button_release)
    row.appendChild(col2)
    container_book.appendChild(row)
    document.getElementById("main_article").appendChild(container_book)
    organiser.active_slots += 1
}

function add_book(search_idx){
    let form_name = "book_form" + search_idx

    let form = document.getElementById(form_name)

    let form_data = new FormData(form)
    form_data.append('csrfmiddlewaretoken', csrfValue)
    form_data.append('search_idx', search_idx)
    form_data.append('adding', 1)

    $.ajax({
        type: 'POST',
        url: $(form_name).attr("action"),
        data: form_data,
        success: function(response) {
            if(response.book_form) {
                let form = document.getElementById("book_form"+search_idx)
                let button_save = document.getElementById("book_button_add"+search_idx)
                while (form.firstChild)
                    form.removeChild(form.firstChild);
                form.remove()
                button_save.remove()
                temporary_book_pass_data(search_idx, response)
          }
          if(response.success){
              let handler = document.getElementById("container_book"+search_idx)
              create_cover_up("success", handler, search_idx)
          }
          else if(!response.success){
              let handler = document.getElementById("container_book"+search_idx)
              create_cover_up("failure", handler, search_idx)
          }
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
        $('#container_book' + search_idx + ' #id_prefix'+ search_idx +'-bought_date').datepicker({
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

    div.appendChild(form)
    div.appendChild(button_add_book)
}


function wait_for_search_result(search_idx){
    let form_data = new FormData()
    form_data.append('csrfmiddlewaretoken', csrfValue)
    form_data.append('search_idx', search_idx)
    form_data.append('mode', 'searching_book_g_library_results')


    $.ajax({
        type: 'POST',
        url: "/add_books",
        data: form_data,
        success: function(response) {
            if(!response.success){
                //document.getElementById("numb"+search_idx).innerText += 10
            }
            else{
                clearInterval(organiser.book_slot_timer_progress[search_idx])
                remove_timer(search_idx)
                document.getElementById("button_release"+search_idx).disabled = false
                temporary_book_pass_data(search_idx, response)
            }
        },
        error: function (error){
            clearInterval(organiser.book_slot_timer_progress[search_idx])
            temporary_book_pass_data(search_idx, response)
            remove_timer(search_idx)
            document.getElementById("button_release"+search_idx).disabled = false
            let handler = document.getElementById("container_book"+search_idx)
            create_cover_up("failure_chromium", handler, search_idx)
        },
        contentType: false,
        processData: false
    });
}


function search_book_ajax(idx){

    let isbn = document.getElementById("input_isbn"+idx).value
    if(isbn.length !== 13) {
        console.log("zły isbn")
        return
    }

    document.getElementById("button_search"+idx).disabled = true

    timer_own(idx)

    organiser.book_slot_timer_progress[idx] = setInterval(wait_for_search_result, 5000, idx)


    let form_data = new FormData()
    form_data.append('csrfmiddlewaretoken', csrfValue)
    form_data.append('search_idx', idx)
    form_data.append('isbn', isbn)
    form_data.append('mode', 'start_searching_book_g_library')

    $.ajax({
      type: 'POST',
      url: "/add_books",
      data: form_data,
      success: function(response) {
          return response
      },
      error: function (error){
          console.log(this.error)
      },
      cache: false,
      contentType: false,
      processData: false,
    });
}

function clean_after_book_slot(search_idx){
    let form = document.getElementById("book_form"+search_idx)
    if(form){
        for (let i = 0; i < form.children.length; i++){
            form.removeChild(form.firstChild);
        }
        form.remove()
    }

    let container = document.getElementById("container_book"+search_idx)
    if(container){
        for (let i = 0; i < container.children.length; i++){
            container.removeChild(container.firstChild);
        }
        container.remove()
    }
    organiser.available_slots[search_idx] = 0
    organiser.active_slots -= 1
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

          clean_after_book_slot(search_idx)

          let slots_number = parseInt(document.getElementById("slot_text_idx2").innerHTML)
          document.getElementById("slot_text_idx2").innerHTML = slots_number - 1

          let node = organiser.list.find(search_idx)
          let prev = organiser.list.delete_node(node)

          if(prev) {
              organiser.actual_list_node = prev
              let slots_number = parseInt(document.getElementById("slot_text_idx1").innerHTML)
              document.getElementById("slot_text_idx1").innerHTML = slots_number - 1
          }
          else {
              document.getElementById("slot_text_idx1").innerHTML = 0
          }

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


