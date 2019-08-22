from django.urls import path
from . import views

urlpatterns = [
    path('adminHotelDash', views.hoteladmindash, name='hotelAdminDash'),
    path('adminHotelUpdate', views.hoteladminupdate, name='hotelAdminUpdate'),
    path('adminHotelRooms', views.hoteladminrooms, name='hotelAdminRooms'),
    path('adminHotelRoomSingle', views.hoteladminroomsingle, name='hotelAdminRoomSingle'),
    path('adminHotelAddRoom', views.hoteladminaddroom, name='hotelAdminAddRoom'),
    path('adminHotelBookings', views.hoteladminbookings, name='hotelAdminBookings'),
    path('adminHotelCalender', views.hoteladmincalender, name='hotelAdminCalender'),
    path('adminAirlinesDash', views.airlinesadmindash, name='airlinesAdminDash'),
    path('adminAirlinesAddRoute', views.airlinesadminaddroute, name='airlinesAdminAddRoute'),
    path('adminAirlinesAddFlightRoute', views.airlinesadminaddflightroute, name='airlinesAdminAddFlightRoute'),
    path('adminAirlinesViewFlights', views.airlinesadminflights, name='airlinesAdminViewFlights'),
    path('adminAirlinesUpdateFlights', views.airlinesadminflightsingle, name='airlinesAdminFlightSingle'),
    path('adminAirlinesAddFlight', views.airlinesadminaddflight, name='airlinesAdminAddFlight'),
    path('airlinesAdminCalendar', views.airlinesadmincalendar, name='airlinesAdminCalendar'),
    path('airlinesAdminBookings', views.airlinesadminbookings, name='airlinesAdminBookings')
]
