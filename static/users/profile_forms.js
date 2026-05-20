function removeEl(elId) {
    let el = document.getElementById(elId);
    el.remove();
}

function hide(elementId) {
    let element = document.getElementById(elementId);
    element.hidden = true;
}

function show(elementId) {
    let element = document.getElementById(elementId);
    element.hidden = false;
}


function addAdvisor(el) {
    
    let formEl = document.getElementById(el.dataset.form_id);
    let vals = htmx.values(formEl);

    let prom = htmx.ajax('POST', el.dataset.url, { target: el.dataset.target, swap: el.dataset.swap, values: vals, source: formEl.id });
    prom.then(function () {
        let parentContainer = document.getElementById("advisor-target");
        instanceId = parentContainer.firstElementChild.dataset.instance_id;
        if (instanceId) {
            console.log("istance found!", instanceId);
            let optionEl = document.querySelector("#id_advisor option:checked");
            console.log(optionEl);
            optionEl.value = instanceId;
            optionEl.text = instanceId;
            console.log(optionEl);
        }
    });
}



function checkAuthorsField() {

    let allAuthors = document.getElementsByClassName("author-saved");
    if (allAuthors) {
        let ids = Array.from(allAuthors).map(a => a.dataset.instance_id);
        let selectEl = document.getElementById("id_authors_field");
        selectEl.innerHTML = "";
        
        for (var j = 0; j < ids.length; j++) {
            var opt = document.createElement('option');
            opt.value = ids[j];
            opt.text = ids[j];
            opt.selected = true;
            selectEl.append(opt);
        }
        selectEl.dispatchEvent(new Event('change'));
    
    }
}


function saveAuthor(el) {
    let formEl = document.getElementById(el.dataset.form_id);
    let vals = htmx.values(formEl);

    let prom = htmx.ajax('POST', formEl.dataset.url, { target: formEl.dataset.target, swap: formEl.dataset.swap, values: vals, source: formEl.id});

    prom.then(function () {
        
        setTimeout(function () {
           checkAuthorsField(); 
        }, 100);
        
    });
}

function delAuthor(el) {
    
    let prom = htmx.ajax('GET', el.dataset.url, { target: el.dataset.target, swap: el.dataset.swap });

    prom.then(function () {
        setTimeout(function () {
            checkAuthorsField();
        }, 100);

    });
}




