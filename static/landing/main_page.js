
function goTo(elementId) {
    console.log("scroll to ", elementId);
    let element = document.getElementById(elementId);

    if (element) {
        console.log("found it!");
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function navGoTo(elementId) {
    changeVisibility('m-nav-shade');
    goTo(elementId);
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


function exceptChangeVisibility(elementId) {
    let element = document.getElementById(elementId);
    console.log(event);

    if ( event.target === element ) {
        changeVisibility(element);
    }

}

function copyContent(elementId) {
    let copiedContent = "";
    let textParts = document.querySelectorAll(`#${elementId} .reg-text`);
    for (let i = 0; i < textParts.length; i++) {
        copiedContent += textParts[i].innerText + '\n';
    }

    navigator.clipboard.writeText(copiedContent);
    let message = document.getElementById('copied-message');
    message.classList.remove('sheer');
    
    setTimeout(function() {
        message.classList.add('sheer');
    }, 1000);

}
