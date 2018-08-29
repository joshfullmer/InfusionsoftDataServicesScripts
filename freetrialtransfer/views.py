from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

import json

from infusionsoft.library import Infusionsoft

from .forms import TransferForm
from .free_trial_transfer_services.free_trial_transfer_services import begin
from services.exceptions import InfusionsoftAPIError


def form(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():

            # Instantiate Infusionsoft apps
            source = Infusionsoft(
                form['src_app_name'].value(),
                form['src_api_key'].value())
            destination = Infusionsoft(
                form['dest_app_name'].value(),
                form['dest_api_key'].value())

            # Run transfer
            # Catch Infusionsoft API errors and add to messages
            results = {}
            try:
                results = begin(source, destination)
            except InfusionsoftAPIError as e:
                messages.error(request, e)

            # Add result string to django messages
            else:
                results['source'] = form['src_app_name'].value()
                results['destination'] = form['dest_app_name'].value()
                result_string = json.dumps(results)
                messages.info(request, result_string)
                return HttpResponseRedirect('thanks')
    else:
        form = TransferForm()
    return render(request, 'freetrialtransfer/form.html', {'form': form})


def thanks(request):

    # Parse messages into dictionary and send to context
    storage = messages.get_messages(request)
    results = [message.message for message in storage]
    results = json.loads(results[0])
    return render(request, 'freetrialtransfer/thankyou.html', results)
