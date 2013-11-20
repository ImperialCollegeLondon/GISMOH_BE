define(['backbone', 'underscore', 'strftime'], function(ig, no, strfdate){
	var PatientList = {}

	
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
		selected_id : null,
		events : {
			'click li' : 'selectPatient'
		},
		
		abortRequest : function()
		{
			if (this.req && this.req.readyState > 0 && this.req.readyState < 4) this.req.abort();
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
			this.$el.addClass('gismoh_plugin');
			//this.collection = new PatientList.PatientCollection();
			
			this.router = this.options.router;
			
			this.router.on('route:selected', this.selectedPatient, this);
			
			this.listenTo(this.collection, 'add', this.addOne);
			this.listenTo(this.collection, 'reset', this.addAll);
			this.listenTo(this.collection, 'all', this.render);
			this.listenTo(this.collection, 'request', this.setLoading);
			this.listenTo(this.collection, 'sync', this.unsetLoading);
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
			
			if( this.selected_id )
			{
				this.selectedPatient(this.selected_id)
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
			this.selected_id = tgt.prop('id');
			this.router.navigate('patient/' + tgt.prop('id'), { trigger : true, replace:true });
		},
		selectedPatient: function(id)
		{
			this.selected_id = id;
			$('.patient', this.$el).removeClass('selected');
			$('#' + id, this.$el).addClass('selected');
		},
		setDateTime : function(dt)
		{
			this.abortRequest();
			this.req = this.collection.fetch({ data : { 
					at_date : dt.strftime('%Y-%m-%d %H:%M:%S')
				}
			});
		},
		router : null
	});
	

	return PatientList;
});
