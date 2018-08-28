from django.http import HttpResponseRedirect
from django.shortcuts import render

from infusionsoft.library import Infusionsoft

from .forms import TransferForm
from .free_trial_transfer_services.free_trial_transfer_services import begin
from services.exceptions import InfusionsoftAPIError


def form(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            source = Infusionsoft(
                form['src_app_name'].value(),
                form['src_api_key'].value())
            destination = Infusionsoft(
                form['dest_app_name'].value(),
                form['dest_api_key'].value())
            try:
                begin(source, destination)
            except InfusionsoftAPIError as e:
                print(e)
            else:
                return HttpResponseRedirect('thanks')
    else:
        form = TransferForm()
    return render(request, 'freetrialtransfer/form.html', {'form': form})


def thanks(request):
    return render(request, 'freetrialtransfer/thankyou.html')
