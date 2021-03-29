

let curatorBtn = document.getElementById("curator-btn");
if (curatorBtn) {
    curatorBtn.onclick = function () {
        showById('upvote');
        hideById('admin');
        // showById('upvote-options');
        loadUpvote();
    }
}

document.getElementById('upvoteForm').onsubmit = function () {
    return false;
}

function loadUpvote() {
    $.ajax({
        url: "/upvote",
        data: {
            username: localStorage.getItem('username')
        },
        type: "POST"
    }).fail(function () {
        alert('Error loading upvote data');
    }).done(function (data) {
        if (data['error']) {
            if (document.getElementById('upvote').style.display = 'block')
                alert(data['error']);
        } else {
            loadUpvotesTable(data['upvotes']);
        }
    });
}

document.getElementById('sendNewUpvote').onclick = function () {
    hideById('sendNewUpvote');
    showById('sendingUpvote', 1);

    if (getValueById('newUpvote') === '') {
        alert("A link is needed");
        hideById('sendingUpvote');
        showById('sendNewUpvote', 1);
    } else {
        $.ajax({
            url: "/upvote",
            dataType: "json",
            data: {
                postlink: getValueById('newUpvote'),
                username: localStorage.getItem('username')
            },
            type: "POST"
        }).fail(function () {
            alert('Error submitting post, please try again');
        }).done(function (data) {
            if (data['error']) {
                alert(data['error']);
                setValueById('newUpvote', '');
            } else {
                alert('Post successfully added to upvote queue');
                setValueById('newUpvote', '');
                setContentById('upvotesTableBody', '');
                console.log(data['upvotes']);
                loadUpvotesTable(data['upvotes']);
            }
        }).always(function () {
            hideById('sendingUpvote');
            showById('sendNewUpvote', 1);
        });
    }
}

function loadUpvotesTable(data) {

    if ($.fn.DataTable.isDataTable('#upvotesTable')) {
        $('#upvotesTable').DataTable().destroy();
    }

    setContentById('upvotesTableBody', '');
    $.each(data, function (index, value) {
        let newrow = document.createElement('tr');
        newrow.setAttribute('id', 'upvote' + value.id);

        //Date
        let newcolumn = document.createElement('td');
        let newcontent = document.createTextNode((value.created).replace("T", " "));
        newcolumn.setAttribute('class', 'align-field');
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // User
        newcolumn = document.createElement('td');
        newcolumn.setAttribute('class', 'align-field');
        let newlink = document.createElement('a');
        newlink.setAttribute('href', 'https://peakd.com/@' + value.user);
        newlink.setAttribute('target', '_blank');
        newcontent = document.createTextNode(value.user);
        newlink.appendChild(newcontent);
        newcolumn.appendChild(newlink);
        newrow.appendChild(newcolumn);

        // Title
        newcolumn = document.createElement('td');
        newcolumn.setAttribute('class', 'align-field');
        newlink = document.createElement('a');
        newlink.setAttribute('href', 'https://peakd.com' + value.link);
        newlink.setAttribute('target', '_blank');
        if (value.title == '') {
            value.title = 'None';
        }
        newcontent = document.createTextNode(value.title);
        newlink.appendChild(newcontent);
        newcolumn.appendChild(newlink);
        newrow.appendChild(newcolumn);

        //Type
        newcolumn = document.createElement('td');
        let type = 'comment'
        if (value.type == 1) {
            type = 'post';
        }
        newcontent = document.createTextNode(type);
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);


        // Payout
        newcolumn = document.createElement('td');
        newcolumn.setAttribute('class', 'align-field');
        newcontent = document.createTextNode((value.payout).replace("T", " "));
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // Status
        newcolumn = document.createElement('td');
        newcontent = document.createTextNode(value.status);
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // Reward
        newcolumn = document.createElement('td');
        newcontent = document.createTextNode(value.reward_sp + ' HP');
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // Delete
        newcolumn = document.createElement('td');
        if (value.status == 'in queue') {
            newlink = document.createElement('a');
            newlink.setAttribute('href', '#');
            newlink.setAttribute('id', 'deleteUpvote' + value.id);
            newicon = document.createElement('img');
            newicon.setAttribute('src', 'static/img/icons/trash.svg');
            newicon.setAttribute('height', '24px');
            newlink.appendChild(newicon);
            newcolumn.appendChild(newlink);
            console.log(newcolumn);
        }
        newrow.appendChild(newcolumn);

        document.getElementById('upvotesTableBody').appendChild(newrow);

        if (value.status == 'in queue') {
            document.getElementById("deleteUpvote" + value.id).onclick = function () {
                if (confirm('Delete upvote for ' + value.title + '?') == true) {
                    deleteUpvote(value.id);
                }
            }
        }

    });

    $('#upvotesTable').DataTable({
        'order': [],
        'lengthChange': false,
        "ordering": false
    });
}

function deleteUpvote(id) {
    $.ajax({
        url: "/upvote",
        data: {
            username: localStorage.getItem("username"),
            userhash: localStorage.getItem("userhash"),
            deleteupvote: id
        },
        type: "POST"
    }).fail(function () {
        alert('Failed deleting upvote');
        loadAdmin();
    }).done(function (data) {
        if (data['error']) {
            alert(data['error']);
        }
        loadUpvote();
    });
}