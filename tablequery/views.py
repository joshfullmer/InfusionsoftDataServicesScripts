from django.contrib import messages
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from wsgiref.util import FileWrapper

import pandas as pd

from infusionsoft.library import Infusionsoft

from .forms import QueryForm
from services.exceptions import InfusionsoftAPIError
from services.tables import get_table


def query(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            app_name = form['app_name'].value()
            api_key = form['api_key'].value()
            tablename = form['tablename'].value()
            ifs = Infusionsoft(
                app_name,
                api_key)
            results = {}
            try:
                results = get_table(ifs, tablename)
            except InfusionsoftAPIError as e:
                messages.error(e)
            else:
                df = pd.DataFrame(results)
                if 'csv_export' in request.POST:
                    file = NamedTemporaryFile(suffix='.csv')
                    df.to_csv(file.name, index=False)
                    wrapper = FileWrapper(file)
                    response = HttpResponse(wrapper, content_type='text/csv')
                    now = timezone.now()
                    now_str = now.strftime('%Y%m%dT%H%MZ')
                    filename = f'{app_name}_{tablename}_{now_str}.csv'
                    disp = f'attachment; filename={filename}'
                    response['Content-Disposition'] = disp
                    return response
                df_html = df.to_html(index=False, na_rep='')
    else:
        form = QueryForm()
        df_html = None
    return render(
        request,
        'tablequery/query.html',
        {'form': form, 'df': df_html})
