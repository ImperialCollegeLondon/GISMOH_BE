from behave import given, when, then, step

@given('there are no other "{worker_type}" workers running')
def step_impl(context, worker_type):
	pass

@given('there are other "{worker_type}" workers running')
def step_impl(context, worker_type):
	pass

@when('we start the "{worker_type}" worker')
def step_impl(context, worker_type):
	pass

@when('we stop the "{worker_type}" worker')
def step_impl(context, worker_type):
	pass

@then('there should be one "{worker_type}" queue')
def step_impl(context, worker_type):
	pass

@then('there should be no "{worker_type}" queue')
def step_impl(context, worker_type):
	pass
