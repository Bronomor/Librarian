let HANDLE_SHELVE_WINDOW = null
let HANDLE_CATEGORY_WINDOW = null
let interval_shelves_search;
let interval_category_search;


function check_shelve_change(search_idx){
    if(HANDLE_SHELVE_WINDOW.document.getElementById("something_change").innerText.length > 0) {
        let old_name = HANDLE_SHELVE_WINDOW.document.getElementById("old_shelve_name").innerText
        let new_name = HANDLE_SHELVE_WINDOW.document.getElementById("new_shelve_name").innerText
        if (old_name !== new_name) HANDLE_SHELVE_WINDOW.document.getElementById("something_change").innerText = ''

        let data_set = document.getElementById("id_localization_list")
        let childrens = data_set.children
        for (let i = 0; i < childrens.length; i++) {
            if (childrens[i].value === old_name) {
                if (new_name === '') {
                    if ($("#book_form"+search_idx + " #id_prefix" + search_idx + "-physical_location").val() == old_name){
                        $("#book_form"+search_idx + " #id_prefix" + search_idx + "-physical_location").val('')
                    }
                    childrens[i].remove()

                }
                else {
                    if ($("#book_form"+search_idx + " #id_prefix" + search_idx + "-physical_location").val() == old_name){
                        $("#book_form"+search_idx + " #id_prefix" + search_idx + "-physical_location").val(new_name)
                    }
                    childrens[i].value = new_name
                }
            }
        }
    }
}


function check_category_change(search_idx){
    if(HANDLE_CATEGORY_WINDOW.document.getElementById("something_change").innerText === "1") {
        let old_name = HANDLE_CATEGORY_WINDOW.document.getElementById("old_shelve_name").innerText
        let new_name = HANDLE_CATEGORY_WINDOW.document.getElementById("new_shelve_name").innerText
        if (old_name !== new_name) HANDLE_CATEGORY_WINDOW.document.getElementById("something_change").innerText = ''

        let data_set = document.getElementById("id_category_list")
        let childrens = data_set.children
        for (let i = 0; i < childrens.length; i++) {
            if (childrens[i].value === old_name) {
                if (new_name === '') {
                    childrens[i].remove()
                }
                else childrens[i].value = new_name
            }
        }
    }
    else if(HANDLE_CATEGORY_WINDOW.document.getElementById("something_change").innerText === "4"){
        let old_name = HANDLE_CATEGORY_WINDOW.document.getElementById("old_shelve_name").innerText

        let categories_elem = document.getElementById("id_prefix"+search_idx+"-categories")
        if(categories_elem.innerHTML.length)
            categories_elem.innerHTML +=  " , " + old_name
        else
            categories_elem.innerHTML = old_name
    }
    else if(HANDLE_CATEGORY_WINDOW.document.getElementById("something_change").innerText === "3"){
        let old_name = HANDLE_CATEGORY_WINDOW.document.getElementById("old_shelve_name").innerText
        let text_content = document.getElementById("id_prefix"+search_idx+"-categories")

        let text_content_string = text_content.innerHTML
        let word_idx = text_content_string.search(old_name)

        let from_comma = word_idx;
        while(!(text_content_string[from_comma] === ',' || text_content_string[from_comma] === '.') && from_comma > 0)
            from_comma -= 1

        let to_comma = word_idx;
        let text_length = text_content_string.length

        while(!(text_content_string[to_comma] === ',' || text_content_string[to_comma] === '.') && to_comma < text_length)
            to_comma += 1

        text_content.innerHTML = text_content_string.replace(text_content_string.substr(from_comma, to_comma-from_comma), ' ')
    }
    HANDLE_CATEGORY_WINDOW.document.getElementById("something_change").innerText = ""
}


