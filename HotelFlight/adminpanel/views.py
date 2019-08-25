from django.shortcuts import render
from .forms import *
from django.contrib import messages
from database.models import Hotel, Hotel_Room, Room
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from django.http import HttpResponseRedirect
from .models import Photos
from collections import namedtuple
from django.db import connection


def isHotel(user):
    return user.groups.filter(name='Hotel').exists()


def isAirlines(user):
    return user.groups.filter(name='Airlines').exists()


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def hoteladmindash(request):
    count = 0
    cursor = connection.cursor()
    cursor.execute("select distinct HB.Checkin_Date,HB.Checkout_Date,H.Hotel_Name,B.User_id,B.MoneyToPay,"
                   "(B.MoneyToPay-B.MoneyToRefund) as 'Paid',B.MoneyToRefund as 'Pending',HR.Room_id,HB.TotalRooms,"
                   "R.RoomType,R.SingleBedCount,R.DoubleBedCount,B.id as 'BookingID',H.CompanyAdmin_id as 'AdminID',"
                   "H.Address,H.Hotel_Location,H.Hotel_Country,U.first_name,U.last_name "
                   "from database_hotel_booking HB join database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join "
                   "database_booking B on(HB.Booking_id=B.id) join database_room R on (R.id=HR.Room_id) join "
                   "database_hotel H on(H.id=HR.Hotel_id) join database_cancellation_log CL on (B.id=CL.Booking_id) "
                   "join auth_user U on(U.id=B.User_id)"
                   "where HB.Checkin_Date>=CURRENT_DATE and CL.Admin_id=%s and CL.notified=0 "
                   "and DATETIME(B.DateOfBooking,'+10 day')>=date('now') order by HB.Checkin_Date,"
                   "HB.Checkout_Date,B.MoneyToPay", [request.user.id])
    data = namedtuplefetchall(cursor)
    for datum in data:
        count = count + 1
    return render(request, "adminpanel/hotelAdminDash.html", {'count': count, 'data': data})


def hoteladminnotifications(request):
    cursor = connection.cursor()
    cursor.execute("select distinct HB.Checkin_Date,HB.Checkout_Date,H.Hotel_Name,B.User_id,B.MoneyToPay,"
                   "(B.MoneyToPay-B.MoneyToRefund) as 'Paid',B.MoneyToRefund as 'Pending',HR.Room_id,HB.TotalRooms,"
                   "R.RoomType,R.SingleBedCount,R.DoubleBedCount,B.id as 'BookingID',H.CompanyAdmin_id as 'AdminID',"
                   "H.Address,H.Hotel_Location,H.Hotel_Country,U.first_name,U.last_name,CL.notified "
                   "from database_hotel_booking HB join database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join "
                   "database_booking B on(HB.Booking_id=B.id) join database_room R on (R.id=HR.Room_id) join "
                   "database_hotel H on(H.id=HR.Hotel_id) join database_cancellation_log CL on (B.id=CL.Booking_id) "
                   "join auth_user U on(U.id=B.User_id)"
                   "where HB.Checkin_Date>=CURRENT_DATE and CL.Admin_id=%s "
                   " and DATETIME(B.DateOfBooking,'+10 day')>=date('now') order by HB.Checkin_Date,"
                   "HB.Checkout_Date,B.MoneyToPay", [request.user.id])
    data = namedtuplefetchall(cursor)
    print(data)
    Cancellation_Log.objects.filter(Admin_id=request.user.id).update(notified=True)
    return render(request, "adminpanel/hotelNotifications.html", {'data': data})


