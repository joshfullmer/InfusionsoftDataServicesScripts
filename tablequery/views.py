from django.contrib import messages
from django.shortcuts import render

import pandas as pd

from infusionsoft.library import Infusionsoft

from .forms import QueryForm
from services.exceptions import InfusionsoftAPIError
from services.tables import get_table


def query(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            ifs = Infusionsoft(
                form['app_name'].value(),
                form['api_key'].value())
            results = {}
            try:
                results = get_table(ifs, form['tablename'].value())
            except InfusionsoftAPIError as e:
                messages.error(e)
            else:
                df = pd.DataFrame(results)
    else:
        form = QueryForm()
    return render(
        request,
        'tablequery/query.html',
        {'form': form, 'df': df.to_html(index=False, na_rep='')})
