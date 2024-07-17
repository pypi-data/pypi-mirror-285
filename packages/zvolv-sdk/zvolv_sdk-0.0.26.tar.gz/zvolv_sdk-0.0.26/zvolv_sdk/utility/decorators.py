from functools import wraps
import traceback

def enforce_pydantic_model(model_class):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for arg in args:
                if isinstance(arg, model_class):
                    break
            else:
                raise TypeError(f"Expected instance of {model_class.__name__}, got {type(arg)}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def handler_wrapper(func):
    def handler(context, event):
        print('in decorator warpper')
        try:
            result = func(context, event)
            context.client.logger.closeExecutionLog('success', 'Execution completed', result, None)
            return result
        except Exception as e:
            trace = traceback.format_exc()
            context.client.logger.closeExecutionLog('failure', str(e), None, trace)
            raise
    return handler
