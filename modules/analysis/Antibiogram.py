from modules.analysis.Base import AnalysisRequestReciever, AnalysisNotification
from modules import Logging
from modules.Antibiogram import Antibiogram

from application import create_db_instance, init_app

logger = Logging.get_logger('GISMOH.Antibiogram_worker')
Logging.add_console_handler(logger)

class AntibiogramWorker(AnalysisRequestReciever):
	def __init__(self):
		super(AntibiogramWorker, self).__init__('similarity', self.process_request)

	def process_request(self, message_id, app_id, body):
		request = AntibiogramSimilarityRequest(body['uuid'], body['params'])

		request.analyzeAll()

	def send_results(self, request):
		Notification = AnalysisNotification('similarity', requres.uuid, request.results).sendNotification()


class AntibiogramSimilarityRequest(object):
	def __init__(self, uuid, request_params):
		self.uuid = uuid,
		self.isolates = request_params

	def analyzeAll(self):
		init_app();
		db = create_db_instance()

		for isolate in self.isolates:
			logger.debug(isolate)

			antibiogram = Antibiogram.find(db, isolate)
			
			if antibiogram is not None:
				antibiograms = Antibiogram.get_nearest(db, antibiogram, 5)

if __name__ == '__main__':
	AntibiogramWorker()
