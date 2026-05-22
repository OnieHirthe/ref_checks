
function showPasswords(el) {
    let inpts = document.querySelectorAll('[name*="password"]');
    console.log(inpts);
    Array.from(inpts).forEach((a) => {
        a.type = el.dataset.type;
    });

    let toHide = document.getElementsByClassName(el.dataset.hide);
    let toShow = document.getElementsByClassName(el.dataset.show);

    Array.from(toHide).forEach((a) => { a.hidden = true; });
    Array.from(toShow).forEach((a) => { a.hidden = false; });
}

function goToMain(element) {
    let targetEl = document.getElementById(element.dataset.go);
    console.log(targetEl);
    targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}


// shows and hides full theme section display
function themeDisplay(toggleElement) {
    let themeCont = document.getElementById(toggleElement.dataset.id);

    hide(toggleElement.id);
    show(toggleElement.dataset.other);


    if ( themeCont.classList.contains('theme-container-partial') ) {
        themeCont.classList.remove('theme-container-partial');
    } else {
        themeCont.classList.add('theme-container-partial');
    }
    
}

// shows and hides rule block for article formatting
function ruleBlockDisplay(ruleOption) {
    let ruleBlock = document.getElementById(ruleOption.dataset.id);
    let allBlocks = document.getElementsByClassName('rules-block');
    let allOptions = document.getElementsByClassName('rules-option');

    for (let i = 0; i < allBlocks.length; i++) {
        allBlocks[i].hidden = true;
        allOptions[i].classList.remove('rules-option-selected');
    }

    ruleBlock.hidden = false;
    ruleOption.classList.add('rules-option-selected');
}

function hide(elementId) {
    let element = document.getElementById(elementId);
    element.hidden = true;
}

function clickOff(elementId) {
    if ( event.target.id === elementId ) {
        hide(elementId);
    }
}

function show(elementId) {
    let element = document.getElementById(elementId);
    element.hidden = false;
}

// entrance blocks switch
function showEntrance(element) {
    
    let entranceBlock = document.getElementById(element.dataset.id);
    let allBlocks = document.getElementsByClassName('entrance-block');

    for (let i = 0; i < allBlocks.length; i++) {
        allBlocks[i].hidden = true;
    }
    entranceBlock.hidden = false;

}

function dropdownVisibility(dropdownId) {
    let dropdownEl = document.getElementById(dropdownId);
    dropdownEl.hidden = !(dropdownEl.hidden);
}

function showAnswer(element) {
    let targetEl = document.getElementById(element.dataset.answer);
    let iconEl = document.getElementById(element.dataset.icon);
    if ( targetEl.classList.contains("answer-hidden") ) {
        targetEl.classList.remove("answer-hidden");
        iconEl.classList.add("q-icon-reversed");
    } else {
        targetEl.classList.add("answer-hidden");
        iconEl.classList.remove("q-icon-reversed");
    }
}

function submitForm(formId) {
    let formEl = document.getElementById(formId);
    formEl.submit();
}


