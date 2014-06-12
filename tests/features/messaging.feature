# -- FILE: featues/messaging.feature
Feature: Check Rabbit Server is working
	Scenario: Send Hello World
		Given pika is installed
			When we try to send the messsage "Hello World"
			Then we should not get an error

	Scenario: Recieve Hello World
		Given we sent a "Hello World" message
			When we attach a consumer
			Then we should get a Hello World Message From the server

	Scenario: When we want to send a patient object
		Given we have a Male patient born on 01/02/1920
			When we pack it into a JSON string
			Then the type should be patient
				and the properties should all be present in the object property
				and we un-serialise the object we should get the same object back
