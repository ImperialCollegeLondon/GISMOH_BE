from interface.Rabbit import Consumer, Producer

from json import dumps, loads

class ObjectSender(object):
	def __init__ (self, connection, object_type):
		queue_name = 'gismoh.objects.%s' % (object_type)
		self.connection = Producer(connection, 'gismoh.objects', queue_name, queue_name)

	def send(self, obj):
		self.message = obj.get_dict()
		self.connection.onReady(self.send_message_when_ready)

	def send_message_when_ready(self):
		self.connection.send(json.dumps(self.message))


class ObjectReciever(object):
	def __init__(self):
		def __init__ (self, connection, object_type=None):
			if type is None:
				queue_name = 'gismoh.objects.all'
				routing_key = 'gismoh.objects.#'
			else:
				queue_name = 'gismoh.objects.%s' % (object_type)
				routing_key = queue_name
			self.connection = Producer(connection, 'gismoh.objects', queue_name, routing_key)

		def send(self, obj):
			self.message = obj.get_dict()
			self.connection.onReady(self.send_message_when_ready)

		def send_message_when_ready(self):
			self.connection.send(json.dumps(self.message))
