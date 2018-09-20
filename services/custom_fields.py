from .constants import CF_FORM_ID
from .exceptions import InfusionsoftAPIError
from .tables import get_table


def create_custom_field(ifs, fieldname, tablename='Contact',
                        fieldtype='Text', values=None):
    form_id = CF_FORM_ID.get(tablename)
    if not form_id:
        raise InfusionsoftAPIError(
            'InfusionsoftAPIError: tablename not recognized')
    query_criteria = {'Label': fieldname, 'FormId': form_id}
    existing_fields = get_table(ifs, 'DataFormField', query_criteria)
    if existing_fields and len(existing_fields) > 1:
        print(existing_fields)
        raise InfusionsoftAPIError(
            f'InfusionsoftAPIError: two custom fields with the same label: '
            f'{existing_fields[0]["Label"]}')

    existing_field = existing_fields[0] if existing_fields else None

    field = {}
    if not existing_field:
        header_id = get_custom_field_header(ifs, tablename)

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

        field['Name'] = "_" + get_table(
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
        field['Id'] = existing_field['Id']
        field['Name'] = '_' + existing_field['Name']

    return field


def get_custom_field_header(ifs, tablename='Contact'):
    """Checks if field exists by given fieldname
    Returns header id"""

    form_id = CF_FORM_ID.get(tablename)
    tab = get_table(ifs, 'DataFormTab', {'FormId': form_id})
    if not tab:
        raise InfusionsoftAPIError(
            f'InfusionsoftAPIError: {tablename} custom '
            f'field tab does not exist')
    tab_id = tab[0]['Id']

    header = get_table(ifs, 'DataFormGroup', {'TabId': tab_id})
    if not header:
        raise InfusionsoftAPIError(
            f'InfusionsoftAPIError: {tablename} custom '
            f'field header does not exist')
    header_id = header[0]['Id']
    return header_id
