

let curatorBtn = document.getElementById("curator-btn");
if (curatorBtn) {
    curatorBtn.onclick = function () {
        showById('main-section');
        hideById('admin-options');
        showById('upvote-options');
        loadUpvote();
    }
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
            alert(data['error']);
        } else {
            loadUpvotesTable(data['upvotes']);
        }
    });
}

document.getElementById('sendNewUpvote').onclick = function () {
    hideById('sendNewUpvote');
    showById('sendingUpvote', 1);

    console.log(localStorage.getItem('username'));
    $.ajax({
        url: "/upvote",
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

function loadUpvotesTable(data) {
    document.getElementById("curator-table").style.display = "block";
    console.log("Construye tabla de Upvote");
    if ($.fn.DataTable.isDataTable('#table-upvote')) {
        $('#table-upvote').DataTable().destroy();
    }

    setContentById('upvotesTableBody', '');
    $.each(data, function (index, value) {
        let newrow = document.createElement('tr');
        newrow.setAttribute('id', 'upvote' + value.id);

        //Date
        let newcolumn = document.createElement('td');
        let newcontent = document.createTextNode(value.created);
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // User
        newcolumn = document.createElement('td');
        let newlink = document.createElement('a');
        newlink.setAttribute('href', 'https://peakd.com/@' + value.user);
        newlink.setAttribute('target', '_blank');
        newcontent = document.createTextNode(value.user);
        newlink.appendChild(newcontent);
        newcolumn.appendChild(newlink);
        newrow.appendChild(newcolumn);

        // Title
        newcolumn = document.createElement('td');
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
        newcontent = document.createTextNode(value.payout);
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
            newimage = document.createElement('span');
            newimage.setAttribute('class', 'material-icons');
            newcontent = document.createTextNode('delete');
            newimage.setAttribute('height', '24px');
            newimage.appendChild(newcontent);
            newlink.appendChild(newimage);
            newcolumn.appendChild(newlink);
            console.log(newcolumn);
        }
        newrow.appendChild(newcolumn);

        document.getElementById('upvotesTableBody').appendChild(newrow);

    });

    $('#table-upvote').DataTable({
        'order': [],
        'lengthChange': false
    });
}


function json_to_array(json_data) {
    console.log(json_data);

    let result = [];

    for (let i = 0; i < json_data.length; i++) {
        result[i] = (Object.values(json_data[i]))
    }
    return result;
}