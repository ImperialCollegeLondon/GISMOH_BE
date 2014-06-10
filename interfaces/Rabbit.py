import pika
from pika.adapters.tornado_connection import TornadoConnection
from tornado.options import options

import types

from modules import Logging

log = Logging.get_logger('Gismoh.Rabbit')
Logging.add_console_handler(log)

# 04/06/2014 - Modification of the Connection to spawn, rather than subclass Producers and consumers

class Connection(object):
	def __init__ (self, server):

		self.is_ready = False
		self.onReady = None
		self.ioloop_running = False

		self.connection = TornadoConnection(pika.ConnectionParameters( server ), self.connectCallback, self.error)


	def connectCallback(self, connection):
		self.connection.add_on_close_callback(self.connectionClosedCallback)
		self.ready()

	def ready(self):
		self.is_ready = True

		if self.onReady is not None:
			self.onReady(self)

	def getConsumer(self, exchange_name, queue_name=None, routing_key=None, auto_delete=False):
		return Consumer(self.connection, exchange_name, queue_name, routing_key, auto_delete)

	def getProducer(self, exchange_name, queue_name=None, routing_key=None):
		return Producer(self.connection, exchange_name, queue_name, routing_key)

	def close(self):
		self.connection.close()
		if self.ioloop_running :
			self.connection.ioloop.stop()

	def error(self, error):
		log.error('error')
		self.close()


	def connectionClosedCallback(self, connection, reply_code, reply_text):
		log.info('connection closed')

	def runio(self):
		log.info('runion')
		self.ioloop_running = True
		self.connection.ioloop.start()

	def addOnReady(self, callback):

		if self.is_ready :
			callback(self.connection)

		self.onReady = callback


class Channel(object):
	def __init__(self, connection, exchange_name, queue_name=None, routing_key=None, auto_delete=False):
		self.is_ready = False
		self.onReady = None

		self.exchange_name =  '%s.%s' % (options.rabbit_prefix, exchange_name)
		self.queue_name = '%s.%s' % (options.rabbit_prefix, queue_name)
		self.routing_key = routing_key
		self.openChannel(connection)

	def ready(self):
		self.is_ready = True

		if self.onReady is not None:
			self.onReady()

	def openChannel(self, connection):
		connection.channel(self.channelOpenCallback)

	def channelOpenCallback(self, channel):
		self.channel = channel
		self.channel.add_on_close_callback(self.channelClosed)
		self.ready()

	def addOnReady(self, callback):

		if self.is_ready :
			callback()

		self.onReady = callback

	def close(self):
		self.channel.close(0, 'closing normally')
		log.info('channel closing...')

	def channelClosed(self, channel, reply_code, reply_text):
		log.info('channel closed ' + reply_text)

	def error(self, error):
		log.error(error)

class Consumer(Channel):
	def __init__(self, connection, exchange_name, queue_name, routing_key=None, auto_delete=False):
		log.info('create consumer')
		super(Consumer, self).__init__(connection, exchange_name, queue_name, routing_key)
		self.messageHandler = None
		self.auto_delete = auto_delete

	def openChannel(self, connection):
		log.info('open channel')
		connection.channel(self.channelOpenCallback)

	def channelOpenCallback(self, channel):
		log.info('channel open')
		self.channel = channel
		self.channel.add_on_close_callback(self.channelClosed)
		log.info('Auto delete = %s', self.auto_delete)
		self.channel.queue_declare(self.queue_declared, self.queue_name, auto_delete = self.auto_delete)

	def queue_declared(self, queue):
		if self.routing_key is not None:
			self.channel.queue_bind(self.queue_bound, self.queue_name, self.exchange_name, self.routing_key)
		else:
			self.queue_bound(None)

	def queue_bound(self, unused_frame):
		self.channel.basic_consume(self.onMessageRecieved, self.queue_name)
		self.ready()

	def delete_queue(self, callback, queue_name):
		self.channel.queue_delete(callback, queue_name)

	def acknowledge_message(self, tag):
		self.channel.basic_ack(tag)

	def negative_acknowledge_message(self, tag):
		self.channel.basic_nack(tag)

	def addMessageHandler(self, handler):
		self.messageHandler = handler

	def onMessageRecieved(self, channel, basic_deliver, properties, body):
		if self.messageHandler :
			self.messageHandler(basic_deliver.delivery_tag, properties.app_id, body)


class Producer(Channel):
	def sendMessage(self, msg, callback):
		self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=msg)
		callback()

	def channelOpenCallback(self, channel):
		self.channel = channel
		self.channel.add_on_close_callback(self.channelClosed)
		self.channel.exchange_declare(self.exchange_declared, self.exchange_name, 'topic', durable=True)

	def exchange_declared(self, guff):
		self.ready()
