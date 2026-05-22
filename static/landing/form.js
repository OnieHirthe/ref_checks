
function alterClass(elementId, className) {
    let element = document.getElementById(elementId);

    if (element.classList.contains(className)) {
        element.classList.remove(className);
    } else {
        element.classList.add(className);
    }
}

function removeClass(elementId, className) {
    let element = document.getElementById(elementId);
    
    if (element.classList.contains(className)) {
        element.classList.remove(className);
    }
    
}

function deleteElement(elementId) {
    let element = document.getElementById(elementId);
    if (element) { element.remove(); }

}

function enableButton(issuer, elementId, className) {
    console.log(issuer.checked);
    let element = document.getElementById(elementId);
    if (issuer.checked && element.classList.contains(className) || (!issuer.checked && !element.classList.contains(className))) { alterClass(elementId, className); }
    
}
