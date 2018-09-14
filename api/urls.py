from django.conf.urls import url, include
from .views.account import LoginView
from .views.course import CourseView
from .views.news import NewsView
from .views.shopping_car import ShoppingCarView
from .views.payment import PaymentView

urlpatterns = [
    url('account/login/$', LoginView.as_view(), name='login'),

    url('course/$', CourseView.as_view({'get':'list'}), name='course'),
    url('course/(?P<pk>\d+)/$', CourseView.as_view({'get':'retrieve'}), name='course_detail'),

    url('news/$', NewsView.as_view({'get':'list'}), name='news'),
    url('news/(?P<pk>\d+)/$', NewsView.as_view({'get':'retrieve'}), name='news_detail'),

    url('shopping_car/$', ShoppingCarView.as_view(), name='shopping_car'),

    url('payment/$', PaymentView.as_view(), name='payment'),
    # url('news/(?P<pk>\d+)/$', NewsView.as_view({'get':'retrieve'}), name='news_detail'),
]
