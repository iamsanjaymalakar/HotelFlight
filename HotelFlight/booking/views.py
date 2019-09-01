from database.models import *
from search.forms import SearchHotelForm, SearchFlightForm
from django.shortcuts import render
from .forms import HotelBookingForm, FlightBookingForm
from django.db import connection
from collections import namedtuple
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def daysBetween(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


# Create your views here.
def hotelbookingpage(request):
    checkIn = request.GET.get('checkin', '')
    checkOut = request.GET.get('checkout', '')
    roomCount = request.GET.get('room', '')
    dateCount = daysBetween(checkIn, checkOut)
    hotelRoomID = request.GET.get('hrid', '')
    adultCount = request.GET.get('adult', '')
    cursor = connection.cursor()
    cursor.execute("SELECT R.RoomType, R.SingleBedCount, R.DoubleBedCount,HR.Room_id as 'roomID',HR.Price*%s as "
                   "'NPrice',HR.Price*%s*%s as 'Price',R.AirConditioner,HR.Complimentary_Breakfast,HR.wifi FROM "
                   "database_hotel_room HR JOIN database_room R ON HR.Room_id=R.id "
                   "WHERE HR.id=%s",
                   [int(roomCount), int(roomCount), dateCount, int(hotelRoomID)])
    room = namedtuplefetchall(cursor)
    cursor.execute("SELECT H.Hotel_Name, H.Hotel_Location, H.Hotel_Country,H.Address,H.CompanyAdmin_id as 'uid' FROM "
                   "database_hotel_room HR JOIN database_hotel H ON HR.Hotel_id=H.id WHERE HR.id=%s",
                   [int(hotelRoomID)])
    hotel = namedtuplefetchall(cursor)
    form = HotelBookingForm()
    hotelForm = SearchHotelForm()
    flightForm = SearchFlightForm()
    # setting initial values for room and adult
    hotelForm.fields['room'].initial = int(roomCount)
    hotelForm.fields['adult'].initial = int(adultCount)
    return render(request, "booking/hotelbooking.html",
                  {'room': room[0], 'hotel': hotel[0], 'form': form, 'hotelForm': hotelForm, 'flightForm': flightForm,
                   'daysCount': dateCount})


def hotelbookingpaymet(request):
    checkIn = request.GET.get('checkin', '')
    checkOut = request.GET.get('checkout', '')
    roomCount = request.GET.get('room', '')
    dateCount = daysBetween(checkIn, checkOut)
    hotelRoomID = request.GET.get('hrid', '')
    adultCount = request.GET.get('adult', '')
    cursor = connection.cursor()
    cursor.execute("SELECT R.RoomType, R.SingleBedCount, R.DoubleBedCount,HR.Room_id as 'roomID',HR.Price*%s as "
                   "'NPrice',HR.Price*%s*%s as 'Price',R.AirConditioner,HR.Complimentary_Breakfast,HR.wifi FROM "
                   "database_hotel_room HR JOIN database_room R ON HR.Room_id=R.id "
                   "WHERE HR.id=%s",
                   [int(roomCount), int(roomCount), dateCount, int(hotelRoomID)])
    room = namedtuplefetchall(cursor)
    cursor.execute("SELECT H.Hotel_Name, H.Hotel_Location, H.Hotel_Country,H.Address,H.CompanyAdmin_id as 'uid' FROM "
                   "database_hotel_room HR JOIN database_hotel H ON HR.Hotel_id=H.id WHERE HR.id=%s",
                   [int(hotelRoomID)])
    hotel = namedtuplefetchall(cursor)
    form = HotelBookingForm()
    hotelForm = SearchHotelForm()
    flightForm = SearchFlightForm()
    # setting initial values for room and adult
    hotelForm.fields['room'].initial = int(roomCount)
    hotelForm.fields['adult'].initial = int(adultCount)
    return render(request, "booking/bookingpayment.html",
                  {'room': room[0], 'hotel': hotel[0], 'form': form, 'hotelForm': hotelForm, 'flightForm': flightForm,
                   'daysCount': dateCount})


def BookingConfirmationPage(request):
    checkIn = request.GET.get('checkin', '')
    checkOut = request.GET.get('checkout', '')
    roomCount = request.GET.get('room', '')
    dateCount = daysBetween(checkIn, checkOut)
    hotelRoomID = request.GET.get('hrid', '')
    adultCount = request.GET.get('adult', '')
    cursor = connection.cursor()
    cursor.execute("SELECT R.RoomType, R.SingleBedCount, R.DoubleBedCount,HR.Room_id as 'roomID',HR.Price*%s as "
                   "'NPrice',HR.Price*%s*%s as 'Price',R.AirConditioner,HR.Complimentary_Breakfast,HR.wifi FROM "
                   "database_hotel_room HR JOIN database_room R ON HR.Room_id=R.id "
                   "WHERE HR.id=%s",
                   [int(roomCount), int(roomCount), dateCount, int(hotelRoomID)])
    room = namedtuplefetchall(cursor)
    cursor.execute("SELECT H.Hotel_Name, H.Hotel_Location, H.Hotel_Country,H.Address,H.CompanyAdmin_id as 'uid' FROM "
                   "database_hotel_room HR JOIN database_hotel H ON HR.Hotel_id=H.id WHERE HR.id=%s",
                   [int(hotelRoomID)])
    hotel = namedtuplefetchall(cursor)
    form = HotelBookingForm()
    hotelForm = SearchHotelForm()
    flightForm = SearchFlightForm()
    firstName = request.GET.get('first_name', '')
    lastName = request.GET.get('last_name', '')
    email = request.GET.get('email', '')
    hotelID = request.GET.get('hid', '')
    userID = request.GET.get('uid', '')
    price = Hotel_Room.objects.get(id=int(hotelRoomID)).Price
    percentage = Hotel.objects.get(id=int(hotelID)).Percentage / 100
    paidMoney = percentage * price * int(roomCount) * dateCount
    moneyToPay = price * (1 - percentage) * int(roomCount) * dateCount
    percentageRefunding = Cancellation_Policy.objects.get(
        id=Hotel_Room.objects.get(id=int(hotelRoomID)).Cancellation_Policy_id).Percentage_refunding / 100
    moneyToRefund = paidMoney * percentageRefunding
    today = datetime.today().strftime('%Y-%m-%d')
    bookingObject = Booking(MoneyToPay=moneyToPay, MoneyToRefund=moneyToRefund, DateOfBooking=today,
                            DateOfCancellation=today, User_id=userID, PaidMoney=paidMoney, isCancelled=False,
                            Status=False)
    bookingObject.save()
    hotelBookingObject = Hotel_Booking(Booking=bookingObject, Hotel_Room_id=hotelRoomID, Checkin_Date=checkIn,
                                       Checkout_Date=checkOut, TotalRooms=roomCount, isApproved=False)
    hotelBookingObject.save()
    hotelRoomObject = Hotel_Room.objects.get(id=hotelRoomID)
    hotelRoomObject.FreeRoomCount -= int(roomCount)
    hotelRoomObject.save()
    '''
    # generate confirmation mail
    # create message object instance
    print(FirstName)
    print(LastName)
    p = canvas.Canvas('./booking/pdfs/ex.pdf')
    p.drawString(250, 700, "Itinerary")
    Fname = "First Name: " + FirstName
    Lname = "Last Name: " + LastName
    Contact = "Contact No.: " + Phone
    HotelName = "Hotel Name: " + hotel[0].Hotel_Name
    InDate = "Check In: " + checkin
    OutDate = "Check Out: " + checkout
    BookAmount = "Booking Amount: " + str(PaidMoney)
    RestAmount = "More to Pay: " + str(MoneyToPay)
    p.drawString(100, 620, "Personal Information")
    p.drawString(100, 600, Fname)
    p.drawString(100, 580, Lname)
    p.drawString(100, 560, Contact)
    p.drawString(100, 500, "Booking Information")
    p.drawString(100, 480, HotelName)
    p.drawString(100, 460, InDate)
    p.drawString(100, 440, OutDate)
    p.drawString(100, 420, BookAmount)
    p.drawString(100, 400, RestAmount)
    p.drawString(100, 350, "This booking has been confirmed.")
    p.drawImage('./HotelFlight/static/booking/barcode.jpg', 400, 750, 6 * cm, 2 * cm)
    p.showPage()
    p.save()
    # create message object instance
    msg = MIMEMultipart()
    message = "Your booking has been confirmed! Thanks for staying with us!!"
    # setup the parameters of the message
    password = "proxierOSP"
    msg['From'] = "onlineserviceprovider131625@gmail.com"
    msg['To'] = Email
    msg['Subject'] = "Response to Hotel/Flight Booking"
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    filename = "ex.pdf"
    attachment = open("./booking/pdfs/ex.pdf", "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    # Login Credentials for sending the mail
    # server.login(msg['From'], password)
    # send the message via the server.
    # server.sendmail(msg['From'], msg['To'], msg.as_string())
    # server.quit()
    print("email sent")
    msg = MIMEMultipart()
    message = "Your reservation has been succesfully confirmed!  " \
              "" \
              "" \
              "Room type:" + room[0].RoomType + "" \
                                                " No of rooms:" + roomcount + "" \
                                                                              "Check-in:" + checkin

    # setup the parameters of the message
    password = "proxierOSP"
    msg['From'] = "onlineserviceprovider131625@gmail.com"
    msg['To'] = Email
    msg['Subject'] = "Hotel reservation on" + hotel[0].Hotel_Name + " hotel"
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    # filename = "query1.txt"
    # attachment = open("./ReservationProject_Root/query1.txt", "rb")
    # p = MIMEBase('application', 'octet-stream')
    # p.set_payload((attachment).read())
    # encoders.encode_base64(p)
    # p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    # msg.attach(p)
    # create server
    #server = smtplib.SMTP('smtp.gmail.com: 587')
    #server.starttls()
    # Login Credentials for sending the mail
    #server.login(msg['From'], password)
    # send the message via the server.
    #server.sendmail(msg['From'], msg['To'], msg.as_string())
    #server.quit()
    #print("email sent")'''
    # setting initial values for room and adult
    hotelForm.fields['room'].initial = int(roomCount)
    hotelForm.fields['adult'].initial = int(adultCount)
    return render(request, "booking/bookingconfirmation.html",
                  {'room': room[0], 'hotel': hotel[0], 'form': form, 'hotelForm': hotelForm, 'flightForm': flightForm,
                   'daysCount': dateCount})


def FlightBookingPage(request):
    print("flight booking page")
    Source = request.GET.get('source', '')
    Dest = request.GET.get('dest', '')
    Departure_Date = request.GET.get('depart', '')
    frid = request.GET.get('FRID', '')
    id1 = request.GET.get('ID1', '')
    id2 = request.GET.get('ID2', '')
    adultCount = request.GET.get('adult', '')
    fids = request.GET.get('FIDS', '')
    fidm1 = request.GET.get('FIDM1', '')
    fidm2 = request.GET.get('FIDM2', '')
    print("Source: " + Source)
    print("Destination: " + Dest)
    print("Departure date: " + Departure_Date)
    print("Multiple hop flight route 1: " + id1)
    print("Multiple hop flight route 2: " + id2)
    print("Single hop 1: " + frid)
    print("Adult count: " + adultCount)
    print(adultCount)
    print("FIDS ->")
    print(fids)
    print("FIDM1 ->")
    print(fidm1)
    print("FIDM2 ->")
    print(fidm2)

    if id1 == "" and id2 == "":
        cursor = connection.cursor()

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [frid])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, frid])

        flight = namedtuplefetchall(cursor)
        form = FlightBookingForm()
        hotelform = SearchHotelForm()
        flightform = SearchFlightForm()
        return render(request, "booking/flightbooking.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'False'})
    else:
        cursor = connection.cursor()

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [id1])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, id1])

        flight = namedtuplefetchall(cursor)

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [id2])
        aircompany2 = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, id2])

        flight2 = namedtuplefetchall(cursor)
        form = FlightBookingForm()
        hotelform = SearchHotelForm()
        flightform = SearchFlightForm()
        return render(request, "booking/flightbooking.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'flight2': flight2[0],
                       'aircompany2': aircompany2[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'True'})


