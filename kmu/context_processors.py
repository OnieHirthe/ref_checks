from django.conf import settings
from kmu.utils import year


def static_versioning(request):
    return {
        'static_version' : settings.STATIC_VERSION,
    }


def stage_flags(request):
    return {
        'flags' : settings.CONF_FLAGS
    }

def conf_years(request):
    return {
        'years' : settings.CONF_YEARS
    }
