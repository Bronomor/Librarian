
function create_cover_up(mode, handler, idx){

    let form = document.getElementById("book_form"+idx)
    if(form)
        form.hidden = true

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
    else{
        handler.className += " failure_div"
        text.innerHTML = "<br><br>Operacja nie powiodła się. Książki nie zmodyfikowano. Spróbuj ponownie <br>"
    }

    button.onclick = function () {
        handler.className = "results_block_clicked"
        document.getElementById("text_info" + idx).remove()
        document.getElementById("button_info" + idx).remove()
        if (form)
            form.hidden = false
    }

    handler.appendChild(text)
    handler.appendChild(button)
}