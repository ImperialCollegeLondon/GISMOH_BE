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
