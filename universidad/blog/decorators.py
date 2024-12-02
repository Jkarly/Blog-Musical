

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def group_required(group_name):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            else:
                return redirect('acceso_denegado')
        return _wrapped_view
    return decorator