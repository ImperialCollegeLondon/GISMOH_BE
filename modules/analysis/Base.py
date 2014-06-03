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



class AnalysisNotification(object):
	def __init__(self, analysis_type, request_uuid, result):
		self.uuid = request_uuid
		self.analysis_type = analysis_type
		self.result = result

	def send_notification(self):
		self.connection = Producer(options.rabbit_server, options.analysis_notification_exchange)
		self.connection.addOnReady(self.sendNotifcation)

	def sendNotification(self):
		self.sendMessage('%s.%s' % (self.analysis, self.uuid))

class AnalysisNotificationReciever(object):
	def __init__(self, analysis_type, request_uuid, message_callback):
		self.consumer = Consumer(options.rabbit_server, options.analysis_request_exchange, analysis_type)
		self.consumer.addMessageHandler(self.messageRecieved)
		self.message_callback = message_callback

	def messageRecieved(message_id, app_id, body):
		if self.message_callback:
			message_callback(message_id, app_id, body)
