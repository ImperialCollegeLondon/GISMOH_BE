from modules.analysis.Base import AnalysisRequestReciever, AnalysisNotification
from modules import Logging
from modules.Antibiogram import Antibiogram
from modules.Location import LocationInterface

from store.Store import Patient, Isolate

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

		logger.info('%s - recieved' % (body['uuid']))

		request.analyze_all_antibiograms()

		if type(request.results) is dict:
			self.acknowledge(message_id)
			self.send_results(request)
		else:
			self.negative_acknowledge(message_id)

	def send_results(self, request):
		Notification = AnalysisNotification('similarity', request.uuid, request.results).send_notification(self.connection)


class AntibiogramSimilarityRequest(object):
	def __init__(self, uuid, request_params):
		self.uuid = uuid
		self.isolates = request_params
		self.results = {}
		self.patient_ids = []
		init_app()

		self.db = create_db_instance()
		#we can submit mutliple isolate IDS so we should return the result
		# with each collection keyed to the isolate that it was related to

	def analyze_all_antibiograms(self):

		related_antibiograms = {}

		for isolate in self.isolates:
			self.patient_ids = []

			antibiogram = Antibiogram.find(self.db, isolate)

			if antibiogram is not None:
				nearest_antibiograms = Antibiogram.get_nearest(self.db, antibiogram)

				self.results[isolate] = []

				for near_antibiogram in nearest_antibiograms:
					self.results[isolate].append(near_antibiogram)
					if self.patient_ids.count(near_antibiogram['patient']) == 0:
						self.patient_ids.append(near_antibiogram['patient'])
				# Do location overlap analysis
				self.look_for_overlaps()

		return self.results

	def look_for_overlaps(self):
		for isolate_number in self.results:
			patient_id = Isolate.get(self.db, isolate_number).patient_id
			for antibiogram in self.results[isolate_number]:
				antibiogram['location_overlaps'] = 0

				if patient_id is not None:
					location_interface = LocationInterface(self.db)
					location_overlaps = location_interface.get_overlaps_with_patient(Patient.get(self.db, patient_id))

					for overlap_key in location_overlaps:
						overlapping_location = location_overlaps[overlap_key]
						continue

						if self.patient_ids.count(overlapping_location.patient_id):
							for antibiogram in self.results[isolate_number]:
								if antibiogram['patient'] == overlapping_location.patient_id:
									antibiogram['location_overlaps'] += 1
				else:
					logger.error ('no patient ' + str(patient_id))

def connect(connection):
	AntibiogramWorker(connection)

if __name__ == '__main__':
	rabbit_connection = Connection(options.rabbit_server)
	rabbit_connection.addOnReady(connect)
	rabbit_connection.runio()
