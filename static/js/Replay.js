define(['backbone', 'underscore'], function(){
	var Replay = Backbone.View.extend({
		currentDateTime : null,
		events:{
			'click .handle' : 'toggle',
			'click .decday' : 'decrement_day',
			'click .dechr' : 'decrement_hour',
			'click .incday' : 'increment_day',
			'click .inchr' : 'increment_hour'
			
		},
		initialize : function()
		{
			this.controller = this.options.controller;
			this.render();
		},
		render : function()
		{
			$('body').append(this.$el);
			
			this.$el.addClass('replay');
			this.$el.append('<div class="tray"><div class="curdate"></div><span class="btn decday">-1 Day</span><span class="btn dechr">-1 Hour</span><span class="btn inchr">+1 Hour</span><span class="btn incday">+1 Day</span></div><div class="handle">Set Time</div>')
		},
		open : function()
		{
			console.debug('open');
			this.$el.clearQueue();
			this.$el.animate({'top' : '0px'})
		},
		close : function()
		{
			this.$el.clearQueue();
			this.$el.animate({'top' : '-120px'})
		},
		increment_day : function()
		{
			var d = this.dateTime;
			this.setDateTime(new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1, d.getHours(), d.getMinutes(), d.getSeconds()));
			this.fireUpdate();
		},
		increment_hour: function()
		{
			var d = this.dateTime;
			this.setDateTime(new Date(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours() + 1, d.getMinutes(), d.getSeconds()));
			this.fireUpdate();
		},
		decrement_day : function()
		{
			var d = this.dateTime;
			this.setDateTime(new Date(d.getFullYear(), d.getMonth(), d.getDate() - 1, d.getHours(), d.getMinutes(), d.getSeconds()));
			this.fireUpdate();
		},
		decrement_hour: function()
		{
			var d = this.dateTime;
			this.setDateTime(new Date(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours() - 1, d.getMinutes(), d.getSeconds()));
			this.fireUpdate();
		},
		toggle : function()
		{
			console.debug('toggle')
			if(this.$el.offset().top == -120)
			{
				this.open();
			}
			else
			{
				this.close();
			}
		},
		setDateTime : function(dt)
		{
			this.dateTime = dt;
			$('.curdate', this.$el).text(dt);
		},
		fireUpdate : function()
		{
			this.controller.setDateTime(this.dateTime);
		}
	});

	return Replay;
});