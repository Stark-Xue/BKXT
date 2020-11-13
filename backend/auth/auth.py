from django.shortcuts import redirect

def check_login(func):
    def inner(request, *args, **kwargs):
        if request.session.get('username'):
            return func(request, *args, **kwargs)
        else:
            return redirect("/login/")
    return inner