import json

settings_json = json.dumps([
    {'type': 'title',
     'title': 'settings title'},
    {'type': 'string',
     'title': 'Library Name',
     'desc': 'Set a library name',
     'section': 'library',
     'key': 'name'},
    {'type': 'path',
     'title': 'Library Stories',
     'desc': 'Set library stories',
     'section': 'library',
     'key': 'story_dir',
     'dirselect': True}
])
