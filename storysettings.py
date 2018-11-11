import json


def get_settings_json(name):
    if name == 'global':
        settings_json = [
            {'type': 'title',
             'title': 'Global Settings'},
            {'type': 'string',
             'title': 'color',
             'desc': 'Base color',
             'section': 'global',
             'key': 'color'}]
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


def get_story_settings(name, pages=2):
    settings_json = [
        {'type': 'title',
         'title': "{} Settings".format(name)
         },
        {'type': 'string',
         'title': 'Title Name',
         'desc': 'The name of the Story',
         'section': 'title',
         'key': 'name'},
        {'type': 'string',
         'title': 'Title Text',
         'desc': 'Text for the title page',
         'section': 'title',
         'key': 'text'},
        {'type': 'string',
         'title': 'Author',
         'desc': 'Story Author',
         'section': 'title',
         'key': 'author'},
        {'type': 'options',
         'title': 'Media Type',
         'desc': 'Image or Video type',
         'options': ['image', 'video'],
         'section': 'title',
         'key': 'media'
         },
        {'type': 'path',
         'title': 'Media Location',
         'desc': 'Filename of the media',
         'section': 'title',
         'key': 'media_location',
         'dirselect': False}
    ]

    for i in range(1, pages + 1):
        settings_json.append({
            {'type': 'string',
             'title': 'name',
             'desc': 'The name of the Page',
             'section': "page{}".format(str(i)),
             'key': 'name'},
            {'type': 'string',
             'title': 'Page Name',
             'desc': 'The name of the page',
             'section': "page{}".format(str(i)),
             'key': 'name'},
            {'type': 'string',
             'title': 'Page Text',
             'desc': 'Text for this page',
             'section': "page{}".format(str(i)),
             'key': 'text'},
            {'type': 'options',
             'title': 'Media Type',
             'desc': 'Image or Video type',
             'options': ['image', 'video'],
             'section': "page{}".format(str(i)),
             'key': 'media'
             },
            {'type': 'path',
             'title': 'Media Location',
             'desc': 'Filename of the media',
             'section': "page{}".format(str(i)),
             'key': 'media_location',
             'dirselect': False}
        })

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
