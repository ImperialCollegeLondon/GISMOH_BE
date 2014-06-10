import uuid, json
from interfaces.Rabbit import Connection, Producer, Consumer
from tornado.options import options
from time import ctime

class AnalysisRequest(object):
	def __init__(self, analysis_type, params):
		self.type = analysis_type

		self.uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'gismoh.dide.ic.ac.uk/analysis/%s/%s' % (json.dumps(params), str(ctime()))))
		self.params = { 'uuid' : self.uuid, 'params' : params }

	def send_analysis_request(self):
		self.producer.sendMessage(self.params if type(self.params) == str else json.dumps(self.params), self.finish)

	def finish(self):
		self.producer.close()

	def start_request(self, connection):
		self.producer = connection.getProducer(options.analysis_request_exchange, self.type, self.type)
		self.producer.addOnReady(self.send_analysis_request)
		return self.uuid

class AnalysisRequestReciever(object):
	def __init__(self, connection, analysis_type, message_callback):

		self.consumer = connection.getConsumer(options.analysis_request_exchange, analysis_type, analysis_type)
		self.consumer.addMessageHandler(self.messageRecieved)
		self.message_callback = message_callback

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

	def send_notification(self, connection):
		queue_name = ('%s.%s' % (self.uuid, self.analysis_type))

		self.sender = connection.getProducer(options.analysis_notification_exchange, queue_name, queue_name)
		self.sender.addOnReady(self.ready_to_send)

	def ready_to_send(self):
		self.sender.sendMessage(self.result if type(self.result) == str else json.dumps(self.result), self.finish)

	def finish(self):
		self.sender.close()

class AnalysisNotificationReciever(object):
	def __init__(self, connection, analysis_type, request_uuid, message_callback):
		self.queue_name = ('%s.%s' % (request_uuid, analysis_type))

		self.consumer = connection.getConsumer(options.analysis_notification_exchange, self.queue_name, self.queue_name, True)
		self.consumer.addMessageHandler(self.messageRecieved)
		self.message_callback = message_callback

	def messageRecieved(self, message_id, app_id, body):
		if self.message_callback:
			data = json.loads(body)

			self.message_callback(message_id, app_id, data)

	def acknowledge(self, message_id):
		self.consumer.acknowledge_message(message_id)

	def close(self):
		self.consumer.delete_queue(self.on_queue_delete_close, self.queue_name)

	def on_queue_delete_close(self, unused):
		print 'xxx closing xxx'
		self.consumer.close()
