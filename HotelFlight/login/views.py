from django.shortcuts import render
from .forms import ProfileForm, UserCreateForm, UpdateProfileForm
from django.http import HttpResponseRedirect
from django.contrib import auth, messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.models import User
from database import models
from django.db import connection
from collections import namedtuple
from database.models import *
from django.contrib.auth.forms import PasswordChangeForm


# Create your views here.
def isHotel(user):
    return user.groups.filter(name='Hotel').exists()


def isFlight(user):
    return user.groups.filter(name='Flight').exists()


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def login(request):
    redirectTo = request.GET.get('next', '')
    if request.method == 'POST':
        username = request.POST.get("username", "")
        password = request.POST.get("pass", "")
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            if isHotel(user):
                return HttpResponseRedirect('/adminHotelDash')
            elif isFlight(user):
                return HttpResponseRedirect('/adminAirlinesDash')
            elif user.is_superuser:
                return HttpResponseRedirect('/adminDash')
            return HttpResponseRedirect(redirectTo)
        else:
            messages.error(request, 'Username or password not correct')
    return render(request, "login/login.html")


def reg(request):
    if request.method == 'POST':
        userForm = UserCreateForm(request.POST)
        profileForm = ProfileForm(request.POST)
        if userForm.is_valid() and profileForm.is_valid():
            user = userForm.save()
            profile = profileForm.save(commit=False)
            profile.user = user
            profile.save()
            return HttpResponseRedirect('/login?next=/')
        else:
            print(userForm.errors)
    else:
        userForm = UserCreateForm()
        profileForm = ProfileForm()
    return render(request, "login/reg.html", {'userForm': userForm, 'profileForm': profileForm})


def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/')


def userbookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "select distinct HB.Checkin_Date,HB.Checkout_Date,H.Hotel_Name,B.User_id,HR.Price*HB.TotalRooms as 'Price',"
        "(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation',"
        "HR.Room_id,HB.TotalRooms as 'TotalRooms', R.RoomType,R.SingleBedCount,R.DoubleBedCount,B.id as 'BookingID',"
        "H.CompanyAdmin_id as 'AdminID', H.Address,H.Hotel_Location,H.Hotel_Country,'+'||CP.DaysCount||' day' "
        "as 'datestr', date('now') as 'Today',B.Status from database_hotel_booking HB join database_hotel_room HR "
        "on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) join database_room R on "
        "(R.id=HR.Room_id) join database_hotel H on(H.id=HR.Hotel_id) join database_cancellation_policy CP on "
        "(HR.Cancellation_Policy_id=CP.id) where HB.Checkin_Date>=CURRENT_DATE and B.User_id=%s"
        " and DATETIME(B.DateOfBooking,datestr)>=date('now') order by HB.Checkin_Date,"
        "HB.Checkout_Date,B.MoneyToPay", [request.user.id])
    data = namedtuplefetchall(cursor)
    # notification data
    cursor = connection.cursor()
    cursor.execute(
        "select H.Hotel_Name,H.Hotel_Location,R.RoomType,HB.Checkin_Date,HB.Checkout_Date,HB.TotalRooms,B.PaidMoney,"
        "B.MoneyToPay,B.MoneyToRefund,BL.Message,BL.notified,B.Status from database_hotel_booking HB join "
        "database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) "
        "join database_room R on (R.id=HR.Room_id) join database_hotel H on(H.id=HR.Hotel_id) join database_bookinglog"
        " BL on (B.id=BL.Booking_id) join auth_user U on(U.id=B.User_id) where BL.Actor=0 and  B.User_id=%s and "
        "BL.notified=0 order by BL.notified,HB.Checkin_Date,HB.Checkout_Date,B.MoneyToPay", [request.user.id])
    dataHotel = namedtuplefetchall(cursor)
    cursor.execute(
        "SELECT DISTINCT BL.Message,BL.notified,B.Status,B.id as 'bookingid',B.User_id,FR.Price*FB.TotalSeats as "
        "'Price', FB.TotalSeats as 'TotalSeats',A.AirCompany_Name as 'AirCompany_Name',F.Airplane_Number as 'Plane', "
        "F.Aircraft as 'Model', FR.Time as 'Time',FR.Date as 'DOF', B.DateOfBooking as 'DOB',(B.PaidMoney) as 'Paid',"
        "B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation','+'||CP.DaysCount||' day' "
        "as 'datestr', FR.Source_Airport ||','||R.Source as 'SRC' , FR.Destination_Airport||','||R.Destination "
        "as 'DEST', FR.Duration as 'Duration' FROM database_flight_booking FB JOIN database_booking B ON "
        "(FB.Booking_id=B.id) JOIN database_bookinglog BL on (B.id=BL.Booking_id) JOIN database_flight_route FR ON "
        "(FB.Flight_id = FR.id) JOIN database_flight F ON (FR.Flight_id = F.id) JOIN database_air_company A ON "
        "(F.AirCompany_id = A.id) JOIN database_cancellation_policy CP ON (CP.id = FR.Cancellation_Policy_id) JOIN "
        "database_route R ON (R.id = FR.Route_id) WHERE B.User_id = %s and BL.notified=0 and "
        "BL.Actor=0  order by B.DateOfBooking,FR.Date", [request.user.id])
    dataFlight = namedtuplefetchall(cursor)
    # notifications count
    count = BookingLog.objects.filter(Actor=0, notified=0, Booking__User=request.user).count()
    return render(request, "login/userBookings.html",
                  {'data': data, 'count': count, 'dataHotel': dataHotel, 'dataFlight': dataFlight})


