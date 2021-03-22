let adminBtn = document.getElementById("admin-btn");
if (adminBtn) {
    adminBtn.onclick = function () {
        showById('main-section');
        hideById('upvote-options');
        showById('admin-options');
    }
}

function pressing_button(tableId) {
    if (document.getElementById(tableId).style.display == "block") {
        document.getElementById(tableId).style.display = "none";
    }
    else {
        document.getElementById(tableId).style.display = "block";
    }

}

$(document).ready(function () {
    console.log("Construyo la tabla");
    let done_btn = "<button class='button-status'><span class='material-icons'>done</span></button>";
    let clear_btn = "<button class='button-status'><span class='material-icons'>clear</span></button>";
    let delete_btn = "<button class='button-delete'><span class='material-icons'>delete</span></button>";


    $('#table').DataTable({
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.10.22/i18n/es_es.json'
        },
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

    let tble = $('#table').DataTable();

    $('#table tbody').on("click", ".button-delete", function () {

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
                    id_admin: id_account
                }),
                success: function () {
                    tble.row(tr.parents('tr')).remove().draw();
                    tble.ajax.reload();
                }
            });
        }
    });

    $('#table tbody').on("click", ".curator-class", function () {
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

    $('#table tbody').on("click", ".delegator-class", function () {
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

    $('#table tbody').on("click", ".admin-class", function () {
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
    /*
        $('#curator-table').DataTable({
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.10.22/i18n/es_es.json'
            },
            "ajax": {
                "url": "/profile_data",
                "dataType": "json",
                "dataSrc": "",
                "contentType": "application/json"
            },
            "columns": [
    
                { "data": "id_curator", "visible": false },
                { "data": "account" },
                { "data": "account" },
                { "data": "account" },
                { "data": "account" },
                { "data": "account" },
                { "data": "undefined" },
                { "data": "aundefined" },
                { "data": "aundefined" },
            ]
        });
    */
});

$(document).ready(function () {
    $('#tableD1').DataTable();
});