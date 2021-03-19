function hideById(id) {
    document.getElementById(id).style.display = "none";
}

function showById(id) {
    document.getElementById(id).style.display = "block";
}

function showById(id, inline) {
    if (inline === undefined) {
        document.getElementById(id).style.display = 'block';
    } else {
        document.getElementById(id).style.display = 'inline-block';
    }
}

function setValueById(id, value) {
    document.getElementById(id).value = value;
}

function setContentById(id, content) {
    document.getElementById(id).innerHTML = content;
}

function getValueById(id) {
    return document.getElementById(id).value;
}