let adminBtn = document.getElementById("admin-btn");
if (adminBtn) {
    adminBtn.onclick = function () {
        hideById('upvote');
        hideById('downvote');
        showById('admin');
        loadAdmin();
    }
}

$(document).ready(function () {
    let done_btn = `<img src='static/img/icons/done.svg' height='24px'></img>`;
    let clear_btn = `<img src='static/img/icons/clear.svg' height='24px'></img>`;
    let delete_btn = `<img class= "button-delete" src='static/img/icons/trash.svg' height='24px'></img>`;

    $('#usersTable').DataTable({
        "ajax": {
            "url": "/profile_data",
            "dataType": "json",
            "dataSrc": "",
            "contentType": "application/json"
        },
        "columns": [

            { "data": "id", "visible": false },
            { "data": "account" },

            {
                "data": function (data) {
                    if (data.curator == true) {
                        return done_btn;
                    } else
                        return clear_btn;
                },
                "className": "curator-class"
            },
            {
                "data": function (data) {
                    if (data.delegator == true) {
                        return done_btn;
                    } else
                        return clear_btn;
                },
                "className": "delegator-class"
            },
            {
                "data": function (data) {
                    if (data.admin == true) {
                        return done_btn;
                    } else
                        return clear_btn;
                },
                "className": "admin-class"
            },
            {
                "data": function (data) {
                    return (data.created).replace("T", " ");
                }
            },
            { "defaultContent": delete_btn },
        ]
    });

    let tble = $('#usersTable').DataTable();

    $('#usersTable tbody').on("click", ".button-delete", function () {

        let tr = $(this).closest("tr");
        let rowindex = tr.index();
        // Get the value of the id in the hidden column (col: 0)
        id_account = tble.cells({ row: rowindex, column: 0 }).data()[0];
        account = tble.cells({ row: rowindex, column: 1 }).data()[0];

        let answer = confirm("Está seguro de eliminar el usuario: " + account);

        if (answer) {
            //Delete account from server side
            $.ajax({
                url: '/delete_account',
                type: 'POST',
                dataType: "json",
                contentType: "application/json",
                data: JSON.stringify({
                    id: id_account
                }),
                success: function () {
                    tble.row(tr.parents('tr')).remove().draw();
                    tble.ajax.reload();
                }
            });
        }
    });

    $('#usersTable tbody').on("click", ".curator-class", function () {
        let tr = $(this).closest("tr");
        let rowindex = tr.index();
        // Get the value of the id in the hidden column (col: 0)
        id_curator = tble.cells({ row: rowindex, column: 0 }).data()[0];

        //Update account status
        $.ajax({
            url: '/update_account_status',
            type: 'POST',
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                id: id_curator,
                option: 1
            }),
            success: function () {
                tble.ajax.reload();
            }
        });

    });

    $('#usersTable tbody').on("click", ".delegator-class", function () {
        let tr = $(this).closest("tr");
        let rowindex = tr.index();
        // Get the value of the id in the hidden column (col: 0)
        id_delegator = tble.cells({ row: rowindex, column: 0 }).data()[0];

        //Update account status
        $.ajax({
            url: '/update_account_status',
            type: 'POST',
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                id: id_delegator,
                option: 2
            }),
            success: function () {
                tble.ajax.reload();
            }
        });

    });

    $('#usersTable tbody').on("click", ".admin-class", function () {
        let tr = $(this).closest("tr");
        let rowindex = tr.index();
        // Get the value of the id in the hidden column (col: 0)
        id_admin = tble.cells({ row: rowindex, column: 0 }).data()[0];

        //Update account status
        $.ajax({
            url: '/update_account_status',
            type: 'POST',
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                id: id_admin,
                option: 3
            }),
            success: function () {
                tble.ajax.reload();
            }
        });
    });

});

function loadAdmin() {
    username = localStorage.getItem('username');
    userhash = localStorage.getItem('userhash');

    $.ajax({
        url: "/admin",
        data: {
            username: username,
            userhash: userhash
        },
        type: "POST"
    }).fail(function () {
        alert('Error loading admin data');
    }).done(function (data) {
        if (data['error']) {
            alert(data['error']);
        } else {
            // loadAdminUserTable(data['users']);
            loadAdminUpvotesTable(data['upvotes']);
            // loadAdminBlacklistTable(data['blacklist']);
            loadAdminDownvotesTable(data['downvotes']);
        }
    });
}

