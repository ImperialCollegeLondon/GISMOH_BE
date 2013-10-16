(function(){
	require.config({
		paths :{
			jquery : 'http://code.jquery.com/jquery.min'
		},
		shim : {
			'jquery' : {
				exports : '$'
			}
		}
	});
	
	require(['jquery'], function(){
	
		$.ajax({
			type : 'POST',
			url : '/',
			data: {
				x : 'one',
				y : 'two_2'
			},
			success : function(res)
			{
				console.debug(res)
			}
		});
	});
})();