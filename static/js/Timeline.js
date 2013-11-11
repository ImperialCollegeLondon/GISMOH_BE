/*jslint nomen: true*/
/*global define, $, Backbone, _, strftime, Raphael */
/*jslint nomen: false*/
define(['backbone', 'underscore', 'strftime'], function (ig, no, strfdate) {
	"use strict";
	var TimeLine = Backbone.View.extend({
        
		initialize : function () {
			this.router = this.options.controller;
			
			this.$el.addClass('gismoh_plugin');
			
			this.size = [this.$el.width(), Math.max(this.$el.height(), 500)];
			
			this.canvas = new Raphael(this.el, this.size[0], this.size[1]);
			this.$el.prepend('<h2>Timeline of overlapping Patients</h2>');
			
			this.gutter = 100;
			
			this.listenTo(this.collection, 'request', this.setLoading);
			this.listenTo(this.collection, 'sync', this.unsetLoading);
			this.listenTo(this.collection, 'add', this.addOne);
			this.listenTo(this.collection, 'reset', this.addAll);
			
			this.router.on('route:selected', this.selectedPatient, this);
		
			this.patients = {};

			
			var today = new Date(), two_weeks = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 10, today.getHours(), today.getMinutes(), today.getSeconds());
			
			this.setScale(two_weeks, today);
		},
		addOne : function (model) {
			var patient_id = model.get('patient_id').toString(),
                draw_base = false,
                start = new Date(model.get('arrived')),
                end = new Date(model.get('left'));
			
			if (end < this.start_date || start > this.end_date) { return; }
			
			
			
			if (!this.patients[patient_id] && this.patients[patient_id] !== 0) {
				this.addPatient(patient_id);
			}
			
			this.drawEpisode(model);
		},
		addAll : function () {
		
			this.canvas.clear();
			this.patients = {};
			this.patients[this.selected_patient] = 0;
			if (this.selected_patient) { this.drawPatient(this.selected_patient); }
			
			this.collection.each(this.addOne, this);

			this.size[1] = (_.size(this.patients) * 30) + 30
			this.canvas.setSize(this.size[0], this.size[1]);
	
			this.drawScale();
		},
		addPatient : function (patient_id)
		{
			this.patients[patient_id] = _.size(this.patients);
			this.drawPatient(patient_id);
		},
		drawPatient : function (patient_id)
		{
			var h = 30;
			var i = this.patients[patient_id] + 1;
			var band = this.canvas.rect(0, i*h, this.size[0], h);
			band.attr('fill', i%2 ? '#e6e6e6' : '#FFFFFF');
			band.attr('stroke', 'none');
			
			var label = this.canvas.text(5, (i*h) + 18, patient_id);
			label.attr('text-anchor', 'start');
			label.attr('font-size', 15);
		},
		drawEpisode : function (model)
		{
			var i = this.patients[model.get('patient_id')] + 1;
			
			var sx = Math.max(this.gutter, this.getPositionOnScale(new Date(model.get('arrived'))));
			var ex = Math.min(this.size[0], this.getPositionOnScale(new Date(model.get('left'))));
			
			if (ex < 0 ) return;
			
			var rect = this.canvas.rect(Math.max(sx, this.gutter), i * 30, ex - sx, 30);
			rect.attr('stroke', '#0000ff');
			rect.attr('fill', '270-#0088cc-#0044cc');
			
			var txt = this.canvas.text(Math.max(sx + 5, this.gutter + 5), i * 30 + 18, model.get('ward'));
			txt.attr('font-size', 15);
			txt.attr('text-anchor', 'start');
			txt.attr('fill', '#FFFFFF');
			
		},
		drawScale : function ()
		{
			for(var d = new Date(this.start_date.getFullYear(), this.start_date.getMonth(), this.start_date.getDate());
				d <= this.end_date; 
				d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1))
			{
				var x = this.getPositionOnScale(d);
				
				if( x < this.gutter ) continue;
				
				var tick = this.canvas.path('M ' + x + ' 20 L ' + x + ' ' + this.size[1]);
				tick.attr('stroke', '#444');
				
				var label = this.canvas.text(x, 13, strftime('%d/%m/%Y', d));
				label.attr('fill', '#444');
				label.attr('font-size', 15);
			}
			
		},
		setScale : function(from_date, to_date)
		{
			this.start_date = from_date;
			this.end_date = to_date;
			
			this.end_seconds = new Date(to_date.getFullYear(), to_date.getMonth(), to_date.getDate() + 1).getTime();
			this.start_seconds = new Date(from_date.getFullYear(), from_date.getMonth(), from_date.getDate()).getTime();
			this.total_seconds = this.end_seconds - this.start_seconds; 
			this.scalar = (this.size[0] - this.gutter) / this.total_seconds;
		},
		getPositionOnScale : function(d)
		{
			var secs = d.getTime();
			var o_secs = secs - this.start_seconds;
			return (o_secs * this.scalar) + this.gutter;
		},
		selectedPatient : function(patient_id)
		{
			this.patients = {  };
			this.patients[patient_id.toString()] = 0;
			this.selected_patient = patient_id;
			
		},
		setDateTime : function(dt)
		{
			var today = dt;
			var two_weeks = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 10, today.getHours(), today.getMinutes(), today.getSeconds());
			
			this.setScale(two_weeks, today);
			this.addAll();
		},
		setLoading : function()
		{
			this.$el.addClass('loading');
		},
		unsetLoading : function()
		{
			this.$el.removeClass('loading');
		}
	});
	
	return TimeLine;
	
});