def flightbookingpayment(request):
    print("flight booking page")
    Source = request.GET.get('source', '')
    Dest = request.GET.get('dest', '')
    Departure_Date = request.GET.get('depart', '')
    frid = request.GET.get('FRID', '')
    id1 = request.GET.get('ID1', '')
    id2 = request.GET.get('ID2', '')
    adultCount = request.GET.get('adult', '')
    fids = request.GET.get('FIDS', '')
    fidm1 = request.GET.get('FIDM1', '')
    fidm2 = request.GET.get('FIDM2', '')
    print("Source: " + Source)
    print("Destination: " + Dest)
    print("Departure date: " + Departure_Date)
    print("Multiple hop flight route 1: " + id1)
    print("Multiple hop flight route 2: " + id2)
    print("Single hop 1: " + frid)
    print("Adult count: " + adultCount)
    print(adultCount)
    print("FIDS ->")
    print(fids)
    print("FIDM1 ->")
    print(fidm1)
    print("FIDM2 ->")
    print(fidm2)

    if id1 == "" and id2 == "":
        cursor = connection.cursor()

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [frid])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, frid])

        flight = namedtuplefetchall(cursor)
        form = FlightBookingForm()
        hotelform = SearchHotelForm()
        flightform = SearchFlightForm()
        return render(request, "booking/flightbookingpayment.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'False'})
    else:
        cursor = connection.cursor()

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [id1])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, id1])

        flight = namedtuplefetchall(cursor)

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [id2])
        aircompany2 = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, id2])

        flight2 = namedtuplefetchall(cursor)
        form = FlightBookingForm()
        hotelform = SearchHotelForm()
        flightform = SearchFlightForm()
        return render(request, "booking/flightbookingpayment.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'flight2': flight2[0],
                       'aircompany2': aircompany2[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'True'})


