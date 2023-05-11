def get_include_fields(model_fields, exclude_fields):
    include_fields = []
    for field in model_fields:
        if field not in exclude_fields:
            include_fields.append(field)

    return include_fields
