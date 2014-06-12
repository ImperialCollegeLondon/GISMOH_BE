
from behave import given, when, then, step
from store.Store import Patient, GISMOH_encoder, GISMOH_object_hook

from modules.ObjectMessaging import ObjectHelper
from datetime import date, datetime

import pika

from json import loads, dumps


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

@given('we have a Male patient born on 01/02/1920')
def step_impl(context):
	patient = Patient()
	patient.uniq_id = 1
	patient.nhs_number = '000-000-000X'
	patient.sex = 'M'
	patient.date_of_birth = date(1920, 02, 01)
	patient.postcode = 'TT1 1TT'
	patient.add_hospital_number('ADD', 'A00000001')
	patient.add_hospital_number('PAP', 'P00000001')

	context.patient = patient

@when('we pack it into a JSON string')
def step_impl(context):
	context.patient_string = dumps(context.patient, cls=GISMOH_encoder)

@then('the type should be patient')
def step_impl(context):
	patient_json = loads(context.patient_string)
	assert patient_json['gismoh_type'] == 'Patient'

@then('the properties should all be present in the object property')
def step_impl(context):
	patient_json = loads(context.patient_string)
	patient_dict = patient_json['object']
	patient = context.patient

	assert patient.uniq_id == patient_dict['uniq_id']
	assert patient.nhs_number == patient_dict['nhs_number']
	assert patient.sex == patient_dict['sex']
	assert patient.date_of_birth == datetime.strptime(patient_dict['date_of_birth'], '%Y-%m-%d').date()
	assert patient.postcode == patient_dict['postcode']
	assert len(patient_dict['hospital_numbers']) == 2

@then('we un-serialise the object we should get the same object back')
def step_impl(context):
	patient_from_json = loads(context.patient_string, object_hook=GISMOH_object_hook)
	print patient_from_json, context.patient
	assert context.patient == patient_from_json

def callback(ch, method, properties, body):
	print body
	assert body == "Hello World"