def hoteladminbookings(request):
    hotel = Hotel.objects.get(CompanyAdmin=request.user.id)
    cursor = connection.cursor()
    cursor.execute(
        "select distinct HB.Checkin_Date,HB.Checkout_Date,B.User_id,U.first_name,U.last_name,U.email,P.Phone,"
        "P.Address,B.MoneyToPay,(B.MoneyToPay-B.MoneyToRefund) as 'Paid',B.MoneyToRefund as 'Pending',"
        "HR.Room_id,HB.TotalRooms,R.RoomType,R.SingleBedCount,R.DoubleBedCount from database_hotel_booking HB "
        "join database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) "
        "join auth_user U on(U.id=B.User_id) join database_profile P on(P.user_id=U.id) join database_room R "
        "on (R.id=HR.Room_id) where HB.Checkin_Date>=CURRENT_DATE and HR.Hotel_id=%s and B.isCancelled=0 "
        "order by HB.Checkin_Date desc,HB.Checkout_Date,B.MoneyToPay", [hotel.id])
    data = namedtuplefetchall(cursor)
    return render(request, "adminpanel/hotelAdminBookings.html", {'data': data})


def hoteladminbookingstoday(request):
    hotel = Hotel.objects.get(CompanyAdmin=request.user.id)
    date = request.GET.get("date", "CURRENT_DATE")
    print(date)
    cursor = connection.cursor()
    cursor.execute(
        "select distinct HB.Checkin_Date,HB.Checkout_Date,B.User_id,U.first_name,U.last_name,U.email,P.Phone,"
        "P.Address,B.MoneyToPay,(B.MoneyToPay-B.MoneyToRefund) as 'Paid',B.MoneyToRefund as 'Pending',"
        "HR.Room_id,HB.TotalRooms,R.RoomType,R.SingleBedCount,R.DoubleBedCount from database_hotel_booking HB "
        "join database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) "
        "join auth_user U on(U.id=B.User_id) join database_profile P on(P.user_id=U.id) join database_room R "
        "on (R.id=HR.Room_id) where HB.Checkin_Date>=CURRENT_DATE and HR.Hotel_id=%s and B.isCancelled=0 "
        "order by HB.Checkin_Date desc,HB.Checkout_Date,B.MoneyToPay", [hotel.id])
    data = namedtuplefetchall(cursor)
    for dd in data:
        print(dd)
    return render(request, "adminpanel/hotelAdminBookingsToday.html", {'data': data})


def hoteladminaddroom(request):
    if request.method == "POST":
        imageform = photoupload(request.POST, request.FILES)
        addroomform = HotelAddRoomForm(request.POST)
        files = request.FILES.getlist('file')
        if addroomform.is_valid() and imageform.is_valid():
            try:
                Hotel_Room.objects.get(Hotel=Hotel.objects.get(CompanyAdmin=request.user.id),
                                       Room=Room.objects.get(pk=int(addroomform.cleaned_data['room'])))
                return HttpResponseRedirect(
                    '/adminHotelRoomSingle?roomID=' + addroomform.cleaned_data['room'] + '&msg=F')
            except Hotel_Room.DoesNotExist:
                hotelRoom = Hotel_Room(Price=addroomform.cleaned_data['price'],
                                       Complimentary_Breakfast=addroomform.cleaned_data['breakfast'],
                                       Wifi=addroomform.cleaned_data['wifi'],
                                       Hotel=Hotel.objects.get(CompanyAdmin=request.user.id),
                                       Room=Room.objects.get(pk=addroomform.cleaned_data['room']),
                                       FreeRoomCount=addroomform.cleaned_data['roomCount'],
                                       TotalRoomCount=addroomform.cleaned_data['roomCount'])
                hotelRoom.save()
                for f in files:
                    photosinstance = Photos(file=f, roomid=addroomform.cleaned_data['room'],
                                            userid=request.user.id)
                    photosinstance.save()
                return HttpResponseRedirect(
                    '/adminHotelRoomSingle?roomID=' + addroomform.cleaned_data['room'] + '&msg=S')
        else:
            messages.error(request, 'Invalid input', extra_tags='alert-danger')

    else:
        imageform = photoupload()
        addroomform = HotelAddRoomForm()
    return render(request, "adminpanel/hotelAdminAddRoom.html", {'imageform': imageform, 'addroomform': addroomform})


