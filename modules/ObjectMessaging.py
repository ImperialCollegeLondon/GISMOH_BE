from interfaces.Rabbit import Consumer, Producer
from store.Store import GISMOH_encoder, GISMOH_object_hook

from json import dumps, loads

class ObjectSender(object):
	def __init__ (self, connection):
		self.onReady = None
		self.is_ready = False

		self.routing_key_base = 'gismoh.objects.%s'
		queue_name = self.routing_key_base % 'all'
		self.connection = connection.getProducer('objects')
		self.connection.addOnReady(self.ready)

	def send(self, obj):
		message = ObjectHelper.pack(obj)
		self.connection.sendMessage(message, None, self.routing_key_base % type(obj).__name__)

	def addOnReady(self, callback):
		if self.is_ready:
			callback()

		self.onReady = callback

	def ready(self):
		if self.onReady is not None:
			self.onReady()

		self.is_ready = True

class ObjectReciever(object):
	def __init__ (self, connection, object_type, message_callback):
		if object_type is None:
			queue_name = 'objects.all'
			routing_key = 'gismoh.objects.#'
		else:
			queue_name = 'objects.%s' % (object_type)
			routing_key = queue_name

		self.consumer = connection.getConsumer('objects', queue_name, routing_key, True)
		self.consumer.addMessageHandler(self.messageRecieved)
		self.message_callback = message_callback

	def messageRecieved(self, message_id, app_id, body):
		if self.message_callback:
			self.message_callback(ObjectHelper.unpack(body))

class ObjectHelper(object):

	#Pack a GisMOH object into a string
	@staticmethod
	def pack(obj):
		return dumps(obj, cls=GISMOH_encoder)

	#Unpack a GisMOH object from a string
	@staticmethod
	def unpack(object_string):
		return loads(object_string, object_hook=GISMOH_object_hook)
