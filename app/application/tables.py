from app.data.utils import raise_error


# create an exact copy of a configuration table
def deepcopy(table):
    if type(table) == dict:
        out = {}
        for k, v in table.items():
            if type(v) == list or type(v) == dict:
                out[k] = deepcopy(v)
            else:
                out[k] = v
    elif type(table) == list:
        out = []
        for i in table:
            if type(i) == list or type(i) == dict:
                out.append(deepcopy(i))
            else:
                out.append(i)
    else:
        out = table
    return out


# prepare the configuration table to be used in the html front end, i.e. remove unwanted members (function calls, ...)
def prepare_config_table_for_view(table):
    try:
        out = deepcopy(table)
        for i in out['template']:
            if 'order_by' in i:
                del i['order_by']
            if not 'orderable' in i:
                i['orderable'] = False
        for k,v in out.items():
            if callable(v):
                out[k] = ''
        out['table_action'] = f'{out["view"]}.table_action'
        out['table_ajax'] = f'{out["view"]}.table_ajax'
    except Exception as e:
        raise_error('Kan de configuratietabel niet ophalen', e)
    return out


def prepare_item_config_for_view(table, action):
    try:
        item_config = table['item'][action]
        item_config['item_action'] = f'{table["view"]}.item_action'
        item_config['action'] = action
    except Exception as e:
        raise_error('Kan de itemconfiguratietabel niet ophalen', e)
    return item_config