def hoteladminroomsingle(request):
    removeImage = request.GET.get('img', '');
    roomID = request.GET.get('roomID', '1');
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    userf = 'user_' + str(request.user.id)
    roomf = 'room_' + str(roomID)
    root = os.path.join(root, 'HotelFlight/static/media/' + userf + '/' + roomf)
    if removeImage != '':
        os.remove(os.path.join(root, removeImage))
        return HttpResponseRedirect('/adminHotelRoomSingle?roomID=' + roomID)
    room = Hotel_Room.objects.get(Hotel=Hotel.objects.get(CompanyAdmin=request.user.id),
                                  Room=Room.objects.get(pk=int(roomID)))
    roomtype = Room.objects.get(pk=int(roomID))
    roomtype = roomtype.RoomType + '   Single Bed:' + str(roomtype.SingleBedCount) + '   Double Bed:' + str(
        roomtype.DoubleBedCount) + '   AC:' + str(roomtype.AirConditioner)
    if request.method == 'POST':
        imageform = photoupload(request.POST, request.FILES)
        updateroomform = HotelUpdateRoom(request.POST)
        files = request.FILES.getlist('file')
        if imageform.is_valid():
            for f in files:
                photosinstance = Photos(file=f, roomid=imageform.cleaned_data['roomid'],
                                        userid=imageform.cleaned_data['userid'])
                photosinstance.save()
            messages.success(request, 'File(s) uploaded successfully', extra_tags='alert-success')
        if updateroomform.is_valid():
            print(updateroomform.cleaned_data['wifi'])
            print(updateroomform.cleaned_data['breakfast'])
            room.Wifi = updateroomform.cleaned_data['wifi']
            room.Complimentary_Breakfast = updateroomform.cleaned_data['breakfast']
            room.Price = updateroomform.cleaned_data['price']
            extra = updateroomform.cleaned_data['roomCount'] - room.TotalRoomCount
            if extra != 0:
                room.FreeRoomCount += extra
                room.TotalRoomCount += extra
            room.save()
            messages.success(request, 'Updated successfully', extra_tags='alert-success')
    else:
        imageform = photoupload()
        updateroomform = HotelUpdateRoom()
        updateroomform.fields['wifi'].initial = room.Wifi
        updateroomform.fields['breakfast'].initial = room.Complimentary_Breakfast
    imagelist = os.listdir(root)
    return render(request, "adminpanel/hotelAdminRoomSingle.html",
                  {'imagelist': imagelist, 'count': len(imagelist), 'imageform': imageform, 'room': room,
                   'updateRoomForm': updateroomform, 'roomtype': roomtype})


def hoteladminrooms(request):
    rooms = Hotel_Room.objects.all().filter(Hotel=Hotel.objects.get(CompanyAdmin=request.user.id))
    return render(request, "adminpanel/hotelAdminRooms.html", {'rooms': rooms})


@login_required(login_url='login')
@user_passes_test(isHotel, login_url='login')
def hoteladminupdate(request):
    hotel = Hotel.objects.get(CompanyAdmin=request.user.id)
    if request.method == "POST":
        updateForm = hotelupdateform(request.POST)
        if updateForm.is_valid():
            hotel.Hotel_Name = updateForm.cleaned_data['name']
            hotel.Phone = updateForm.cleaned_data['phone']
            hotel.Address = updateForm.cleaned_data['address']
            hotel.Hotel_Location = updateForm.cleaned_data['location']
            hotel.Hotel_Country = updateForm.cleaned_data['country']
            hotel.save()
            messages.success(request, 'Updated successfully', extra_tags='alert-success')
        else:
            messages.error(request, 'Invalid input', extra_tags='alert-danger')
    else:
        updateForm = hotelupdateform()
    return render(request, "adminpanel/hotelAdminUpdate.html", {'form': updateForm, 'hotel': hotel})


def hoteladmincalender(request):
    hotel = Hotel.objects.get(CompanyAdmin=request.user.id)
    cursor = connection.cursor()
    cursor.execute(
        "select distinct HB.Checkin_Date,HB.Checkout_Date,B.User_id,U.first_name,U.last_name,U.email,P.Phone,"
        "P.Address,B.MoneyToPay,(B.MoneyToPay-B.MoneyToRefund) as 'Paid',B.MoneyToRefund as 'Pending',"
        "HR.Room_id,HB.TotalRooms,R.RoomType,R.SingleBedCount,R.DoubleBedCount from database_hotel_booking HB "
        "join database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) "
        "join auth_user U on(U.id=B.User_id) join database_profile P on(P.user_id=U.id) join database_room R "
        "on (R.id=HR.Room_id) where HB.Checkin_Date>=CURRENT_DATE and HR.Hotel_id=%s and B.isCancelled=0 "
        "order by HB.Checkin_Date,HB.Checkout_Date,B.MoneyToPay", [hotel.id])
    data = namedtuplefetchall(cursor)
    for datum in data:
        print(datum.first_name)
    return render(request, "adminpanel/hotelAdminCalender.html", {'data': data})