function func_shelve_window_close(mode, search_idx) {
    if(HANDLE_SHELVE_WINDOW.location.href !== 'about:blank'){
        if (mode === "add"){
            let data = HANDLE_SHELVE_WINDOW.document.getElementById("id_name").value
            if(data) {
                let elements = document.getElementsByName("id_physical_location_list")

                for (let j = 0; j < elements.length; j++) {
                    let option = "<option value='" + data + "' />";
                    elements[j].innerHTML += option;
                }
                let selected_element = document.getElementById("book_form" + search_idx).elements["id_prefix" + search_idx + "-physical_location"];
                selected_element.value = data

                let list = document.getElementById("id_localization_list")
                let option = document.createElement('option')
                option.value = data
                list.appendChild(option);
            }
        }
        else if (mode === "search"){
            clearInterval(interval_shelves_search)
            let elem = HANDLE_SHELVE_WINDOW.document.getElementById("something_change")
            if (elem.innerText.length){
                let old_value = HANDLE_SHELVE_WINDOW.document.getElementById("old_shelve_name").innerText
                let new_value = HANDLE_SHELVE_WINDOW.document.getElementById("new_shelve_name").innerText

                if (old_value === new_value && new_value)
                    $("#book_form"+search_idx + " #id_prefix" + search_idx + "-physical_location").val(new_value)
            }
            elem.innerText = ''
        }
        HANDLE_SHELVE_WINDOW.close()
    }
    else {
        if (mode === "search"){
            interval_shelves_search = setInterval(function(){
                check_shelve_change(search_idx)
            }, 1000)
            console.log("dsd")
        }
    }
}


function func_category_window_close(mode, search_idx) {
    if(HANDLE_CATEGORY_WINDOW.location.href !== 'about:blank'){
        if (mode === "add") {
            let data = HANDLE_CATEGORY_WINDOW.document.getElementById("id_name").value
            if(data) {
                let form_categories = document.getElementById("book_form" + search_idx).elements["id_prefix" + search_idx + "-categories"];

                if (form_categories.value.length > 0)
                    form_categories.value += " , " + data
                else
                    form_categories.value = data

                let list = document.getElementById("id_category_list")
                let option = document.createElement('option')
                option.value = data
                list.appendChild(option);
            }
        }
        else if(mode === "search"){
            clearInterval(interval_category_search)
            let elem = HANDLE_CATEGORY_WINDOW.document.getElementById("something_change")
            if (elem.innerText == "1"){
                let old_value = HANDLE_CATEGORY_WINDOW.document.getElementById("old_shelve_name").innerText
                let new_value = HANDLE_CATEGORY_WINDOW.document.getElementById("new_shelve_name").innerText


                if (old_value === new_value){
                    let form_categories = document.getElementById("book_form"+search_idx).elements["id_prefix" + search_idx + "-categories"];
                    if(form_categories.value.length > 0)
                        form_categories.value += " , " + new_value
                    else
                        form_categories.value = new_value
                }
                elem.innerText = ''
            }
        }
        HANDLE_CATEGORY_WINDOW.close()
    }
    else {
        if (mode === "search"){
            interval_category_search = setInterval(function(){
                check_category_change(search_idx)
            }, 1000)
            console.log("dsd")
        }
    }

}


function func_search_loc(search_idx){
    HANDLE_SHELVE_WINDOW = window.open("/search_shelve", 'search_shelve', 'height=800,width=900');
    HANDLE_SHELVE_WINDOW.onunload = function (){ func_shelve_window_close("search", search_idx);}
}

function func_add_loc(search_idx){
    HANDLE_SHELVE_WINDOW = window.open("/add_shelve", 'add_shelves', 'height=500,width=900');
    HANDLE_SHELVE_WINDOW.onunload = function (){ func_shelve_window_close("add", search_idx);}
}

function func_add_cat(search_idx){
    HANDLE_CATEGORY_WINDOW = window.open("/add_category", 'add_category', 'height=300,width=400');
    HANDLE_CATEGORY_WINDOW.onunload = function (){ func_category_window_close("add", search_idx);}
}

function func_search_cat(search_idx){
    HANDLE_CATEGORY_WINDOW = window.open("/search_category", 'search_category', 'height=800,width=600');
    HANDLE_CATEGORY_WINDOW.onunload = function (){func_category_window_close("search", search_idx);}
}