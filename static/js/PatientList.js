define(['backbone', 'underscore'], function(){
	var PatientList = {}
	
	PatientList.Patient = Backbone.Model.extend({
		idAttribute : 'patient_id'
	});
	
	PatientList.PatientCollection = Backbone.Collection.extend({
		model : PatientList.Patient,
		url : '/risk_patients'
	});
	
	PatientList.PatientItem = Backbone.View.extend({
		tagName : 'li',
		events : '',
		initialize: function() {
	      this.listenTo(this.model, 'change', this.render);
	      
	  
	      
	    },
	    template : _.template($('#patient_template').html()),
		render : function()
		{
			this.$el.prop('id', this.model.get('patient_id'));
			this.$el.append(this.template(this.model.attributes));
			this.$el.addClass(this.model.get('type'))
			this.$el.addClass('patient')
			return this;
		}
	});
	
	
	PatientList.PatientList = Backbone.View.extend({
		events : {
			'click li' : 'selectPatient'
		},
		addOne : function(item)
		{
			var pat_itm = new PatientList.PatientItem({model : item });
			this.$('ul').append(pat_itm.render().el);
		},
		addAll : function()
		{
			this.collection.each(this.addOne, this)
		},
		initialize: function()
		{
			this.listenTo(this.collection, 'add', this.addOne);
			this.listenTo(this.collection, 'reset', this.addAll);
			this.listenTo(this.collection, 'all', this.render);
			this.listenTo(this.collection, 'request', this.setLoading)
			this.listenTo(this.collection, 'sync', this.unsetLoading)
		},
		render : function(){
			this.$el.empty();
			
			this.$el.addClass('patient_viewer');
			this.$el.append('<h2>Positive and Risk Patients</h2><ul ></ul>');
			this.list = $('ul', this.$el);
			
			if( this.collection.length == 0 && !this.$el.hasClass('loading') )
			{
				this.$el.append('<i>No patients<i>');
			}
			else
			{
				this.addAll();
			}
			return this;
		},
		setLoading : function()
		{
			this.$el.addClass('loading');
		},
		unsetLoading : function()
		{
			this.$el.removeClass('loading');
		},
		selectPatient : function(evt)
		{
			$('.patient', this.$el).removeClass('selected');
			var tgt = $(evt.target);
			if (! tgt.hasClass('patient'))
			{
				tgt = tgt.parents('.patient')
			}
			tgt.addClass('selected');
		}
	});
	

	return PatientList;
});