def FlightBookingConfirmationPage(request):
    FirstName = request.GET.get('first_name', '')
    LastName = request.GET.get('last_name', '')
    Email = request.GET.get('email', '')
    Phone = request.GET.get('phone', '')
    Passport = request.GET.get('passport', '')
    print(FirstName)
    print(LastName)
    print(Email)
    print(Phone)
    print("confirmation page")
    Source = request.GET.get('source', '')
    Dest = request.GET.get('dest', '')
    Departure_Date = request.GET.get('depart', '')
    frid = request.GET.get('FRID', '')
    id1 = request.GET.get('ID1', '')
    id2 = request.GET.get('ID2', '')
    uid = request.GET.get('uid', '')
    adultCount = request.GET.get('adult', '')
    fids = request.GET.get('FIDS', '')
    fidm1 = request.GET.get('FIDM1', '')
    fidm2 = request.GET.get('FIDM2', '')
    print(Source)
    print(Dest)
    print(Departure_Date)
    print(id1)
    print(id2)
    print(frid)
    print(uid)
    print(adultCount)
    print("FIDS ->")
    print(fids)
    print("FIDM1 ->")
    print(fidm1)
    print("FIDM2 ->")
    print(fidm2)
    form = FlightBookingForm()
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    if frid == "":
        print("Single hop  empty")
    else:
        print("Single hop not empty")
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(id) from database_booking")
        results = cursor.fetchone()
        print(results)
        id = 1
        if results[0] is None:
            id = 1
        else:
            id = results[0] + 1
        cursor.execute("SELECT Price FROM database_flight_route where id=%s", [frid])
        results = cursor.fetchone()
        print("price is ")
        print(results[0])
        Price = results[0]
        cursor.execute("SELECT A.Percentage from database_air_company A JOIN database_flight F "
                       "ON (A.id = F.AirCompany_id) JOIN database_flight_route FR "
                       "ON (FR.Flight_id = F.id) where FR.id=%s", [frid])
        results = cursor.fetchone()
        Percentage = results[0] / 100
        PaidMoney = Percentage * Price * float(adultCount)
        MoneyToPay = Price * float(adultCount) * (1 - Percentage)
        cursor.execute(
            "SELECT Percentage_refunding FROM database_cancellation_policy WHERE id =(SELECT Cancellation_Policy_id FROM database_flight_route where id=%s)",
            [frid])
        results = cursor.fetchone()
        Percentage_refunding = results[0] / 100

        MoneyToRefund = PaidMoney * Percentage_refunding
        MoneyToRefund = PaidMoney * .8
        cursor.execute(
            "INSERT INTO database_booking (id, MoneyToPay, MoneyToRefund, DateOfBooking, DateOfCancellation, User_id,PaidMoney,isCancelled,Status) "
            "VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_DATE,  %s,%s,0,0)",
            [id, MoneyToPay, MoneyToRefund, uid, PaidMoney])
        cursor.execute("SELECT MAX(id) from database_flight_booking")
        results = cursor.fetchone()
        print(results)
        new_id = 1
        if results[0] is None:
            new_id = 1
        else:
            new_id = results[0] + 1
        cursor.execute("INSERT INTO database_flight_booking (id, Booking_id, Flight_id,TotalSeats,isApproved) "
                       "VALUES (%s,%s,%s,%s,0)", [new_id, id, frid, adultCount])
        cursor.execute("UPDATE database_flight_route "
                       "SET TotalSeatsBooked = TotalSeatsBooked + %s "
                       "WHERE id=%s", [adultCount, frid])
        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [frid])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, frid])

        flight = namedtuplefetchall(cursor)

        return render(request, "booking/flightbookingconfirmation.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'False'})

    if id1 == "" and id2 == "":
        print("Multi hop empty")
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(id) from database_booking")
        results = cursor.fetchone()
        print(results)
        id = 1
        if results[0] is None:
            id = 1
        else:
            id = results[0] + 1
            Price = 0
            cursor.execute("SELECT Price FROM database_flight_route where id=%s", [id1])
            results = cursor.fetchone()
            print("price is ")
            print(results[0])
            Price1 = results[0]
            cursor.execute("SELECT Price FROM database_flight_route where id=%s", [id2])

            results = cursor.fetchone()
            print("price is ")
            print(results[0])
            Price2 = results[0]
            cursor.execute("SELECT A.Percentage from database_air_company A JOIN database_flight F "
                           "ON (A.id = F.AirCompany_id) JOIN database_flight_route FR "
                           "ON (FR.Flight_id = F.id) where FR.id=%s", [id1])
            results = cursor.fetchone()
            Percentage = results[0] / 100
            PaidMoney = Percentage * Price1 * float(adultCount)
            MoneyToPay = Price1 * float(adultCount) * (1 - Percentage)
            cursor.execute(
                "SELECT Percentage_refunding FROM database_cancellation_policy WHERE id =(SELECT Cancellation_Policy_id FROM database_flight_route where id=%s)",
                [id1])
            results = cursor.fetchone()
            Percentage_refunding = results[0] / 100

            MoneyToRefund = PaidMoney * Percentage_refunding

            cursor.execute(
                "INSERT INTO database_booking (id, MoneyToPay, MoneyToRefund, DateOfBooking, DateOfCancellation,  User_id, PaidMoney,isCancelled,Status) "
                "VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_DATE,  %s,%s,0,0)",
                [id, MoneyToPay, MoneyToRefund, uid, PaidMoney])

            cursor.execute("SELECT A.Percentage from database_air_company A JOIN database_flight F "
                           "ON (A.id = F.AirCompany_id) JOIN database_flight_route FR "
                           "ON (FR.Flight_id = F.id) where FR.id=%s", [id2])
            results = cursor.fetchone()
            Percentage = results[0] / 100
            PaidMoney = Percentage * Price2 * float(adultCount)
            MoneyToPay = Price2 * float(adultCount) * (1 - Percentage)
            cursor.execute(
                "SELECT Percentage_refunding FROM database_cancellation_policy WHERE id =(SELECT Cancellation_Policy_id FROM database_flight_route where id=%s)",
                [id2])
            results = cursor.fetchone()
            Percentage_refunding = results[0] / 100

            MoneyToRefund = PaidMoney * Percentage_refunding
            cursor.execute(
                "INSERT INTO database_booking (id, MoneyToPay, MoneyToRefund, DateOfBooking, DateOfCancellation, User_id,PaidMoney,isCancelled) "
                "VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_DATE, %s, %s,0)",
                [id + 1, MoneyToPay, MoneyToRefund, uid, PaidMoney])

            cursor.execute("SELECT MAX(id) from database_flight_booking")
            results = cursor.fetchone()
            print(results)
            new_id = 1
            if results[0] is None:
                new_id = 1
            else:
                new_id = results[0] + 1
            cursor.execute("INSERT INTO database_flight_booking (id, Booking_id, Flight_id,TotalSeats,isApproved) "
                           "VALUES (%s,%s,%s,%s,0)", [new_id, id, id1, adultCount])
            new_id = new_id + 1
            cursor.execute("INSERT INTO database_flight_booking (id, Booking_id, Flight_id,TotalSeats,isApproved) "
                           "VALUES (%s,%s,%s,%s,0)", [new_id, id + 1, id2, adultCount])
            cursor.execute("UPDATE database_flight_route "
                           "SET TotalSeatsBooked = TotalSeatsBooked + %s "
                           "WHERE id=%s", [adultCount, id1])
            cursor.execute("UPDATE database_flight_route "
                           "SET TotalSeatsBooked = TotalSeatsBooked + %s "
                           "WHERE id=%s", [adultCount, id2])
            cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                           "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                           "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                           "WHERE FR.id = %s", [id1])
            aircompany = namedtuplefetchall(cursor)

            cursor.execute(
                "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
                "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
                "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
                [adultCount, id1])

            flight = namedtuplefetchall(cursor)

            cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                           "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                           "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                           "WHERE FR.id = %s", [id2])
            aircompany2 = namedtuplefetchall(cursor)

            cursor.execute(
                "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
                "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
                "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
                [adultCount, id2])

            flight2 = namedtuplefetchall(cursor)
            return render(request, "booking/flightbookingconfirmation.html",
                          {'flight': flight[0], 'aircompany': aircompany[0], 'flight2': flight2[0],
                           'aircompany2': aircompany2[0], 'form': form, 'hotelform': hotelform,
                           'flightform': flightform, 'multi': 'True'})
