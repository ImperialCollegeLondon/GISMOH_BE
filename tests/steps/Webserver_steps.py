from behave import given, when, then, step

@given("there are no workers running")
def step_impl(context):
	pass

@given('there is a "{worker_type}" worker running')
def step_impl(context, worker_type):
	pass

@when('we ask for a "{analysis_type}" analysis')
def step_impl(context, analysis_type):
	pass

@then('we should get an unavailable error')
def step_impl(context):
	pass

@then('we should get a valid response')
def step_impl(context):
	pass