def usernotifications(request):
    cursor = connection.cursor()
    cursor.execute(
        "select H.Hotel_Name,H.Hotel_Location,R.RoomType,HB.Checkin_Date,HB.Checkout_Date,HB.TotalRooms,B.PaidMoney,"
        "B.MoneyToPay,B.MoneyToRefund,BL.Message,BL.notified,B.Status from database_hotel_booking HB join "
        "database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) "
        "join database_room R on (R.id=HR.Room_id) join database_hotel H on(H.id=HR.Hotel_id) join database_bookinglog"
        " BL on (B.id=BL.Booking_id) join auth_user U on(U.id=B.User_id) where BL.Actor=0 and  B.User_id=%s order by "
        "BL.notified,HB.Checkin_Date,HB.Checkout_Date,B.MoneyToPay", [request.user.id])
    data = namedtuplefetchall(cursor)
    cursor.execute(
        "SELECT DISTINCT BL.Message,BL.notified,B.Status,B.id as 'bookingid',B.User_id,FR.Price*FB.TotalSeats as "
        "'Price', FB.TotalSeats as 'TotalSeats',A.AirCompany_Name as 'AirCompany_Name',F.Airplane_Number as 'Plane', "
        "F.Aircraft as 'Model', FR.Time as 'Time',FR.Date as 'DOF', B.DateOfBooking as 'DOB',(B.PaidMoney) as 'Paid',"
        "B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation','+'||CP.DaysCount||' day' "
        "as 'datestr', FR.Source_Airport ||','||R.Source as 'SRC' , FR.Destination_Airport||','||R.Destination "
        "as 'DEST', FR.Duration as 'Duration' FROM database_flight_booking FB JOIN database_booking B ON "
        "(FB.Booking_id=B.id) JOIN database_bookinglog BL on (B.id=BL.Booking_id) JOIN database_flight_route FR ON "
        "(FB.Flight_id = FR.id) JOIN database_flight F ON (FR.Flight_id = F.id) JOIN database_air_company A ON "
        "(F.AirCompany_id = A.id) JOIN database_cancellation_policy CP ON (CP.id = FR.Cancellation_Policy_id) JOIN "
        "database_route R ON (R.id = FR.Route_id) WHERE B.User_id = %s and "
        "BL.Actor=0  order by B.DateOfBooking,FR.Date", [request.user.id])
    data1 = namedtuplefetchall(cursor)
    BookingLog.objects.filter(Booking__User=request.user).update(notified=True)
    return render(request, "login/userNotifications.html", {'data': data, 'data1': data1})


