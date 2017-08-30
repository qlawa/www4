from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    url(r'^api/kraj/$', views.kraj_json, name='dr_index'),
    url(r'^api/wojewodztwo/(?P<wojewodztwo_nr>[0-9]+)$', views.wojewodztwo_json, name='dr_wojewodztwo'),
    url(r'^api/kandydaci/$', views.kandydaci_json, name='kandydaci_json'),
    url(r'^api/okreg/(?P<okreg_nr>[0-9]+)$', views.okreg_json, name='dr_okreg'),
    url(r'^api/gmina/(?P<gmina_nr>[0-9]+)$', views.gmina_json, name='dr_gmina'),
    url(r'^api/szukaj/(?P<nazwa>\w+)$', views.szukaj_gminy_json, name='dr_szukaj_gminy'),
    url(r'^api/obwod/(?P<obwod_id>[0-9]+)$', views.edycja_json, name='dr_edycja'),
    url(r'^api/statystyki/(?P<obwod_id>[0-9]+)$', views.statystyka_json, name='dr_staty'),
    url(r'^api/login/$', views.rest_login, name='dr_login'),

    url(r'^$', views.kraj, name='kraj'),
    url(r'^login/$', views.new_login, name='login'),


    # #url(r'^login/$', views.login_view, name='login'),
    # url(r'^logout/$', views.logout_view, name='logout'),
    #
    # url(r'^wojewodztwo/(?P<wojewodztwo_nr>[0-9]+).html$', views.wojewodztwo, name='wojewodztwo'),
    # url(r'^okreg/(?P<okreg_nr>[0-9]+).html$', views.okreg, name='okreg'),
    # url(r'^gmina/(?P<gmina_nr>[0-9]+).html$', views.gmina, name='gmina'),
    #
    #
    # url(r'^edycja/(?P<g>[0-9]+)/(?P<o>[0-9]+)$', views.edycja, name='edycja'),


]
