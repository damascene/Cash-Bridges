"""
main url configuration file for the askbot site
"""
from django.conf import settings
try:
    from django.conf.urls import handler404
    from django.conf.urls import include, url
except ImportError:
    from django.conf.urls.defaults import handler404
    from django.conf.urls.defaults import include, url

from askbot import is_multilingual
from askbot.views.error import internal_error as handler500
from django.conf import settings
from django.contrib import admin
from django.views import static as StaticViews
from django.urls import re_path

from askbot.utils import postman_filters

from postman.views import WriteView

admin.autodiscover()

if is_multilingual():
    from django.conf.urls.i18n import i18n_patterns
    urlpatterns = i18n_patterns(
        url(r'%s' % settings.ASKBOT_URL, include('askbot.urls'))
    )
else:
    urlpatterns = [
        url(r'%s' % settings.ASKBOT_URL, include('askbot.urls'))
    ]

urlpatterns += [
    url(r'^admin/', admin.site.urls),
    #(r'^cache/', include('keyedcache.urls')), - broken views disable for now
    #(r'^settings/', include('askbot.deps.livesettings.urls')),
    url(r'^followit/', include('followit.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^messages/write/(?:(?P<recipients>[^/#]+)/)?$',
            WriteView.as_view(exchange_filter=postman_filters.postman_exchange_filter),
            name='write'),
    url(r'^messages/', include('postman.urls')),
    url(r'^robots.txt$', include('robots.urls')),
    url( # TODO: replace with django.conf.urls.static ?
        r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
        StaticViews.serve,
        {'document_root': settings.MEDIA_ROOT.replace('\\','/')},
    )
]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
                    url(r'^rosetta/', include('rosetta.urls')),
                ]

handler500 = 'askbot.views.error.internal_error'
