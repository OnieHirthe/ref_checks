
function changeVisibility(element) {
    if (typeof element === "string") {
        element = document.getElementById(element);
    }
    if (element) {
        element.hidden = !(element.hidden);
    } else {
        console.log("In changeVisibility: element not found");
    }
}


function delElement(elId) {
    let el = document.getElementById(elId);
    el.remove();
}


function setFilter(el) {
    let linkEl = document.getElementById("filter-link");
    let csvEl = document.getElementById("csv-link");
    let jsonEl = document.getElementById("json-link");

    let filterNames = ['status', 'section_id', 'citizenship', 'online', 'reports']

    function setDataAttrTarget(attrName) {
        if (el.name.includes(attrName)) {
            linkEl.setAttribute(`data-${ attrName }`, el.value);
            csvEl.setAttribute(`data-${ attrName }`, el.value);
            if ( jsonEl ) { jsonEl.setAttribute(`data-${ attrName }`, el.value); }
        }
    }
    
    filterNames.forEach((attrName) => setDataAttrTarget(attrName)); 

    linkEl.href =` ${linkEl.dataset.href}?`
    csvEl.href =` ${csvEl.dataset.href}?`
    if ( jsonEl ) { jsonEl.href =` ${jsonEl.dataset.href}?` }

    function linkAppend(attrName) {
        if (linkEl.getAttribute(`data-${ attrName }`)) {
            attrValue = linkEl.getAttribute(`data-${ attrName }`)
            linkEl.href += `${ attrName }=${ attrValue }&` 
            csvEl.href += `${ attrName }=${ attrValue }&` 
            if ( jsonEl ) { jsonEl.href += `${ attrName }=${ attrValue }&` }
        }
    }

    filterNames.forEach((attrName) => linkAppend(attrName));
}

function selectYearList(el) {
    console.log(el.value);
    let targetEl = document.getElementById(el.dataset.target);
    targetEl.href = targetEl.dataset.base_url + el.value;
    console.log(targetEl.href);
}