def bookingcancel(request):
    bookingID = request.GET.get('bid', '1')
    bookingID = int(bookingID)
    cursor = connection.cursor()
    HotelBooking = Hotel_Booking.objects.get(Booking=Booking.objects.get(pk=bookingID))
    HotelRoom = Hotel_Room.objects.get(pk=HotelBooking.Hotel_Room_id)
    CancellationPolicy = Cancellation_Policy.objects.get(pk=HotelRoom.Cancellation_Policy_id)
    datestr = '+' + str(CancellationPolicy.DaysCount) + ' day'
    cursor.execute(
        "select distinct HB.Checkin_Date,HB.Checkout_Date,H.Hotel_Name,B.User_id,HR.Price*HB.TotalRooms as 'Price',"
        "(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation', "
        "HR.Room_id,HB.TotalRooms as 'TotalRooms',R.RoomType,R.SingleBedCount,R.DoubleBedCount,B.id as 'BookingID',"
        "H.CompanyAdmin_id as 'AdminID',H.Address,H.Hotel_Location,H.Hotel_Country from database_hotel_booking HB "
        "join database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) join "
        "database_room R on (R.id=HR.Room_id) join database_hotel H on(H.id=HR.Hotel_id) where "
        "HB.Checkin_Date>=CURRENT_DATE and B.id=%s and DATETIME(B.DateOfBooking,%s)>=date('now')"
        " order by HB.Checkin_Date,HB.Checkout_Date,B.MoneyToPay", [bookingID, datestr])
    data = namedtuplefetchall(cursor)
    # notifications count
    count = BookingLog.objects.filter(Actor=0, notified=0, Booking__User=request.user).count()
    return render(request, "login/bookingCancelConfirm.html", {'data': data[0], 'count': count})


def bookingcancelredirect(request):
    bookingID = request.GET.get('bid', '1')
    adminID = request.GET.get('aid', '3')
    # update status of booking
    bookingObject = Booking.objects.get(pk=int(bookingID))
    bookingObject.Status = 2
    bookingObject.save()
    # add notification for admin
    try:
        logObject = BookingLog.objects.get(Actor=1, Admin_id=adminID, Booking_id=int(bookingID))
        # todo
        logObject.Message = ''
        logObject.notified = 0
        logObject.save()
    except BookingLog.DoesNotExist:
        logObject = BookingLog(Actor=1, Message='', notified=0, Admin_id=adminID, Booking_id=int(bookingID))
        logObject.save()
    # increase the number of free rooms
    hotelBookingObject = Hotel_Booking.objects.get(Booking=bookingObject)
    hotelRoomObject = hotelBookingObject.Hotel_Room
    hotelRoomObject.FreeRoomCount += hotelBookingObject.TotalRooms
    hotelRoomObject.save()
    return HttpResponseRedirect('userbookings')


def userflightbookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT DISTINCT B.id as 'bookingid',B.User_id,FR.Price*FB.TotalSeats as 'Price', FB.TotalSeats as 'TotalSeats'"
        ",A.AirCompany_Name as 'AirCompany_Name',F.Airplane_Number as 'Plane', F.Aircraft as 'Model', FR.Time as 'Time'"
        ",FR.Date as 'DOF', B.DateOfBooking as 'DOB',(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund "
        "as 'RefundedMoneyUponCancellation','+'||CP.DaysCount||' day' as 'datestr', FR.Source_Airport ||','||R.Source "
        "as 'SRC' , FR.Destination_Airport||','||R.Destination as 'DEST', FR.Duration as 'Duration' FROM "
        "database_flight_booking FB JOIN database_booking B ON (FB.Booking_id=B.id) JOIN database_flight_route FR ON "
        "(FB.Flight_id = FR.id) JOIN database_flight F ON (FR.Flight_id = F.id) JOIN database_air_company A ON "
        "(F.AirCompany_id = A.id) JOIN database_cancellation_policy CP ON (CP.id = FR.Cancellation_Policy_id) JOIN "
        "database_route R ON (R.id = FR.Route_id) WHERE B.User_id = %s and B.Status=0 and "
        "DATETIME(B.DateOfBooking,datestr)>=date('now') order by B.DateOfBooking,FR.Date", [request.user.id])
    data = namedtuplefetchall(cursor)
    # notifications count
    count = BookingLog.objects.filter(Actor=0, notified=0, Booking__User=request.user).count()
    return render(request, "login/userFlightBookings.html", {'data': data, 'count': count})


