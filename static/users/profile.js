
function goTo(element) {
    let targetEl = document.getElementById(element.dataset.go);
    targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });

    let coll = document.getElementsByClassName('po-js');

    Array.from(coll).forEach(a => a.classList.remove("profile-option-chosen"));

    element.classList.add('profile-option-chosen');
}

function dropdownVisibility(dropdownId) {
    let dropdownEl = document.getElementById(dropdownId);
    dropdownEl.hidden = !(dropdownEl.hidden);
}

function submitForm(formId) {
    let formEl = document.getElementById(formId);
    formEl.submit();
}


function changeVisibility(element) {

	console.log("in change visibility ", element);

	if (typeof element === "string") {

		element = document.getElementById(element);
	}
	if (element) {
		element.hidden = !(element.hidden);
	} else {
		console.log("In changeVisibility: element not found");
	}
}


function clickOff(elementId) {
    if ( event.target.id === elementId ) {
        hide(elementId);
    }
}

function saveDataAnd(el) {
    let formEl = document.getElementById(el.dataset.form_id);
    let vals = htmx.values(formEl);

    let prom = htmx.ajax('POST', formEl.dataset.url, { target: formEl.dataset.target, swap: formEl.dataset.swap, values: vals, source: formEl.id});

    prom.then(function () {
        htmx.ajax('GET', el.dataset.then_url, { target: '#participation-form-target', swap: 'innerHTML', source: '#participation-form-target'});
    });
}


function registerAnd(el) {

    let formEl = document.getElementById(el.dataset.form_id);
    let vals = htmx.values(formEl);

    let prom = htmx.ajax('POST', formEl.dataset.url, { target: formEl.dataset.target, swap: formEl.dataset.swap, values: vals, source: formEl.id});

    prom.then(function () {
        htmx.ajax('GET', el.dataset.then_url, { target: '#reports-target', swap: 'innerHTML', source: '#reports-target'});
        show("reports");
        show("profile-nav-reports");
	});
}

function unregisterAnd(el) {
    
    let prom = htmx.ajax('GET', el.dataset.url, { target: el.dataset.target, swap: el.dataset.swap, source: el.dataset.target});

    prom.then(function () {
        hide("reports");
        hide("profile-nav-reports");
    });
}



function checkParent(elId, parentId) {
    console.log("in ancestor", elId, parentId);

    let el = document.getElementById(elId);
    console.log(el);
    let ancestor = el.closest(parentId);
    console.log(ancestor);

    if (ancestor !== null) {
        console.log("FOUND ancestor!");
        hide(elId);
    }
}

