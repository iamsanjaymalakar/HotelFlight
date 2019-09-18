from django.shortcuts import render
from database.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from collections import namedtuple
from django.db import connection


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def admindash(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(HR.Price)*.05 as 'TotalRevenue' , B.DateOfBooking as 'Date',HB.Checkin_Date "
        "FROM database_booking B JOIN database_hotel_booking HB ON B.id=HB.Booking_id JOIN database_hotel_room HR "
        "ON HB.Hotel_Room_id=HR.id GROUP BY HB.Checkin_Date")
    dataHotelRev = namedtuplefetchall(cursor)
    cursor.execute(
        "SELECT AU.first_name || ' '|| AU.last_name as 'name' , PR.Phone as 'phn', PR.Address as 'addr', "
        "AU.email as 'mail',PL.Flag,H.Hotel_Name as Hotel_Name,R.RoomType as RoomType,HR.Price as UnitPrice,"
        "B.MoneyToPay as MoneyToPay,B.MoneyToRefund as MoneyToRefund,B.PaidMoney as PaidMoney,B.DateOfBooking "
        "as DOB,HB.Checkin_Date as CheckinDate,HB.Checkout_Date as CheckoutDate,HB.TotalRooms as TotalRooms FROM "
        "database_payment_log PL JOIN database_booking B ON (PL.booking_id = B.id) JOIN database_hotel_booking HB "
        "ON(HB.Booking_id = B.id) JOIN database_hotel_room HR ON (HB.Hotel_Room_id = HR.id) "
        "JOIN database_hotel H ON (H.id = HR.Hotel_id) JOIN database_room R ON (R.id = HR.Room_id) "
        "JOIN auth_user AU on (B.User_id=AU.id) JOIN database_profile PR ON (PR.user_id = AU.id) "
        " WHERE PL.Admin_id=%s", [request.user.id])
    dataPayment = namedtuplefetchall(cursor)
    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(HR.Price)*.05 as 'TotalRevenue' , H.Hotel_Name as 'HotelName' "
        "FROM database_booking B JOIN database_hotel_booking HB ON B.id=HB.Booking_id "
        "JOIN database_hotel_room HR ON HB.Hotel_Room_id=HR.id "
        "JOIN database_hotel H ON HR.Hotel_id=H.id "
        "GROUP BY H.id ORDER BY sum(HR.Price) ")
    dataPie = namedtuplefetchall(cursor)
    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(FR.Price)*.05 as 'TotalRevenue' , B.DateOfBooking as 'Date' "
        "FROM database_booking B JOIN database_flight_booking FB ON B.id=FB.Booking_id "
        "JOIN database_flight_route FR ON FB.Flight_id=FR.id "
        "GROUP BY B.DateOfBooking")
    results3 = cursor.fetchall()
    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(FR.Price)*.05 as 'TotalRevenue' , AC.AirCompany_Name as 'CompanyName' "
        "FROM database_booking B JOIN database_flight_booking FB ON B.id=FB.Booking_id "
        "JOIN database_flight_route FR ON FB.Flight_id=FR.id "
        "JOIN database_flight F ON FR.Flight_id=F.id "
        "JOIN database_air_company AC ON F.AirCompany_id=AC.id "
        "GROUP BY AC.id "
        "ORDER BY sum(FR.Price)")
    results4 = cursor.fetchall()

    # notification count
    cursor = connection.cursor()
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminDash.html",
                  {'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount,
                   'dataHotelRev': dataHotelRev, 'dataPayment': dataPayment,
                   'dataPie': dataPie, 'data3': results3, 'data4': results4})


