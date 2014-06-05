from modules.analysis.Base import AnalysisRequestReciever, AnalysisNotification
from modules import Logging
from modules.Antibiogram import Antibiogram
from modules.Location import LocationInterface

from interfaces.Rabbit import Connection

from tornado.options import options

from application import create_db_instance, init_app

logger = Logging.get_logger('GISMOH.Antibiogram_worker')
Logging.add_console_handler(logger)

pika_logger = Logging.get_logger('pika')
Logging.set_level(pika_logger, 'error')

class AntibiogramWorker(AnalysisRequestReciever):
	def __init__(self, connection):
		self.connection = connection

		try:
			super(AntibiogramWorker, self).__init__(connection, 'similarity', self.process_request)
		except KeyboardInterrupt:
			self.close()
			logger.info('Worker Stopped')


	def process_request(self, message_id, app_id, body):
		request = AntibiogramSimilarityRequest(body['uuid'], body['params'])

		request.analyze_all_antibiograms()

		if type(request.results) is dict:
			logger.info('ack' + str(message_id))
			self.acknowledge(message_id)
			self.send_results(request)
		else:
			self.negative_acknowledge(message_id)
			logger.info('nack' + result.isolates)

	def send_results(self, request):
		Notification = AnalysisNotification('similarity', request.uuid, request.results).send_notification(self.connection)


class AntibiogramSimilarityRequest(object):
	def __init__(self, uuid, request_params):
		self.uuid = uuid
		self.isolates = request_params
		self.results = {}
		#we can submit mutliple isolate IDS so we should return the result
		# with each collection keyed to the isolate that it was related to

	def analyze_all_antibiograms(self):
		init_app()
		db = create_db_instance()

		related_antibiograms = {}

		for isolate in self.isolates:

			antibiogram = Antibiogram.find(db, isolate)

			if antibiogram is not None:
				logger.info(antibiogram)
				nearest_antibiograms = Antibiogram.get_nearest(db, antibiogram)

				self.results[isolate] = []

				for near_antibiogram in nearest_antibiograms:
					self.results[isolate].append(near_antibiogram)

		return self.results


def connect(connection):
	AntibiogramWorker(connection)

if __name__ == '__main__':
	rabbit_connection = Connection(options.rabbit_server)
	rabbit_connection.addOnReady(connect)
	rabbit_connection.runio()
