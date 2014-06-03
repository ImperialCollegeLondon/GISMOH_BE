# -- FILE: features/OverlapWorker.feature
Feature: The overlap worker for the rabbit-enabled GisMOH System

	Scenario : Spin up
		Given there are no other "basic_overlap" workers running
			When we start the "basic_overlap" worker
			Then there should be one "basic_overlap" queue

		Given there are other "basic_overlap" workers running
			When we start the "basic_overlap" worker
			Then there should be one "basic_overlap" queue

	Scenario: Shut down
		Given there are other "basic_overlap" workers running
			When we stop the "basic_overlap" worker
			Then there should be one "basic_overlap" queue

		Given there are no other "basic_overlap" workers running
			When we stop the "basic_overlap" worker
			Then there should be no "basic_overlap" queue
