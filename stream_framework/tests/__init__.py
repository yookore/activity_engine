
try:
    from django.conf import settings
    try:
        # ignore this if we already configured settings
        settings.configure()
    except RuntimeError, e:
        pass
except:
    pass
