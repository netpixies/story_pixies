import json

def get_settings_json(name):
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
         'dirselect': True},
        {'type': 'library_options',
         'title': 'Current Book',
         'desc': 'The Current Book',
         'section': 'libraryname',
         'key': 'current_book'}]

    for idx, i in enumerate(settings_json):
        if settings_json[idx].get('section'):
            settings_json[idx]['section'] = name

    return json.dumps(settings_json)
