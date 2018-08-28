from .constants import CF_FORM_ID
from .exceptions import InfusionsoftAPIError
from .tables import get_table


def create_custom_field(ifs, fieldname, tablename='Contact',
                        fieldtype='Text', values=None):
    form_id = CF_FORM_ID.get(tablename)
    if not form_id:
        raise InfusionsoftAPIError('Tablename not recognized')
    query_criteria = {'Label': fieldname, 'FormId': form_id}
    all_custom_fields = get_table(ifs, 'DataFormField', query_criteria)

    existing_field = [f for f in all_custom_fields if f['FormId'] == form_id]

    field = {}
    if not existing_field:
        tab = get_table(ifs, 'DataFormTab', {'FormId': form_id})
        if not tab:
            raise InfusionsoftAPIError(
                f'InfusionsoftAPIError: {tablename} custom'
                ' field tab does not exist')
        tab_id = tab[0]['Id']

        header = get_table(ifs, 'DataFormGroup', {'TabId': tab_id})
        if not header:
            raise InfusionsoftAPIError(
                f'InfusionsoftAPIError: {tablename} custom'
                ' field header does not exist')
        header_id = header[0]['Id']

        created_field = ifs.DataService(
            'addCustomField',
            tablename,
            fieldname,
            fieldtype,
            header_id)
        if isinstance(created_field, tuple) or not created_field:
            raise InfusionsoftAPIError(
                f'InfusionsoftAPIError: custom field could not be created:'
                f'{created_field[1]}')
        field['Id'] = created_field

        field['Name'] = get_table(
            ifs,
            'DataFormField',
            {'Id': created_field},
            ['Name'])[0]['Name']

        if values and values.get('Values'):
            created_values = ifs.DataService(
                'updateCustomField',
                field['Id'],
                values)
            if isinstance(created_values, tuple):
                raise InfusionsoftAPIError(
                    'InfusionsoftAPIError: custom field values'
                    ' could not be added')
    else:
        field['Id'] = existing_field[0]['Id']
        field['Name'] = '_' + existing_field[0]['Name']

    return field
