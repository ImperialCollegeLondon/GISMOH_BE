(function(){
	require.config({
		baseUrl: '/static/js/',
		paths :{
			jquery : 'http://code.jquery.com/jquery.min',
			raphael : '/static/js/raphael-min'
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
	
	require(['PatientList','Linker', 'Replay', 'strftime', 'Timeline'], function(PatientList, Linker, Replay, strftime, Timeline){
		
		var Controller = Backbone.Router.extend({
			routes : {
				"patient/:id" : "selected"
			},
			selected : function(page){
				
			},
			setDateTime : function(dt)
			{
				plist.setDateTime(dt);
				linker.setDateTime(dt);
				replay.setDateTime(dt, false);
			}
		});
		
		var currentDate = new Date('2011-02-18 01:00:00');
		
		var controller = new Controller();
		var linker = new Linker.Graph({el : '#linker', router : controller});
		var plist = new PatientList.PatientList({ el : '#patient_list', router : controller});
		var replay = new Replay({ controller : controller });

		controller.setDateTime(currentDate);
		
		
		Backbone.history.start();
	});
})();