from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def csrf(request):
    return HttpResponse()

# def chat_startup(request):
#     groups = [{'group_name': g.group_name, 'group_id': g.id} for g in request.user.groups]
#     return JsonResponse({
#         'groups': groups
#     })
