from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import SearchHotelForm, SearchFlightForm
from django.db import connection
from django.core.paginator import Paginator
from collections import namedtuple
import os


# Create your views here.


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def homepage(request):
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    return render(request, "search/homepage.html", {'hotelform': hotelform, 'flightform': flightform})


def searchHotelPage(request):
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    dest = request.GET.get('hoteldest', '')
    checkin = request.GET.get('checkin', '')
    checkout = request.GET.get('checkout', '')
    roomcount = request.GET.get('room', '')
    adultcount = request.GET.get('adult', '')
    dest = '%' + dest + '%'
    roomcount = int(roomcount)
    cursor = connection.cursor()
    cursor.execute("SELECT H.Hotel_Name,H.Address,H.Hotel_Location,H.Hotel_Country,H.Description,sum(HR.FreeRoomCount)"
                   " as 'Num', min(HR.Price)*%s as 'Price', H.CompanyAdmin_id as ID , H.id as HID  FROM "
                   "database_hotel_room HR  join database_hotel H on(HR.Hotel_id=H.id) where (lower(H.Hotel_Name) "
                   "Like %s OR lower(H.Hotel_Location) Like %s OR lower(H.Hotel_Country) Like %s OR "
                   "lower(H.Address) Like %s) GROUP BY H.Hotel_Name HAVING Num >= %s",
                   [roomcount, dest, dest, dest, dest, roomcount])
    hotels = namedtuplefetchall(cursor)
    # paginator = Paginator(data, 5)
    # page = request.GET.get('page')
    # hotels = paginator.get_page(page)
    return render(request, "search/searchHotel.html",
                  {'hotelform': hotelform, 'flightform': flightform, 'hotels': hotels})


# @login_required(login_url='/login/')
def hotelrooms(request):
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    dest = request.GET.get('hoteldest', '')
    checkin = request.GET.get('checkin', '')
    checkout = request.GET.get('checkout', '')
    roomcount = request.GET.get('room', '')
    adultcount = request.GET.get('adult', '')
    hid = request.GET.get('hid', '')
    huid = request.GET.get('huid', '')
    dest = '%' + dest + '%'
    roomcount = int(roomcount)
    hid = int(hid)
    huid = int(huid)
    cursor = connection.cursor()
    cursor.execute("select H.Hotel_Name,H.Address,H.Hotel_Location,H.Hotel_Country,H.Description,H.CompanyAdmin_id "
                   "as 'uid',H.id as 'hid' from database_hotel H WHERE H.id=%s",
                   [hid])
    hotel = namedtuplefetchall(cursor)
    hotelRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    userf = 'user_' + str(hotel[0].uid)
    hotelRoot = os.path.join(hotelRoot, 'HotelFlight/static/media/' + userf + '/main')
    imageList = os.listdir(hotelRoot)
    cursor.execute("select R.SingleBedCount,R.DoubleBedCount,R.RoomType,R.AirConditioner,HR.Price*%s as 'Price',"
                   "HR.Complimentary_Breakfast,HR.wifi,HR.FreeRoomCount as 'cnt',HR.Hotel_id as 'hotelID',"
                   " HR.Room_id as 'roomID',hr.ID as 'hrID' from database_room R join database_hotel_room HR "
                   "on (R.id=HR.Room_id) where HR.Hotel_id=%s and cnt>=%s group by HR.Hotel_id,R.id ",
                   [roomcount, hid, roomcount])
    rooms = namedtuplefetchall(cursor)
    return render(request, "search/hotelRooms.html",
                  {'hotelform': hotelform, 'flightform': flightform, 'hotel': hotel[0], 'rooms': rooms,
                   'imageList': imageList})


def searchFlightPage(request):
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    source = request.GET.get('source', '')
    dest = request.GET.get('dest', '')
    depart = request.GET.get('depart', '')
    adultcount = request.GET.get('adult', '')
    childrenCount = request.GET.get('children', '')
    cursor = connection.cursor()
    # single stop
    cursor.execute("SELECT R.Source, R.Destination, FR.Source_Airport, FR.Destination_Airport, FR.Date, FR.Time, "
                   "FR.Duration, FR.Price, A.AirCompany_Name, F.Aircraft, F.Airplane_Number FROM database_route R "
                   "JOIN database_flight_route FR ON R.id = FR.Route_id "
                   "JOIN database_flight F ON F.id = FR.Flight_id "
                   "JOIN database_air_company A ON F.AirCompany_id=A.id "
                   "WHERE R.Source=%s AND R.Destination=%s AND FR.Date=%s",
                   [source, dest, depart])
    ssflights = namedtuplefetchall(cursor)
    # multi stop
    cursor.execute("SELECT T.Source, T.Source_Airport as 'SrcAirport' , T.Destination as 'Intermediate', "
                   "T.Destination_Airport as 'InterAirport', S.Destination, S.Destination_Airport as 'DestAirport',"
                   " T.Date, T.AirCompany_Name as 'SrcCompany', T.Aircraft as 'SrcAircraft', "
                   "T.Airplane_Number as 'SrcAirNo', T.Time as 'SrcTime', T.Duration as 'SrcDuration', "
                   "S.AirCompany_Name as 'DestCompany', S.Aircraft as 'DestAircraft', S.Airplane_Number as 'DestAirNo',"
                   " S.Time as 'DestTime', S.Duration as 'DestDuration',"
                   " ((strftime('%%H',S.Time)*60+strftime('%%M',S.Time))- "
                   "strftime('%%H',T.Time)*60-strftime('%%M',T.Time)-T.Duration) as 'TimeDiff',"
                   "T.Price as 'firstPrice',S.Price 'secondPrice' "
                   "FROM (SELECT * FROM database_route R JOIN database_flight_route FR ON R.id = FR.Route_id "
                   "JOIN database_flight F ON F.id = FR.Flight_id JOIN database_air_company A "
                   "ON F.AirCompany_id=A.id WHERE R.Source = %s AND FR.Date=%s) T "
                   "JOIN (SELECT * FROM database_route R JOIN database_flight_route FR ON R.id = FR.Route_id "
                   "JOIN database_flight F ON F.id = FR.Flight_id JOIN database_air_company A ON F.AirCompany_id=A.id"
                   " where R.Destination=%s) S ON S.Source = T.Destination "
                   "WHERE T.SOURCE = %s AND S.Destination = %s AND T.Date=S.Date AND "
                   "(strftime('%%H', T.Time)*60 + strftime('%%M', T.Time) + 30 + T.Duration) < "
                   "(strftime('%%H', S.Time)*60 + strftime('%%M', S.Time))", [source, depart, dest, source, dest])
    msflights = namedtuplefetchall(cursor)
    return render(request, "search/flighttest.html",
                  {'hotelform': hotelform, 'flightform': flightform, 'ssflights': ssflights, 'msflights': msflights})
