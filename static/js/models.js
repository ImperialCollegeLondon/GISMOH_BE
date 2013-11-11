define(['backbone', 'underscore'], function(){
	var Models = {};
	
	Models.LocationLink = Backbone.Model.extend({
		
	});
	
	Models.BioLink = Backbone.Model.extend({
		
	});
	
	Models.Patient = Backbone.Model.extend({
		idAttribute : 'patient_id'
	});
	
	Models.PatientCollection = Backbone.Collection.extend({
		model : Models.Patient,
		url : '/risk_patients'
	});
	
	Models.LocationLinkCollection = Backbone.Collection.extend({
		model: Models.LocationLink,
		url : '/overlaps'
	});
	
	Models.BioLinkCollection = Backbone.Collection.extend({
		model: Models.BioLink,
		url : '/antibiogram'
	});
	
	return Models;
});