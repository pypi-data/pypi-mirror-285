import wrapt


def patch_livereload_to_fix_bug_around_wsgi_support():  
    """
    This patch is to fix the error descrbed here: https://stackoverflow.com/questions/78039400/flask-with-livereload-and-tornado-causing-error-when-i-run-my-program
    This implements the fix proposed in https://github.com/lepture/python-livereload/pull/275
    """

    from livereload.server import WSGIContainer


    @wrapt.patch_function_wrapper('livereload.server', 'LiveScriptContainer.__call__')
    def patched_call(wrapped, instance, args, kwargs):
        """
        LiveScriptContainer.__call__ is trying to call an instance method of its parent class as a static method.
        The problem is that it was changed from a static method in some change, and this is what broke things.
        Here, we trick the __call__ method into using a WSGIContainer instance instead of the type.
        """
        wrapped.__globals__['WSGIContainer'] = WSGIContainer(wsgi_application=instance.wsgi_app)
        return wrapped(*args, **kwargs)

