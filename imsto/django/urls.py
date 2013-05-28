from django.conf.urls import patterns, url

from handle import ImageHandle, ManageHandle

urlpatterns = patterns('',
    url(r'^t/(.+)$', ImageHandle),
    url(r'^Manage/(.*)$', ManageHandle),
)
