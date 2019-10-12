def get_sheet_title(model):
    # module_name is renamed to model_name in Django 1.8
    app_label = model._meta.app_label
    try:
        return '%s_%s' % (app_label, model._meta.model_name,)
    except AttributeError:
        return '%s_%s' % (app_label, model._meta.module_name,)
