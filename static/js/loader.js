(function(){
	require.config({
		baseUrl: '/static/js/',
		paths :{
			jquery : 'http://code.jquery.com/jquery.min'
		},
		shim : {
			'jquery' : {
				exports : '$'
			},
			'backbone' : {
				exports : 'Backbone',
				deps : ['jquery', 'underscore']
			},
			'underscore' : {
				exports : '_',
				deps : ['jquery']
			}
		}
	});
	
	require(['PatientList'], function(PatientList){
		var pcol = new PatientList.PatientCollection()
		
		
		var plist = new PatientList.PatientList({ el : '#patient_list', collection : pcol});
		plist.render();
		
		pcol.fetch({ data : { at_date : '2011-01-01 00:00:00' }});
		
		
	});
})();