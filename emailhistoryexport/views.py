from django.contrib import messages
from django.core.files.temp import NamedTemporaryFile
from django.http import FileResponse
from django.shortcuts import render, redirect

import datetime
import os
import urllib

from instance.models import Instance
from services.api import (get_access_token_response,
                          get_refresh_token_response)
from services.ftp.ftp import upload_file


def instance_form(request, instance_name):
    try:
        instance = Instance.objects.get(name=instance_name)
    except Instance.DoesNotExist:
        messages.error(
            request,
            f'Tokens for "{instance_name}" does not exist')
        return redirect('/emailhistoryexport')
    else:
        if instance.access_token is None:
            messages.error(request, 'No access token')
            return redirect('/emailhistoryexport')
        if instance.expire_time < datetime.datetime.now(datetime.timezone.utc):
            response = get_refresh_token_response(instance.refresh_token)
            Instance.create_or_update_instance(response)

    context = {'instance_name': instance_name}
    return render(request, 'emailhistoryexport/instance_form.html', context)


def form(request):
    code = request.GET.get('code')
    redirect_uri = urllib.parse.quote_plus(request.build_absolute_uri('?'))

    # if a code is in the response params, it has been redirected from
    # authorization.
    #
    # Get tokens and persist to database.
    if code:
        response = get_access_token_response(request, code)
        if response.json().get('error'):
            messages.error(request, response.json().get('error_description'))
        else:
            name = Instance.create_or_update_instance(response)
            return redirect(f'/emailhistoryexport/{name}')

    context = {
        'client_id': 'nndwt7ass8w95kqfgh2utw9h',
        'redirect_uri': redirect_uri,
    }
    return render(request, 'emailhistoryexport/form.html', context)


def begin(request, instance_name):
    try:
        tmp = NamedTemporaryFile(delete=False)
        with open(tmp.name, 'w') as file:
            file.write('hello')
            upload_file(file)
        response = FileResponse(open(tmp.name, 'rb'))
        filename = f'hello_{instance_name}.txt'
        disp = f'attachment; filename={filename}'
        response['Content-Disposition'] = disp
        return response
    finally:
        os.remove(tmp.name)
