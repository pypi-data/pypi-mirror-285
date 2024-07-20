from models import DeepTeaModel

def TEA(data, tea_model, **kwargs):
    '''Tabular embedding alignment (TEA).
    Tabular embedding alignment performs alignment of tabular 
    embeddings to create effective projections between different
    datasets in terms of partially observable entries and columns
    in the datasets. It artificially imputes missing values in the
    datasets and aligns the embeddings to create a common space.
    Through optimizing for the reconstruction loss of the imputed
    values, the model learns to align the embeddings.

    Parameters
    ----------
    data : pandas.DataFrame
        Input data to be aligned.
    tea_model : TeaModel or str
        TeaModel object or string specifying the model to use.
    kwargs : dict

    '''
    data = data.copy()
    if isinstance(tea_model, str):
        tea_model = get_tea_model(tea_model)
    model = tea_model(**kwargs)
    model.fit(data)
    return model.transform(data)


def get_tea_model(model_name):
    '''Get a TEA model by name.
    '''
    if model_name == 'DeepTEA':
        return DeepTeaModel
    else:
        raise ValueError('Model name not recognized.')