function timer_own(search_idx){

    div = document.createElement("div")
    div.className = "container"
    div.id = "container"+search_idx

    circular = document.createElement("div")
    circular.className = "circular"
    circular.id = "circular"+search_idx

    inner = document.createElement("div")
    inner.className = "inner"
    inner.id = "inner"+search_idx

    outer = document.createElement("div")
    outer.className = "outer"
    outer.id = "outer"+search_idx

    numb_ = document.createElement("div")
    numb_.className = "numb"
    numb_.innerText = "0%"
    numb_.id = "numb"+search_idx

    circle = document.createElement("div")
    circle.className = "circle"
    circle.id = "circle"+search_idx

    dot = document.createElement("div")
    dot.className = "dot"
    dot.id = "dot"+search_idx

    bar_left = document.createElement("div")
    bar_left.className = "bar left"
    bar_left.id = "bar left"+search_idx

    progress_1 = document.createElement("div")
    progress_1.className = "progress"
    progress_1.id = "progress1"+search_idx

    bar_right = document.createElement("div")
    bar_right.className = "bar right"
    bar_right.id = "bar right"+search_idx

    progress_2 = document.createElement("div")
    progress_2.className = "progress"
    progress_2.id = "progress2"+search_idx

    global_div = document.getElementById("container_book"+search_idx)
        div.appendChild(circular)
            circular.appendChild(inner)
            circular.appendChild(outer)
            circular.appendChild(numb_)
            circular.appendChild(circle)
                circle.appendChild(dot)
                circle.appendChild(bar_left)
                    bar_left.appendChild(progress_1)
                circle.appendChild(bar_right)
                    bar_right.appendChild(progress_2)
    global_div.appendChild(circular)
}

function remove_timer(search_idx){

    let child = document.getElementById("progress2"+search_idx)
    child.parentElement.removeChild(child)

    child = document.getElementById("progress1"+search_idx)
    child.parentElement.removeChild(child)

    child = document.getElementById("bar right"+search_idx)
    child.parentElement.removeChild(child)

    child = document.getElementById("bar left"+search_idx)
    child.parentElement.removeChild(child)

    child = document.getElementById("dot"+search_idx)
    child.parentElement.removeChild(child)

    child = document.getElementById("inner"+search_idx)
    child.parentElement.removeChild(child)

    child = document.getElementById("outer"+search_idx)
    child.parentElement.removeChild(child)

    child = document.getElementById("numb"+search_idx)
    child.parentElement.removeChild(child)

    child = document.getElementById("circle"+search_idx)
    child.parentElement.removeChild(child)

    child = document.getElementById("circular"+search_idx)
    child.parentElement.removeChild(child)

}