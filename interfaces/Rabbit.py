import pika
from pika.adapters.tornado_connection import TornadoConnection
from tornado.options import options

import types

class Connection(object):
	def __init__ (self, server, exchange_name, queue_name=None, routing_key=None):

		self.exchange_name =  '%s.%s' % (options.rabbit_prefix, exchange_name)
		self.queue_name = '%s.%s' % (options.rabbit_prefix, queue_name)
		self.routing_key = routing_key

		self.is_ready = False
		self.onReady = None

		self.connection = TornadoConnection(pika.ConnectionParameters(server), self.connectCallback, self.error)


	def connectCallback(self, connection):
		self.connection.add_on_close_callback(self.connectionClosedCallback)
		self.connection.channel(on_open_callback=self.channelOpenCallback)

	def channelOpenCallback(self, channel):

		self.channel = channel
		self.channel.add_on_close_callback(self.channelClosed)
		self.ready()

	def ready(self):
		self.is_ready = True

		if self.onReady is not None:
			self.onReady()

	def addOnReady(self, callback):

		if self.is_ready :
			callback()

		self.onReady = callback

	def close(self):
		self.connection.close()

	def channelClosed(self, one, two, three):
		pass

	def connectionClosedCallback(self, connection, reply_code, reply_text):
		pass

	def error(self, error):
		pass

class Consumer(Connection):
	def __init__(self, server, exchange_name, queue_name, routing_key=None):
		super(Consumer, self).__init__(server, exchange_name, queue_name, routing_key)
		self.messageHandler = None

	def channelOpenCallback(self, channel):
		self.channel = channel
		self.channel.queue_declare(self.queue_declared, self.queue_name)

	def queue_declared(self, queue):
		if self.routing_key is not None:
			self.channel.queue_bind(self.queue_bound, self.queue_name, self.exchange_name, self.routing_key)
		else:
			self.queue_bound(None)

	def queue_bound(self, unused_frame):
		self.channel.basic_consume(self.onMessageRecieved, self.queue_name)
		self.ready()

	def listen(self):
		self.connection.ioloop.start()

	def acknowledge_message(self, tag):
		self.channel.basic_ack(tag)

	def negative_acknowledge_message(self, tag):
		self.channel.basic_nack(tag)

	def addMessageHandler(self, handler):
		self.messageHandler = handler

	def onMessageRecieved(self, channel, basic_deliver, properties, body):
		if self.messageHandler :
			self.messageHandler(basic_deliver.delivery_tag, properties.app_id, body)

	def close(self, ioloop=True):
		self.connection.close()
		if ioloop:
			self.connection.ioloop.stop()


class Producer(Connection):
	def sendMessage(self, msg, callback):
		self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=msg)
		#callback()

	def channelOpenCallback(self, channel):
		self.channel = channel
		self.channel.add_on_close_callback(self.channelClosed)
		self.channel.exchange_declare(self.exchange_declared, self.exchange_name, 'topic', durable=True)

	def exchange_declared(self, guff):
		self.ready()
