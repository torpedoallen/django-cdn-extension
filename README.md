

### Requirements
***
```
    see pip-req.txt
```

### Sample Django settings
***
```
    STATIC_ROOT = 'static/build'  # build directory

    ONLINE_STATIC_ROOT = 'static' # online prefix

    CDN_FINDER_PREFIX = 'http://static.daixiaomi.com'

    INSTALLED_APPS = (
        'other apps',
        'cdn',
    )

    JINJA2_EXTENSIONS = (
        # extensions
        'cdn.extensions.CdnExtension',
    )

```

### Hope to help

[here](https://github.com/torpedoallen/django-cdn-extension/blob/master/cdn/models.py "static file") is a static files packaging script