def viewHotels(request):
    cursor = connection.cursor()
    cursor.execute(
        "select Hotel_Name,Hotel_Location,Hotel_Country,Address,Phone,TotalSentMoney,Percentage,Latitude,Longitude"
        " from database_hotel")
    data = namedtuplefetchall(cursor)
    # notification count
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminHotels.html",
                  {'data': data, 'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount})


def viewAirlines(request):
    cursor = connection.cursor()
    cursor.execute(
        "select AirCompany_Name,TotalSentMoney,Percentage from database_air_company")
    data = namedtuplefetchall(cursor)
    # notification count
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminAirlines.html",
                  {'data': data, 'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount})


def viewPaymentLog(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT AU.first_name || ' '|| AU.last_name as 'name' , PR.Phone as 'phn', PR.Address as 'addr', "
        "AU.email as 'mail',PL.Flag,H.Hotel_Name as Hotel_Name,R.RoomType as RoomType,HR.Price as UnitPrice,"
        "B.MoneyToPay as MoneyToPay,B.MoneyToRefund as MoneyToRefund,B.PaidMoney as PaidMoney,B.DateOfBooking "
        "as DOB,HB.Checkin_Date as CheckinDate,HB.Checkout_Date as CheckoutDate,HB.TotalRooms as TotalRooms FROM "
        "database_payment_log PL JOIN database_booking B ON (PL.booking_id = B.id) JOIN database_hotel_booking HB "
        "ON(HB.Booking_id = B.id) JOIN database_hotel_room HR ON (HB.Hotel_Room_id = HR.id) "
        "JOIN database_hotel H ON (H.id = HR.Hotel_id) JOIN database_room R ON (R.id = HR.Room_id) "
        "JOIN auth_user AU on (B.User_id=AU.id) JOIN database_profile PR ON (PR.user_id = AU.id) "
        " WHERE PL.Admin_id=%s", [request.user.id])
    '''
    cursor.execute(
        "SELECT PL.Flag,H.Hotel_Name as Hotel_Name,R.RoomType as RoomType,HR.Price as UnitPrice,"
        "B.MoneyToPay as MoneyToPay,B.MoneyToRefund as MoneyToRefund,B.PaidMoney as PaidMoney,"
        "B.DateOfBooking as DOB,HB.Checkin_Date as CheckinDate,HB.Checkout_Date as CheckoutDate,"
        "HB.TotalRooms as TotalRooms FROM database_payment_log PL JOIN database_booking B ON (PL.booking_id = B.id) "
        "JOIN database_hotel_booking HB ON(HB.Booking_id = B.id) JOIN database_hotel_room HR ON "
        "(HB.Hotel_Room_id = HR.id) JOIN database_hotel H ON (H.id = HR.Hotel_id) JOIN database_room R ON "
        "(R.id = HR.Room_id) WHERE PL.Admin_id=%s", [request.user.id])
    '''
    data = namedtuplefetchall(cursor)
    # notification count
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminPaymentLog.html",
                  {'data': data, 'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount})


def viewAirlinesPaymentLog(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT  AU.first_name || ' '|| AU.last_name as 'name' , PR.Phone as 'phn', PR.Address as 'addr', "
        "AU.email as 'mail', PL.Flag,B.User_id,FR.Price*FB.TotalSeats as 'Price', FB.TotalSeats as 'TotalSeats', "
        "A.AirCompany_Name as 'AirCompany_Name', F.Airplane_Number as 'Plane', F.Aircraft as 'Model', FR.Time "
        "as 'Time', FR.Date as 'DOF', B.DateOfBooking as 'DOB', (B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',"
        "B.MoneyToRefund as 'RefundedMoneyUponCancellation', FR.Source_Airport||','||R.Source as 'SRC' , "
        "FR.Destination_Airport||','||R.Destination as 'DEST', FR.Duration as 'Duration' FROM database_booking B "
        "JOIN database_payment_log PL ON (PL.Booking_id=B.id) JOIN database_flight_booking FB ON (FB.Booking_id=B.id) "
        "JOIN database_flight_route FR ON (FB.Flight_id = FR.id) JOIN database_flight F ON (FR.Flight_id = F.id) "
        "JOIN database_air_company A ON (F.AirCompany_id = A.id) JOIN database_route R ON (R.id=FR.Route_id) "
        "JOIN auth_user AU on (B.User_id=AU.id) JOIN database_profile PR ON (PR.user_id = AU.id) "
        "WHERE PL.Admin_id=%s", [request.user.id])
    '''
    cursor.execute(
        "SELECT DISTINCT PL.Flag,B.User_id,FR.Price*FB.TotalSeats as 'Price', FB.TotalSeats as 'TotalSeats', "
        "A.AirCompany_Name as 'AirCompany_Name', F.Airplane_Number as 'Plane', F.Aircraft as 'Model', FR.Time as 'Time'"
        ", FR.Date as 'DOF', B.DateOfBooking as 'DOB', (B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',"
        "B.MoneyToRefund as 'RefundedMoneyUponCancellation', FR.Source_Airport||','||R.Source as 'SRC' , "
        "FR.Destination_Airport||','||R.Destination as 'DEST', FR.Duration as 'Duration' FROM database_booking B "
        "JOIN database_payment_log PL ON (PL.Booking_id=B.id) JOIN database_flight_booking FB ON (FB.Booking_id=B.id) "
        "JOIN database_flight_route FR ON (FB.Flight_id = FR.id) JOIN database_flight F ON (FR.Flight_id = F.id) "
        "JOIN database_air_company A ON (F.AirCompany_id = A.id) JOIN database_route R ON (R.id=FR.Route_id) "
        "WHERE PL.Admin_id=%s", [request.user.id])
    '''
    data = namedtuplefetchall(cursor)
    # notification count
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminAirlinesPaymentLog.html",
                  {'data': data, 'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount})


def approveHotelBookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT AU.first_name || ' '|| AU.last_name as 'name' , PR.Phone as 'phn', PR.Address as 'addr', AU.email as "
        "'mail', B.id as 'bookingID', H.Hotel_Name as Hotel_Name,R.RoomType as 'RoomType',HR.Price as 'Price',"
        "B.MoneyToPay as 'MoneyToPay',B.MoneyToRefund as MoneyToRefund,B.PaidMoney as PaidMoney,"
        "B.DateOfBooking as DOB,HB.Checkin_Date as CheckinDate,HB.Checkout_Date as CheckoutDate,HB.TotalRooms as "
        "TotalRooms FROM database_booking B JOIN database_hotel_booking HB ON(HB.Booking_id = B.id) JOIN "
        "database_hotel_room HR ON (HB.Hotel_Room_id = HR.id) JOIN database_hotel H ON (H.id = HR.Hotel_id) JOIN "
        "database_room R ON (R.id = HR.Room_id) JOIN auth_user AU on (B.User_id=AU.id) JOIN database_profile PR ON "
        "(PR.user_id = AU.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    '''
    cursor.execute(
        "SELECT B.id as 'bookingID', H.Hotel_Name as Hotel_Name,R.RoomType as 'RoomType',HR.Price as 'Price',"
        "B.MoneyToPay as 'MoneyToPay',B.MoneyToRefund as MoneyToRefund,B.PaidMoney as PaidMoney,B.DateOfBooking "
        "as DOB,HB.Checkin_Date as CheckinDate,HB.Checkout_Date as CheckoutDate,HB.TotalRooms as TotalRooms "
        "FROM database_booking B JOIN database_hotel_booking HB ON(HB.Booking_id = B.id) JOIN database_hotel_room HR"
        " ON (HB.Hotel_Room_id = HR.id) JOIN database_hotel H ON (H.id = HR.Hotel_id) JOIN database_room R ON "
        "(R.id = HR.Room_id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    '''
    data = namedtuplefetchall(cursor)
    # notification count
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminApproveHotelBooking.html",
                  {'data': data, 'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount})


def approveHotelBookingRedirect(request):
    bookingID = request.GET.get('bookingID', '')
    hotelBookingObject = Hotel_Booking.objects.get(Booking=Booking.objects.get(pk=int(bookingID)))
    hotelBookingObject.isApproved = True
    hotelBookingObject.save()
    hotelRoomObject = Hotel_Room.objects.get(pk=hotelBookingObject.Hotel_Room_id)
    bookingObject = Booking.objects.get(pk=int(bookingID))
    moneyToSend = bookingObject.PaidMoney
    hotelToSend = hotelRoomObject.Hotel_id
    hotelObject = Hotel.objects.get(pk=int(hotelToSend))
    hotelObject.TotalSentMoney += moneyToSend
    hotelObject.save()
    payment = Payment_Log(Booking_id=bookingID, Admin_id=request.user.id, Flag=True)
    payment.save()
    return HttpResponseRedirect('approveHotelBookings')


def approveCancelHotelBookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT AU.first_name || ' '|| AU.last_name as 'name' , PR.Phone as 'phn', PR.Address as 'addr', AU.email as "
        "'mail',B.id as 'bookingID', H.Hotel_Name as Hotel_Name,R.RoomType as 'RoomType',HR.Price as 'Price', "
        "B.MoneyToPay as 'MoneyToPay',B.MoneyToRefund as MoneyToRefund,B.PaidMoney as PaidMoney,"
        "B.DateOfBooking as DOB,HB.Checkin_Date as CheckinDate,HB.Checkout_Date as CheckoutDate,HB.TotalRooms as "
        "TotalRooms FROM database_booking B JOIN database_hotel_booking HB ON(HB.Booking_id = B.id) JOIN "
        "database_hotel_room HR ON (HB.Hotel_Room_id = HR.id) JOIN database_hotel H ON (H.id = HR.Hotel_id) JOIN "
        "database_room R ON (R.id = HR.Room_id) JOIN auth_user AU on (B.User_id=AU.id) JOIN database_profile PR ON "
        "(PR.user_id = AU.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    '''
    cursor.execute(
        "SELECT B.id as 'bookingID', H.Hotel_Name as Hotel_Name,R.RoomType as 'RoomType',HR.Price as 'Price',"
        "B.MoneyToPay as 'MoneyToPay',B.MoneyToRefund as MoneyToRefund,B.PaidMoney as PaidMoney,B.DateOfBooking as DOB"
        ",HB.Checkin_Date as CheckinDate,HB.Checkout_Date as CheckoutDate,HB.TotalRooms as TotalRooms FROM "
        "database_booking B JOIN database_hotel_booking HB ON(HB.Booking_id = B.id) JOIN database_hotel_room HR ON "
        "(HB.Hotel_Room_id = HR.id) JOIN database_hotel H ON (H.id = HR.Hotel_id) JOIN database_room R ON "
        "(R.id = HR.Room_id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    '''
    data = namedtuplefetchall(cursor)
    # notification count
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminApproveCancelHotelBooking.html",
                  {'data': data, 'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount})


def approveCancelHotelBookingRedirect(request):
    bookingID = request.GET.get('bookingID', '')
    hotelBookingObject = Hotel_Booking.objects.get(Booking=Booking.objects.get(pk=int(bookingID)))
    hotelBookingObject.isCancellationApproved = True
    hotelBookingObject.save()
    hotelRoomObject = Hotel_Room.objects.get(pk=hotelBookingObject.Hotel_Room_id)
    bookingObject = Booking.objects.get(pk=int(bookingID))
    moneyToRefund = bookingObject.MoneyToRefund
    hotelToSend = hotelRoomObject.Hotel_id
    hotelObject = Hotel.objects.get(pk=int(hotelToSend))
    hotelObject.TotalSentMoney -= moneyToRefund
    hotelObject.save()
    payment = Payment_Log(Booking_id=bookingID, Admin_id=request.user.id, Flag=False)
    payment.save()
    return HttpResponseRedirect('approveCancelHotelBookings')


def approveFlightBookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT AU.first_name || ' '|| AU.last_name as 'name' , PR.Phone as 'phn', PR.Address as 'addr', AU.email as 'mail',  FB.id as 'fid',B.id as 'bookingID',FR.Price*FB.TotalSeats as 'Price', FB.TotalSeats as 'TotalSeats', A.AirCompany_Name as 'AirCompany_Name', "
        "F.Airplane_Number as 'Plane', F.Aircraft as 'Model', FR.Time as 'Time', FR.Date as 'DOF', B.DateOfBooking as 'DOB', "
        "(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation', "
        "FR.Source_Airport||','||R.Source as 'SRC' , FR.Destination_Airport||','||R.Destination as 'DEST', FR.Duration as 'Duration' "
        "FROM database_flight_booking FB JOIN database_booking B ON (FB.Booking_id=B.id) "
        "JOIN database_flight_route FR ON (FB.Flight_id = FR.id) "
        "JOIN database_flight F ON (FR.Flight_id = F.id) "
        "JOIN database_air_company A ON (F.AirCompany_id = A.id) JOIN database_route R ON (R.id=FR.Route_id) JOIN auth_user AU on (B.User_id=AU.id) "
        "JOIN database_profile PR ON (PR.user_id = AU.id)  where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    data = namedtuplefetchall(cursor)
    # notification count
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminApproveFlightBooking.html",
                  {'data': data, 'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount})


def approveCancelFlightBookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT AU.first_name || ' '|| AU.last_name as 'name' , PR.Phone as 'phn', PR.Address as 'addr', AU.email as 'mail', FB.id as 'fid',B.id as 'bookingID',FR.Price*FB.TotalSeats as 'Price', FB.TotalSeats as 'TotalSeats', A.AirCompany_Name as 'AirCompany_Name', "
        "F.Airplane_Number as 'Plane', F.Aircraft as 'Model', FR.Time as 'Time', FR.Date as 'DOF', B.DateOfBooking as 'DOB', "
        "(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation', "
        "FR.Source_Airport||','||R.Source as 'SRC' , FR.Destination_Airport||','||R.Destination as 'DEST', FR.Duration as 'Duration' "
        "FROM database_flight_booking FB JOIN database_booking B ON (FB.Booking_id=B.id) "
        "JOIN database_flight_route FR ON (FB.Flight_id = FR.id) "
        "JOIN database_flight F ON (FR.Flight_id = F.id) "
        "JOIN database_air_company A ON (F.AirCompany_id = A.id) JOIN database_route R ON (R.id=FR.Route_id) "
        "JOIN auth_user AU on (B.User_id=AU.id) JOIN database_profile PR ON (PR.user_id = AU.id) "
        "where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    data = namedtuplefetchall(cursor)
    # notification count
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminApproveCancelFlightBooking.html",
                  {'data': data, 'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount})


def approveFlightBookingRedirect(request):
    id = request.GET.get('bookingID', '')
    print("bookingid")
    print(id)
    fid = request.GET.get('fid', '')
    flightbookingobject = Flight_Booking.objects.get(pk=int(fid))
    print('flight booking id')
    print(fid)
    flightbookingobject.isApproved = True
    flightbookingobject.save()
    flightroute = Flight_Route.objects.get(pk=flightbookingobject.Flight_id)
    cursor = connection.cursor()
    cursor.execute("SELECT PaidMoney FROM database_booking where id=%s", [id])
    results = cursor.fetchone()
    MoneyToSend = results[0]
    print(MoneyToSend)
    cursor.execute("SELECT Flight_id FROM database_flight_route where id=%s", [flightroute.id])
    results = cursor.fetchone()
    Flight = results[0]
    print("flight ID")
    print(Flight)
    cursor.execute("SELECT AirCompany_id FROM database_flight where id=%s", [Flight])
    results = cursor.fetchone()
    AirCompany = results[0]
    print("Air company ID: ")
    print(AirCompany)
    cursor.execute("UPDATE database_air_company "
                   "SET TotalSentMoney = TotalSentMoney + %s "
                   "WHERE id=%s", [MoneyToSend, AirCompany])
    payment = Payment_Log(Booking_id=id, Admin_id=request.user.id, Flag=True)
    payment.save()
    print("Approved")
    return HttpResponseRedirect('approveFlightBookings')


def approveCancelFlightBookingRedirect(request):
    id = request.GET.get('bookingID', '')
    print("bookingid")
    print(id)
    fid = request.GET.get('fid', '')
    flightbookingobject = Flight_Booking.objects.get(pk=int(fid))
    print('flight booking id')
    print(fid)
    flightbookingobject.isCancellationApproved = True
    flightbookingobject.save()
    flightroute = Flight_Route.objects.get(pk=flightbookingobject.Flight_id)
    cursor = connection.cursor()
    cursor.execute("SELECT MoneyToRefund FROM database_booking where id=%s", [id])
    results = cursor.fetchone()
    MoneyToDeduct = results[0]
    print(MoneyToDeduct)
    cursor.execute("SELECT Flight_id FROM database_flight_route where id=%s", [flightroute.id])
    results = cursor.fetchone()
    Flight = results[0]
    print("flight ID")
    print(Flight)
    cursor.execute("SELECT AirCompany_id FROM database_flight where id=%s", [Flight])
    results = cursor.fetchone()
    AirCompany = results[0]
    print("Air company ID: ")
    print(AirCompany)
    cursor.execute("UPDATE database_air_company "
                   "SET TotalSentMoney = TotalSentMoney - %s "
                   "WHERE id=%s", [MoneyToDeduct, AirCompany])
    payment = Payment_Log(Booking_id=id, Admin_id=request.user.id, Flag=False)
    payment.save()
    print("Cancellation approved")
    return HttpResponseRedirect('approveCancelFlightBookings')


def viewStats(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(HR.Price)*.05 as 'TotalRevenue' , B.DateOfBooking as 'Date' "
        "FROM database_booking B JOIN database_hotel_booking HB ON B.id=HB.Booking_id "
        "JOIN database_hotel_room HR ON HB.Hotel_Room_id=HR.id "
        "GROUP BY B.DateOfBooking")
    results1 = cursor.fetchall()
    totalHotelBooking = []
    totalHotelRevenue = []
    dates = []
    for row in results1:
        print(row)
        totalHotelBooking.append(row[0])
        totalHotelRevenue.append(row[1])
        dates.append(row[2])
    data = namedtuplefetchall(cursor)
    print("Data1")
    print(data)
    print(results1)
    print(results1[0][2])

    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(HR.Price)*.05 as 'TotalRevenue' , H.Hotel_Name as 'HotelName' "
        "FROM database_booking B JOIN database_hotel_booking HB ON B.id=HB.Booking_id "
        "JOIN database_hotel_room HR ON HB.Hotel_Room_id=HR.id "
        "JOIN database_hotel H ON HR.Hotel_id=H.id "
        "GROUP BY H.id ORDER BY sum(HR.Price) ")
    results2 = cursor.fetchall();
    print(results2)

    '''y_pos = np.arange(len(totalHotelBooking))
    plt.bar(y_pos, totalHotelBooking, align='center', color="skyblue")
    plt.xticks(y_pos, dates)
    plt.xlabel('Date')
    plt.ylabel('Hotel Bookings')
    plt.title('Hotel Booking per day')
    plt.savefig('./HotelFlight/static/siteadmin/barPlotHotelBooking.png')

    y_pos = np.arange(len(totalHotelRevenue))
    plt.bar(y_pos, totalHotelRevenue, align='center', color="lightgreen")
    plt.xticks(y_pos, dates)
    plt.xlabel('Date')
    plt.ylabel('Revenue from Hotels')
    plt.title('Revenue from hotels per day')
    plt.savefig('./HotelFlight/static/siteadmin/barPlotHotelRevenue.png')
    #plt.show()'''

    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(FR.Price)*.05 as 'TotalRevenue' , B.DateOfBooking as 'Date' "
        "FROM database_booking B JOIN database_flight_booking FB ON B.id=FB.Booking_id "
        "JOIN database_flight_route FR ON FB.Flight_id=FR.id "
        "GROUP BY B.DateOfBooking")
    results3 = cursor.fetchall()

    data = namedtuplefetchall(cursor)
    print("Data3")
    print(data)
    print(results3)
    # print(totalHotelBooking)

    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(FR.Price)*.05 as 'TotalRevenue' , AC.AirCompany_Name as 'CompanyName' "
        "FROM database_booking B JOIN database_flight_booking FB ON B.id=FB.Booking_id "
        "JOIN database_flight_route FR ON FB.Flight_id=FR.id "
        "JOIN database_flight F ON FR.Flight_id=F.id "
        "JOIN database_air_company AC ON F.AirCompany_id=AC.id "
        "GROUP BY AC.id "
        "ORDER BY sum(FR.Price)")
    results4 = cursor.fetchall()

    data = namedtuplefetchall(cursor)
    print("Data3")
    print(data)
    print(results4)
    # notification count
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=0 AND HB.isCancellationApproved=0 AND B.Status<>2")
    hotelApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_hotel_booking HB join database_booking B on "
                   "(HB.Booking_id=B.id) where HB.isApproved=1 AND HB.isCancellationApproved=0 AND B.Status=2")
    hotelCancelCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=0 AND FB.isCancellationApproved=0 AND B.Status<>2")
    flightApproveCount = namedtuplefetchall(cursor)[0].cnt
    cursor.execute("select count(*) as cnt from database_flight_booking FB join database_booking B on "
                   "(FB.Booking_id=B.id) where FB.isApproved=1 AND FB.isCancellationApproved=0 AND B.Status=2")
    flightCancelCount = namedtuplefetchall(cursor)[0].cnt
    return render(request, "siteadmin/AdminStats.html",
                  {'data1': results1, 'data2': results2, 'data3': results3, 'data4': results4,
                   'hotelApproveCount': hotelApproveCount, 'hotelCancelCount': hotelCancelCount,
                   'flightApproveCount': flightApproveCount, 'flightCancelCount': flightCancelCount})
