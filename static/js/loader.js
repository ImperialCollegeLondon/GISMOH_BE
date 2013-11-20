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
	
	require(['PatientList','Linker', 'Replay', 'strftime', 'Timeline', 'models'], function(PatientList, Linker, Replay, strftime, Timeline, Models){
		
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
				timeline.setDateTime(dt);
			}
		});
		
		var currentDate = new Date('2011-02-18T01:00:00');
		
		var patientCollection = new Models.PatientCollection();
		var isolateCollection = new Models.BioLinkCollection();
		var overlapCollection = new Models.LocationLinkCollection();
		
		var controller = new Controller();
		var linker = new Linker.Graph({el : '#linker', router : controller, bio_collection : isolateCollection, loc_collection: overlapCollection });
		var plist = new PatientList.PatientList({ el : '#patient_list', router : controller, collection: patientCollection});
		var replay = new Replay({ controller : controller });
		var timeline = new Timeline({ el: '#timeline', controller : controller, collection : overlapCollection });

		controller.setDateTime(currentDate);
		
		Backbone.history.start();
	});
})();
