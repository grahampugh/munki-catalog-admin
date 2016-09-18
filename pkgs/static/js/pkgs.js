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
  checkboxes = document.getElementsByName('foo');
  for each(var checkbox in checkboxes)
    checkbox.checked = source.checked;
}