from django.conf.urls import url
from . import views
from django.contrib import admin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView

admin.site.site_title = "Future Track Classes"
admin.site.site_header = "Future Track Classes"
admin.site.index_title = "Welcome Sir"

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^more$', views.index, name='index'),
    url(r'^memories$', views.memories, name='memories'),
    url(r'^notice$', views.notice, name='notice'),
    url(r'^registration$', views.registration, name='registration'),
    url(r'^accounts/login/$', views.loginPage, name='login'),
    url(r'^logout$', views.logoutPage, name='logout'),
    url(r'^importantpdf$', views.importantpdf, name='importantpdf'),
    url(r'^importantforms$', views.importantforms, name='importantforms'),
    url(r'^quiz$', views.quiz, name='quiz'),
    url(r'^mypapers$', views.mypapers, name='mypapers'),
    url(r'^paidpapers$', views.paidpapers, name='paidpapers'),
    url(r'^freepapers$', views.freepapers, name='freepapers'),
    url(r'^quiz/(?P<quiz_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^quiz/examkey/(?P<quiz_id>[0-9]+)$', views.examkey, name='examkey'),
    url(r'^quiz/question/(?P<quiz_id>[0-9]+)/$', views.question, name='question'),
    url(r'^quiz/timer/(?P<quiz_id>[0-9]+)/$', views.timer, name='timer'),
    url(r'^quiz/result/(?P<quiz_id>[0-9]+)/$', views.result, name='result'),
    url(r'^quiz/progress/$', views.progress, name='progress'),
    url(r'^quiz/progress/detail/(?P<quiz_id>[0-9]+)/$', views.progressdetail, name='detail'),
    url(r'^quiz/progress/rank/(?P<quiz_id>[0-9]+)/$', views.rank, name='rank'),
    url(r'^reset-password/$', PasswordResetView.as_view(template_name='home/password_reset.html')
        , name='reset_password'),

    url(r'^reset-password/done/$', PasswordResetDoneView.as_view(template_name='home/password_reset_done.html'),
        name='password_reset_done'),

    url(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(template_name='home/password_reset_confirm.html'),
        name='password_reset_confirm'),

    url(r'^reset-password/complete/$',
        PasswordResetCompleteView.as_view(template_name='home/password_reset_complete.html'),
        name='password_reset_complete'),
    url(r'^profile/$', views.view_profile, name='view_profile'),
    url(r'^updatecart/$', views.UpdateCart, name="UpdateCart"),
    url(r'^checkout/$', views.CheckOut, name="Checkout"),
    url(r'^handlerrequest/$', views.handlerequest, name="HandleRequest"),

]
