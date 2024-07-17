def handler_startup(context, event):
    print('in interceptor startup')
    headers = event.headers
    automation_uuid = headers['X-Nuclio-Function-Name']
    client = getattr(context, 'client', None)
    client.logger.initExecutionLog(automation_uuid, event.body)
