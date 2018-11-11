import json

def get_settings_json(name):
    if name == 'global':
        settings_json = [
        {'type': 'title',
         'title': 'Global Settings'},
        {'type': 'path',
         'title': 'Template Location',
         'desc': 'The template directory',
         'section': 'global',
         'key': 'template_dir',
         'dirselect': True}]
    else:
        settings_json = [
            {'type': 'title',
             'title': 'Story Settings'},
            {'type': 'string',
             'title': 'Library Name',
             'desc': 'The library name',
             'section': 'libraryname',
             'key': 'name'},
            {'type': 'path',
             'title': 'Library Stories',
             'desc': 'Where are the stories located?',
             'section': 'libraryname',
             'key': 'story_dir',
             'dirselect': True}]

        for idx, i in enumerate(settings_json):
            if settings_json[idx].get('section'):
                settings_json[idx]['section'] = name

    return json.dumps(settings_json)

def get_new_settings(name):
    settings_json = [
        {'type': 'title',
         'title': 'New panel'},
        {'type': 'string',
         'title': 'New Name',
         'desc': 'The new name',
         'section': 'title',
         'key': 'pages'}
    ]

    return json.dumps(settings_json)
