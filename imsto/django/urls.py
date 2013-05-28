from django.conf.urls import patterns, url

from handle import imagehandle, managehandle

urlpatterns = patterns('',
    url(r't/(.+)$', imagehandle),
    url(r'Manage/(.*)$', managehandle),
)