def airlinesadmindash(request):
    return render(request, "adminpanel/airlinesAdminDash.html")


def airlinesadminbookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT U.first_name || ' ' || U.last_name as 'name',U.email as 'email',P.Phone as 'phn',F.Airplane_Number as 'airplanenumber',B.DateOfBooking as 'dob',FR.Date as 'dof',(FR.Price*FB.TotalSeats - B.MoneyToPay) as 'Paid',B.MoneyToRefund as 'Pending', FB.TotalSeats as 'seats' "
        "FROM database_flight_booking FB JOIN database_booking B ON (B.id = FB.Booking_id) "
        "JOIN database_flight_route FR ON (FR.id = FB.Flight_id) "
        "JOIN database_flight F ON (F.id = FR.Flight_id) "
        "JOIN database_air_company A ON (F.AirCompany_id = A.id) "
        "JOIN auth_user U on (U.id = B.user_id) "
        "JOIN database_profile P on(P.user_id=U.id) "
        "WHERE A.CompanyAdmin_id = %s "
        "", [request.user.id])
    data = namedtuplefetchall(cursor)
    print("Data is printing .........................")
    for datum in data:
        print(datum.seats)
    # return render(request,"adminpanel/airlinesAdminDash.html")
    return render(request, "adminpanel/airlinesAdminBookings.html", {'data': data})


def airlinesadminaddroute(request):
    if request.method == "POST":
        addrouteform = FlightAddRouteForm(request.POST)
        if addrouteform.is_valid():
            source = addrouteform.cleaned_data['Source']
            destination = addrouteform.cleaned_data['Destination']
            try:
                Route.objects.get(Source=source, Destination=destination)
                print("already present" + source + destination)
                messages.success(request, 'Route already present', extra_tags='alert-danger')

            except Route.DoesNotExist:
                print("route does not exist")
                route = Route(Source=source, Destination=destination)
                route.save()
                messages.success(request, 'Route added successfully', extra_tags='alert-success')
        else:
            messages.error(request, 'Invalid input', extra_tags='alert-danger')
    else:
        addrouteform = FlightAddRouteForm()
    return render(request, "adminpanel/airlinesAdminAddRoute.html", {'addrouteform': addrouteform})


def airlinesadminaddflightroute(request):
    print(request.user.id)
    if request.method == "POST":
        addflightrouteform = FlightAddFlightRoute(request.POST, my_arg=request.user.id)
        if addflightrouteform.is_valid():
            print("yes")
            id1 = int(addflightrouteform.cleaned_data['Route'])
            id2 = int(addflightrouteform.cleaned_data['Flight'])
            id3 = int(addflightrouteform.cleaned_data['Cancellation_Policy'])
            date = addflightrouteform.cleaned_data['Date']
            time = addflightrouteform.cleaned_data['Time']
            route = Route.objects.filter(pk=id1)
            for row in route:
                print(row)
            print(id1)
            print(id2)
            print(date)
            print(time)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM database_flight_route FR JOIN database_flight F ON(FR.Flight_id = F.id) "
                           "JOIN database_route R ON (R.id = FR.Route_id) JOIN database_cancellation_policy CP ON (CP.id=FR.Cancellation_Policy_id) WHERE F.id = %s AND R.id = %s AND FR.Date = %s  AND CP.id = %s"
                           "", [id2, id1, date, id3])
            results = cursor.fetchone()
            if not results:
                flight_route = Flight_Route(Route=Route.objects.get(pk=id1),
                                            Cancellation_Policy=Cancellation_Policy.objects.get(pk=id3),
                                            Flight=Flight.objects.get(pk=id2), Time=time, Date=date,
                                            Price=addflightrouteform.cleaned_data['Price'],
                                            Duration=addflightrouteform.cleaned_data['Duration'],
                                            Source_Airport=addflightrouteform.cleaned_data['Source_Airport'],
                                            Destination_Airport=addflightrouteform.cleaned_data['Destination_Airport'],
                                            TotalSeatsBooked=0)

                flight_route.save()
                messages.error(request, 'Flight added successfully', extra_tags='alert-success')
            else:
                messages.error(request, 'Flight already present', extra_tags='alert-danger')
        else:
            messages.error(request, 'Invalid input', extra_tags='alert-danger')
    else:
        addflightrouteform = FlightAddFlightRoute(my_arg=request.user.id)
    return render(request, "adminpanel/airlinesAdminAddFlightRoute.html", {'addflightrouteform': addflightrouteform})


