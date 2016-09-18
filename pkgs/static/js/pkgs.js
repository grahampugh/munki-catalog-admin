// Search fields
// Main Search
$(document).ready(function() {
	$('#SearchField').keyup(function(){
		var filter = $(this).val();
		var regExPattern = "gi";
		var regEx = new RegExp(filter, regExPattern);
		$('#listbig a').each(function(){	 
			if (
				$(this).text().search(new RegExp(filter, "i")) < 0 &&
				$(this).data('state').search(regEx) < 0 
				){
					$(this).hide();
				} else {
					$(this).show();
				}		 
		});
	});
	$('#SearchFieldMobile').keyup(function(){
		var filter = $(this).val();
		var regExPattern = "gi";
		var regEx = new RegExp(filter, regExPattern);
		$('#listbig a').each(function(){	 
			if (
				$(this).text().search(new RegExp(filter, "i")) < 0 &&
				$(this).data('state').search(regEx) < 0 
				){
					$(this).hide();
				} else {
					$(this).show();
				}		 
		});
	});

	$('#SearchField').change(function(){
		$('#SearchField').keyup();
	});

	$('#SearchFieldMobile').change(function(){
		$('#SearchFieldMobile').keyup();
	});
});

function toggle(source) {
  checkboxes = document.getElementsByName('items_to_move[]');
  for(var i=0, n=checkboxes.length;i<n;i++) {
    checkboxes[i].checked = source.checked;
  }
}
