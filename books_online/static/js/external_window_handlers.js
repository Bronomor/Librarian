let HANDLE_SHELVE_WINDOW = null
let HANDLE_CATEGORY_WINDOW = null
let interval_shelves_search;


function check_shelve_change(){

    let elem = HANDLE_SHELVE_WINDOW.document.getElementById("something_change").innerText
    if(elem){
        let old_name = HANDLE_SHELVE_WINDOW.document.getElementById("old_shelve_name").innerText
        let new_name = HANDLE_SHELVE_WINDOW.document.getElementById("new_shelve_name").innerText
        if (old_name !== new_name) HANDLE_SHELVE_WINDOW.document.getElementById("something_change").innerText = ''

        //let data_set = $("#id_physical_location_list #id_physical_location_list")
        //console.log(data_set)
        //let childrens = data_set.children
        //console.log(childrens)
        //for(let i=0; i<childrens.length; i++){
        //    if(childrens[i].value === old_name){
        //        if (new_name === '') childrens[i].remove()
        //        else childrens[i].value = new_name
        //    }

        if (new_name === '') {
            console.log($("#id_physical_location_list #id_physical_location_list option[value=new_value]"))
            $("#id_physical_location_list #id_physical_location_list option[value=new_value]").remove();
        }
        else {
            console.log($("#id_physical_location_list #id_physical_location_list option[value=new_value]"))
            $("#id_physical_location_list #id_physical_location_list option[value=new_value]").remove();
            let data_set = $("#id_physical_location_list #id_physical_location_list")
            data_set.add(new Option("",new_name));
        }

    }
}


function func_shelve_window_close(mode, search_idx) {
    if(HANDLE_SHELVE_WINDOW.location.href !== 'about:blank'){
        if (mode === "add"){
            let data = HANDLE_SHELVE_WINDOW.document.getElementById("id_name").value
            let elements = document.getElementsByName("id_physical_location_list")

            for (let j = 0; j < elements.length; j++) {
                let option = "<option value='" + data + "' />";
                elements[j].innerHTML += option;
            }
            let selected_element = document.getElementById("book_form"+search_idx).elements["id_physical_location"];
            selected_element.value = data
            global_Shelves_name.push(data)
        }
        else if (mode === "search"){
            clearInterval(interval_shelves_search)
            let elem = HANDLE_SHELVE_WINDOW.document.getElementById("something_change")
            if (elem){
                let old_value = HANDLE_SHELVE_WINDOW.document.getElementById("old_shelve_name").innerText
                let new_value = HANDLE_SHELVE_WINDOW.document.getElementById("new_shelve_name").innerText

                if (old_value === new_value)
                    $("#book_form"+search_idx + " #id_physical_location").val(new_value)
            }
            elem.innerText = ''
        }
        HANDLE_SHELVE_WINDOW.close()
    }
    else {
        if (mode === "search"){
            interval_shelves_search = setInterval(check_shelve_change, 1000)
            console.log("dsd")
        }
    }
}


function func_category_window_close(mode, search_idx) {
    if(HANDLE_CATEGORY_WINDOW.location.href !== 'about:blank'){
        if (mode === "add") {
            let data = HANDLE_CATEGORY_WINDOW.document.getElementById("id_name").value
            let form_categories = document.getElementById("book_form"+search_idx).elements["id_categories"];
            if(form_categories.value.length > 0)
                form_categories.value += " , " + data
            else
                form_categories.value = data

            global_Shelves_name.push(data)
        }
        if (mode === "search"){

        }
        HANDLE_CATEGORY_WINDOW.close()
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
    HANDLE_CATEGORY_WINDOW = window.open("/search_category", 'search_category', 'height=300,width=400');
    HANDLE_CATEGORY_WINDOW.onunload = function (){func_category_window_close("search", search_idx);}
}