def airlinesadminflights(request):
    flights = Flight.objects.all().filter(AirCompany=Air_Company.objects.get(CompanyAdmin=request.user.id))
    return render(request, "adminpanel/airlinesAdminFlights.html", {'flights': flights})


def airlinesadminflightsingle(request):
    id = request.GET.get('flightID', '')
    flight = Flight.objects.get(pk=id)
    if request.method == "POST":
        updateForm = FlightUpdateForm(request.POST)
        if updateForm.is_valid():
            flight.TotalSeats = updateForm.cleaned_data['TotalSeats']
            flight.save()
            messages.success(request, 'Updated successfully', extra_tags='alert-success')
        else:
            messages.error(request, 'Invalid input', extra_tags='alert-danger')

    else:
        updateForm = FlightUpdateForm()
    return render(request, "adminpanel/airlinesAdminFlightSingle.html", {'form': updateForm, 'flight': flight})


def airlinesadminaddflight(request):
    adminid = request.user.id
    if request.method == "POST":
        addflightform = FlightAddFlight(request.POST)
        if addflightform.is_valid():
            airplanenumber = addflightform.cleaned_data['AirplaneNumber']
            aircraft = addflightform.cleaned_data['Aircraft']
            totalseats = addflightform.cleaned_data['TotalSeats']
            try:
                Flight.objects.get(AirCompany=Air_Company.objects.get(CompanyAdmin_id=adminid),
                                   Airplane_Number=airplanenumber)
                messages.error(request, 'Flight already exists', extra_tags='alert-danger')
            except Flight.DoesNotExist:
                print("does not exist")
                flight = Flight(Airplane_Number=airplanenumber, Aircraft=aircraft, TotalSeats=totalseats,
                                Air_Company=Air_Company.objects.get(CompanyAdmin=adminid))
                flight.save()
                messages.success(request, 'Added successfully', extra_tags='alert-success')
        else:
            messages.error(request, 'Invalid input', extra_tags='alert-danger')

    else:
        addflightform = FlightAddFlight()
    return render(request, "adminpanel/airlinesAdminAddFlight.html", {'addflightform': addflightform})


def airlinesadmincalendar(request):
    cursor = connection.cursor()

    cursor.execute(
        "SELECT F.Airplane_Number as 'airplanenumber',B.DateOfBooking as 'dob',FR.Date as 'dof', sum(FB.TotalSeats) as 'seats' "
        "FROM database_flight_booking FB JOIN database_booking B ON (B.id = FB.Booking_id) "
        "JOIN database_flight_route FR ON (FR.id = FB.Flight_id) "
        "JOIN database_flight F ON (F.id = FR.Flight_id) "
        "JOIN database_air_company A ON (F.AirCompany_id = A.id) "
        "WHERE A.CompanyAdmin_id = %s "
        "GROUP BY B.DateOfBooking,FR.Date", [request.user.id])
    data = namedtuplefetchall(cursor)
    print("Data is printing .........................")
    for datum in data:
        print(datum.seats)
    # return render(request,"adminpanel/airlinesAdminDash.html")
    return render(request, "adminpanel/airlinesAdminCalendar.html", {'data': data})
