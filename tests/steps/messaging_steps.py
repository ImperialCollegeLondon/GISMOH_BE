
from behave import given, when, then, step

import pika

@given('pika is installed')
def step_impl(context):
	pass

@when('we try to send the messsage "Hello World"')
def step_impl(context):

	connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.30.10'))
	channel = connection.channel()
	channel.queue_declare(queue='hello')
	channel.basic_publish(exchange='', routing_key='hello', body='Hello World')

@then('we should not get an error')
def step_impl(context):
	assert True

@given('we sent a "Hello World" message')
def step_impl(context):

	connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.30.10'))
	channel = connection.channel()
	channel.queue_declare(queue='hello')
	channel.basic_publish(exchange='', routing_key='hello', body='Hello World')

@when('we attach a consumer')
def step_impl(context):
	pass

@then('we should get a Hello World Message From the server')
def step_impl(context):
	connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.30.10'))
	channel = connection.channel()
	channel.queue_declare(queue='hello')

	channel.basic_consume(callback, queue='hello', no_ack=True)
	channel.start_consuming

def callback(ch, method, properties, body):
	print body
	assert body == "Hello World"
