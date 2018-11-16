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


def get_story_settings_metadata(name, library):
    settings_json = [
        {'type': 'title',
         'title': "{}: '{}' metadata settings".format(library, name)
         },
        {'type': 'string',
         'title': 'Story Name',
         'desc': 'The name of the story',
         'section': 'metadata',
         'key': 'story'},
        {'type': 'string',
         'title': 'Library Name',
         'desc': 'The name of the library',
         'section': 'metadata',
         'key': 'library'},
        {'type': 'string',
         'title': 'Author',
         'desc': 'Story Author',
         'section': 'metadata',
         'key': 'author'},
        {'type': 'page_settings',
         'title': 'Pages in story',
         'desc': 'Add, move or remove pages in the story',
         'section': 'metadata',
         'key': 'pages'},
        {'type': 'buttons',
         'title': 'Title',
         'desc': 'Edit title page',
         'section': 'metadata',
         'key': 'buttons'},
        {'type': 'buttons',
         'title': 'Pages',
         'desc': 'Edit pages',
         'section': 'metadata',
         'key': 'buttons'}
    ]
    return json.dumps(settings_json)


def get_story_settings_title(name, library):
    settings_json = [
        {'type': 'title',
         'title': "{}: '{}' title page settings".format(library, name)
         },
        {'type': 'string',
         'title': 'Title Name',
         'desc': 'The name of the Story',
         'section': 'title',
         'key': 'name'},
        {'type': 'story_text',
         'title': 'Title Text',
         'desc': 'Text for the title page',
         'section': 'title',
         'key': 'text'},
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
    return json.dumps(settings_json)


def get_story_settings_page(name, page, library):
    settings_json = [
        {'type': 'title',
         'title': "{}: {} '{}' settings".format(library, name, page)
         },
        {'type': 'string',
         'title': 'Page Name',
         'desc': 'The name of the page',
         'section': page,
         'key': 'name'},
        {'type': 'story_text',
         'title': 'Page Text',
         'desc': 'Text for this page',
         'section': page,
         'key': 'text'},
        {'type': 'options',
         'title': 'Media Type',
         'desc': 'Image or Video type',
         'options': ['image', 'video'],
         'section': page,
         'key': 'media'
         },
        {'type': 'path',
         'title': 'Media Location',
         'desc': 'Filename of the media',
         'section': page,
         'key': 'media_location',
         'dirselect': False}]

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