def flightbookingcancel(request):
    bookingID = request.GET.get('bid', '1')
    bookingID = int(bookingID)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT DISTINCT A.CompanyAdmin_id as 'AdminID',B.id as 'bookingid',B.User_id,FR.Price*FB.TotalSeats as 'Price'"
        ", FB.TotalSeats as 'TotalSeats', A.AirCompany_Name as 'AirCompany_Name',F.Airplane_Number as 'Plane', "
        "F.Aircraft as 'Model', FR.Time as 'Time', FR.Date as 'DOF', B.DateOfBooking as 'DOB',(B.PaidMoney) as "
        "'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation', '+'||CP.DaysCount||' day'"
        " as 'datestr', FR.Source_Airport ||','||R.Source as 'SRC' , FR.Destination_Airport||','||R.Destination as "
        "'DEST', FR.Duration as 'Duration' FROM database_flight_booking FB JOIN database_booking B ON "
        "(FB.Booking_id=B.id) JOIN database_flight_route FR ON (FB.Flight_id = FR.id) JOIN database_flight F ON "
        "(FR.Flight_id = F.id) JOIN database_air_company A ON (F.AirCompany_id = A.id) JOIN "
        "database_cancellation_policy CP ON (CP.id = FR.Cancellation_Policy_id) JOIN database_route R ON "
        "(R.id = FR.Route_id) WHERE B.User_id = %s and B.id = %s and B.Status=0 and "
        "DATETIME(B.DateOfBooking,datestr)>=date('now') order by B.DateOfBooking,FR.Date", [request.user.id, bookingID])
    data = namedtuplefetchall(cursor)
    # notifications count
    count = BookingLog.objects.filter(Actor=0, notified=0, Booking__User=request.user).count()
    return render(request, "login/flightBookingCancelConfirm.html", {'datum': data[0], 'count': count})


def flightbookingcancelredirect(request):
    bookingID = request.GET.get('bid', '1')
    adminID = request.GET.get('aid', '3')
    bookingObject = Booking.objects.get(pk=int(bookingID))
    bookingObject.Status = 2
    bookingObject.save()
    # add notification for admin
    try:
        logObject = BookingLog.objects.get(Actor=1, Admin_id=adminID, Booking_id=int(bookingID))
        # todo
        logObject.Message = ''
        logObject.notified = 0
        logObject.save()
    except BookingLog.DoesNotExist:
        logObject = BookingLog(Actor=1, Message='', notified=0, Admin_id=adminID, Booking_id=int(bookingID))
        logObject.save()
    flightbookingobject = Flight_Booking.objects.get(Booking=bookingObject)
    flightrouteobject = flightbookingobject.Flight
    flightrouteobject.TotalSeatsBooked = flightrouteobject.TotalSeatsBooked - flightbookingobject.TotalSeats
    flightrouteobject.save()
    return HttpResponseRedirect('userflightbookings')


def userprofile(request):
    userObject = User.objects.get(id=request.user.id)
    profileObject = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        profileForm = UpdateProfileForm(request.POST)
        if profileForm.is_valid():
            # updating user first
            userObject.first_name = profileForm.cleaned_data['firstName']
            userObject.last_name = profileForm.cleaned_data['lastName']
            userObject.email = profileForm.cleaned_data['email']
            userObject.save()
            # updating profile
            profileObject.Phone = profileForm.cleaned_data['phone']
            profileObject.Address = profileForm.cleaned_data['address']
            profileObject.save()
            messages.success(request, 'Your profile was successfully updated!')
        else:
            print(profileForm.errors)
    else:
        profileForm = UpdateProfileForm()
    # notifications count
    count = BookingLog.objects.filter(Actor=0, notified=0, Booking__User=request.user).count()
    return render(request, "login/profile.html",
                  {'profileForm': profileForm, 'profileObject': profileObject, 'count': count})


def userpassword(request):
    if request.method == 'POST':
        passwordForm = PasswordChangeForm(request.user, request.POST)
        if passwordForm.is_valid():
            user = passwordForm.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
        else:
            print(passwordForm.errors)
    else:
        passwordForm = PasswordChangeForm(request.user)
    # notifications count
    count = BookingLog.objects.filter(Actor=0, notified=0, Booking__User=request.user).count()
    return render(request, "login/password.html",
                  {'passwordForm': passwordForm, 'count': count})