function loadAdminUpvotesTable(upvotes) {
    if ($.fn.DataTable.isDataTable('#adminUpvotesTable')) {
        $('#adminUpvotesTable').DataTable().destroy();
    }

    setContentById('adminUpvotesTableBody', '');
    $.each(upvotes, function (index, value) {
        let newRow = document.createElement('tr');
        newRow.setAttribute('id', 'adminUpvote' + value.id);

        //Created
        let newColumn = document.createElement('td');
        let newContent = document.createTextNode((value.created).replace("T", " "));
        newColumn.setAttribute('class', 'align-field');
        newColumn.appendChild(newContent);
        newRow.appendChild(newColumn);

        //Account
        newColumn = document.createElement('td');
        newContent = document.createTextNode(value.account);
        newColumn.setAttribute('class', 'align-field');
        newColumn.appendChild(newContent);
        newRow.appendChild(newColumn);

        // User
        newColumn = document.createElement('td');
        let newLink = document.createElement('a');
        newLink.setAttribute('href', 'https://peakd.com/@' + value.user);
        newLink.setAttribute('target', '_blank');
        newContent = document.createTextNode(value.user);
        newLink.appendChild(newContent);
        newColumn.appendChild(newLink);
        newColumn.setAttribute('class', 'align-field');
        newRow.appendChild(newColumn);

        //Title
        newColumn = document.createElement('td');
        newLink = document.createElement('a');
        newLink.setAttribute('href', 'https://peakd.com' + value.link);
        newLink.setAttribute('target', '_blank');
        if (value.title == '') {
            value.title = 'None';
        }
        newContent = document.createTextNode(value.title);
        newColumn.setAttribute('class', 'align-field');
        newLink.appendChild(newContent);
        newColumn.appendChild(newLink);
        newRow.appendChild(newColumn);

        //Type
        newColumn = document.createElement('td');
        let type = 'comment';
        if (value.type == 1)
            type = 'post';
        newContent = document.createTextNode(type);
        newColumn.appendChild(newContent);
        newRow.appendChild(newColumn);

        //Status
        newColumn = document.createElement('td');
        newContent = document.createTextNode(value.status);
        newColumn.appendChild(newContent);
        newRow.appendChild(newColumn);

        //Delete
        newColumn = document.createElement('td');
        if (value.status === 'in queue') {
            newLink = document.createElement('a');
            newLink.setAttribute('href', '#');
            newLink.setAttribute('id', 'adminUpvoteDelete' + value.id);
            let newIcon = document.createElement('img');
            newIcon.setAttribute('src', 'static/img/icons/trash.svg');
            newIcon.setAttribute('height', '24px');
            newLink.appendChild(newIcon);
            newColumn.appendChild(newLink);
        }
        newRow.appendChild(newColumn);

        document.getElementById('adminUpvotesTableBody').appendChild(newRow);

        if (value.status === 'in queue') {
            document.getElementById('adminUpvoteDelete' + value.id).onclick = function () {
                if (confirm('Delete upvote for ' + value.title + '?') == true) {
                    adminDeleteUpvote(value.id);
                }
            }
        }


    });
    $('#adminUpvotesTable').DataTable({
        'order': [],
        'lengthChange': false,
        "ordering": false
    });

}

function adminDeleteUpvote(id) {
    $.ajax({
        url: "/admin",
        data: {
            username: localStorage.getItem('username'),
            userhash: localStorage.getItem('userhash'),
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
        loadAdmin();
    });
}

function loadAdminDownvotesTable(downvotes) {
    if ($.fn.DataTable.isDataTable('#adminDownvotesTable')) {
        $('#adminDownvotesTable').DataTable().destroy();
    }
    setContentById('adminDownvotesTableBody', '');
    $.each(downvotes, function (index, value) {
        let newrow = document.createElement('tr');
        newrow.setAttribute('id', 'admindownvote' + value.id);

        // Created
        let newcolumn = document.createElement('td');
        let newcontent = document.createTextNode(value.created);
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // Account
        newcolumn = document.createElement('td');
        newcontent = document.createTextNode(value.account);
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // Reason
        newcolumn = document.createElement('td');
        newcontent = document.createTextNode(value.reason);
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

        // Type
        newcolumn = document.createElement('td');
        let type = 'comment'
        if (value.type == 1) {
            type = 'post';
        }
        newcontent = document.createTextNode(type);
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // Limit
        newcolumn = document.createElement('td');
        newcontent = document.createTextNode(value.maxi + ' HBD');
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // Status
        newcolumn = document.createElement('td');
        newcontent = document.createTextNode(value.status);
        newcolumn.appendChild(newcontent);
        newrow.appendChild(newcolumn);

        // Delete
        newcolumn = document.createElement('td');
        if (value.status == 'wait') {
            newlink = document.createElement('a');
            newlink.setAttribute('href', '#');
            newlink.setAttribute('id', 'adminDeleteDownvote' + value.id);
            newimage = document.createElement('img');
            newimage.setAttribute('src', 'static/img/icons/trash.svg');
            newimage.setAttribute('height', '24px');
            newlink.appendChild(newimage);
            newcolumn.appendChild(newlink);
        }
        newrow.appendChild(newcolumn);

        document.getElementById('adminDownvotesTableBody').appendChild(newrow);

        if (value.status == 'wait') {
            document.getElementById("adminDeleteDownvote" + value.id).onclick = function () {
                if (confirm('Delete downvote for ' + value.title + '?') == true) {
                    adminDeleteDownvote(value.id);
                }
            }
        }
    });
    $('#adminDownvotesTable').DataTable({
        'order': [],
        'lengthChange': false,
        "ordering": false
    });
}

function adminDeleteDownvote(id) {
    $.ajax({
        url: "/admin",
        data: {
            username: username,
            userhash: userhash,
            deletedownvote: id
        },
        type: "POST"
    }).fail(function () {
        alert('Failed deleting downvote');
        loadAdmin();
    }).done(function (data) {
        if (data['error']) {
            alert(data['error']);
        }
        loadAdmin();
    });
}