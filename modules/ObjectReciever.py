from modules.ObjectMessaging import ObjectReciever
from interfaces.Rabbit import Connection

from tornado.options import options

from application import create_db_instance, init_app
from modules import Logging

log = Logging.get_logger('Object_reciever')
Logging.add_console_handler(log)

pika_logger = Logging.get_logger('pika')
Logging.set_level(pika_logger, 'error')

def save_object(obj):
	log.info(obj)
	obj.save(db)

def connect(connection):
	reciever = ObjectReciever(connection, None, save_object)

if __name__ == '__main__' :
	init_app()
	db = create_db_instance(options.db_type, options.db_constr)
	connection = Connection(options.rabbit_server)
	connection.addOnReady(connect)
	connection.runio()
