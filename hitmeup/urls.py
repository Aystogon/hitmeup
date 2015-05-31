from django.conf.urls import include, url
from django.contrib import admin
from django_jinja import views as jinja_views
from user_accounts.api import UserProfileResource, FriendResource
from ourcalendar.api import EventResource
from notifications.api import NotificationResource

handler400 = jinja_views.BadRequest.as_view()
handler403 = jinja_views.PermissionDenied.as_view()
handler404 = jinja_views.PageNotFound.as_view()
handler500 = jinja_views.ServerError.as_view()
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'hitmeup.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # REST APIs
    url(r'^api/friends/', include(FriendResource.urls(),
        namespace='friends_api')),
    url(r'^api/users/', include(UserProfileResource.urls(),
        namespace='users_api')),
    url(r'^api/notifications/', include(NotificationResource.urls(),
        namespace='notifications_api')),
    url(r'^api/events/', include(EventResource.urls(),
        namespace='events_api')),


    # Other URLs
    url(r'^admin/', include(admin.site.urls)),
    url(r'^notifications/', include('notifications.urls', namespace='notifications')),
    url(r'^sync/', include('triton_sync.urls', namespace='triton_sync')),
    url(r'^', include('static_pages.urls', namespace='static_pages')),
    url(r'^', include('user_accounts.urls', namespace='user_accounts')),
    url(r'^calendar/', include('ourcalendar.urls', namespace='calendar')),
    url(r'^sudowoodo_login_fb/', include('fb_login.urls', namespace='fb_login')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^facebook/', include('django_facebook.urls')),
]
