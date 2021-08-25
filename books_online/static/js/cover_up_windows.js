
function create_cover_up(mode, handler, idx){

    let form = document.getElementById("book_form"+idx)
    if(form)
        form.hidden = true
    let button_save = document.getElementById("book_button_add"+idx)
        if(button_save)
            button_save.hidden = true

    let text = document.createElement("p")
        text.id = "text_info"+idx
    let button = document.createElement("button")
        button.innerHTML = "OK"
        button.id = "button_info"+idx
        button.className = "btn btn btn-dark btn-lg"

    if(mode === "success") {
        handler.className += " success_div"
        text.innerHTML = "<br><br>Poprawnie zmodyfikowano książkę<br>"
    }
    else if(mode === "failure_chromium") {
        handler.className += " failure_div"
        text.innerHTML = "<br><br>Operacja nie powiodła się. Nie dostępne są sterowniki Google Chronium, przez co książki nie mogą być wyszukiwane w zdalny sposób. Spróbuj zrestartować serwery. Po naciśnieściu OK będzie możliwość ręcznego wprowadzenia danych <br>"
    }
    else{
        handler.className += " failure_div"
        text.innerHTML = "<br><br>Operacja nie powiodła się. Książki nie zmodyfikowano. Spróbuj ponownie <br>"
    }

    button.onclick = function () {
        handler.className = "results_block_clicked card-header"
        document.getElementById("text_info" + idx).remove()
        document.getElementById("button_info" + idx).remove()
        if (form)
            form.hidden = false
        if(button_save)
            button_save.hidden = false
    }

    handler.appendChild(text)
    handler.appendChild(button)
}