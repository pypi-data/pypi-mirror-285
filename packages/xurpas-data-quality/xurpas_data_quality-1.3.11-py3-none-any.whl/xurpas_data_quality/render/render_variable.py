from xurpas_data_quality.data.describer import TableDescription

from visions import Float, Integer, Date, Categorical, Generic

def render_variable(data: dict):
    if Float in data['type'] or Integer in data['type']:
        return render_numerical(data)
    
    elif Categorical in data['type']:
        return render_categorical(data)
    
    elif Date in data['type']:
        return render_date(data)
    
    else:
        return render_generic(data)