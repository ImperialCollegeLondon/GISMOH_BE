
Feature: The Webserver for the Rabbit-enabled GisMOH

	Scenario: We request an analysis from the server
		Given there are no workers running
			When we ask for a "basic_overlap" analysis
			Then we should get an unavailable error

		Given there is a "basic_overlap" worker running
			When we ask for a "basic_overlap" analysis
			Then we should get a valid response
