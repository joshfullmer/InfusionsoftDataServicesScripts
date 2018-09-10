from django.contrib import messages
from django.shortcuts import render, redirect

import datetime
import requests
import urllib

from instance.models import Instance


def instance_form(request, instance_name):
    try:
        instance = Instance.objects.get(name=instance_name)
    except Instance.DoesNotExist:
        messages.error(
            request,
            f'Authorization for "{instance_name}" does not exist')
        return redirect('/emailhistoryexport')
    else:
        if instance.access_token is None:
            messages.error(request, 'No access token')
            return redirect('/emailhistoryexport')
        if instance.expire_time < datetime.datetime.now(datetime.timezone.utc):
            # renew token
            pass

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
        params = {
            'client_id': 'nndwt7ass8w95kqfgh2utw9h',
            'client_secret': 'fWew3CY7zp',
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': request.build_absolute_uri('?'),
        }
        response = requests.post(
            'https://api.infusionsoft.com/token',
            params,
        )
        if response.json().get('error'):
            messages.error(request, response.json().get('error_description'))
        else:
            r_json = response.json()
            name = r_json.get('scope').split('.')[0][1:]
            access_token = r_json.get('access_token')
            refresh_token = r_json.get('refresh_token')
            now = datetime.datetime.now(datetime.timezone.utc)
            expires_in = r_json.get('expires_in')
            expire_time = now + datetime.timedelta(seconds=expires_in)
            try:
                instance = Instance.objects.get(name=name)
            except Instance.DoesNotExist:
                instance = Instance(
                    name=name,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expire_time=expire_time)
            else:
                instance.access_token = access_token
                instance.refresh_token = refresh_token
                instance.expire_time = expire_time
            instance.save()
            return redirect(f'/emailhistoryexport/{name}')

    context = {
        'client_id': 'nndwt7ass8w95kqfgh2utw9h',
        'redirect_uri': redirect_uri,
    }
    return render(request, 'emailhistoryexport/form.html', context)
