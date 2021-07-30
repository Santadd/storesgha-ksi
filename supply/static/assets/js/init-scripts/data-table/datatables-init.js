(function ($) {
    //    "use strict";


    /*  Data Table
    -------------*/

    $('#bootstrap-data-table').DataTable({
        lengthMenu: [[10, 20, 50, -1], [10, 20, 50, "All"]],
		'responsive': true,
		dom: 'frtipB',
        buttons: [
			{
				extend: 'print',
			}
        ]
    });
	
    $('#bootstrap-data-table-export').DataTable({
        lengthMenu: [[10, 20, 50, -1], [10, 20, 50, "All"]],
		'responsive': true,
		dom: 'frtipB',
        buttons: [
            'print'
        ]
    });

    $('#bootstrap-data-table-export_1').DataTable({ 
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
        buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],
    }).buttons().container();

	$('#row-select').DataTable( {
        initComplete: function () {
				this.api().columns().every( function () {
					var column = this;
					var select = $('<select class="form-control"><option value=""></option></select>')
						.appendTo( $(column.footer()).empty() )
						.on( 'change', function () {
							var val = $.fn.dataTable.util.escapeRegex(
								$(this).val()
							);

							column
								.search( val ? '^'+val+'$' : '', true, false )
								.draw();
						} );

					column.data().unique().sort().each( function ( d, j ) {
						select.append( '<option value="'+d+'">'+d+'</option>' )
					} );
				} );
			}
		} );

})(jQuery);
