import uuid, json
from interfaces.Rabbit import Producer, Consumer
from tornado.options import options
from time import ctime

class AnalysisRequest(object):
	def __init__(self, analysis_type, params):
		self.type = analysis_type

		self.uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'gismoh.dide.ic.ac.uk/analysis/%s/%s' % (json.dumps(params), str(ctime()))))
		self.params = { 'uuid' : self.uuid, 'params' : params }

	def send_analysis_request(self):
		self.connection.sendMessage(self.params if type(self.params) == str else json.dumps(self.params), self.finish)

	def finish(self):
		self.connection.close()

	def start_request(self):
		self.connection = Producer(options.rabbit_server, options.analysis_request_exchange, self.type, self.type)
		self.connection.addOnReady(self.send_analysis_request)
		return self.uuid

class AnalysisRequestReciever(object):
	def __init__(self, analysis_type, message_callback):
		self.consumer = Consumer(options.rabbit_server, options.analysis_request_exchange, analysis_type, analysis_type)
		self.consumer.addMessageHandler(self.messageRecieved)
		self.message_callback = message_callback
		self.consumer.listen()

	def messageRecieved(self, message_id, app_id, body):
		if self.message_callback:
			data = json.loads(body)

			self.message_callback(message_id, app_id, data)

	def acknowledge(self, message_id):
		self.consumer.acknowledge_message(message_id)

	def negative_acknowledge(self, message_id):
		self.consumer.negative_acknowledge_message(message_id)

	def close(self):
		self.consumer.close()



class AnalysisNotification(object):
	def __init__(self, analysis_type, request_uuid, result):
		self.uuid = request_uuid
		self.analysis_type = analysis_type
		self.result = result

	def send_notification(self):
		queue_name = ('%s.%s' % (self.uuid, self.analysis_type))

		self.connection = Producer(options.rabbit_server, options.analysis_notification_exchange, queue_name, queue_name)
		self.connection.addOnReady(self.ready_to_send)

	def ready_to_send(self):
		self.connection.sendMessage(self.result if type(self.result) == str else json.dumps(self.result), self.finish)

	def finish(self):
		self.connection.close()

class AnalysisNotificationReciever(object):
	def __init__(self, analysis_type, request_uuid, message_callback):
		queue_name = ('%s.%s' % (request_uuid, analysis_type))

		self.consumer = Consumer(options.rabbit_server, options.analysis_notification_exchange, queue_name, queue_name)
		self.consumer.addMessageHandler(self.messageRecieved)
		self.message_callback = message_callback

	def messageRecieved(self, message_id, app_id, body):
		if self.message_callback:
			data = json.loads(body)

			self.message_callback(message_id, app_id, data)

	def acknowledge(self, message_id):
		self.consumer.acknowledge_message(message_id)

	def close(self):
		self.consumer.close(ioloop=False)
