from django.db import connection
from collections import namedtuple
from datetime import datetime
from django.utils.encoding import smart_str
from geopy import geocoders
from geopy.exc import GeocoderServiceError

EASY_MAPS_GOOGLE_KEY = "AIzaSyATg_isuGSCHIlJamrxAXfkFDTYhIz7ytM"


def google_v3(address):
    try:
        g = geocoders.GoogleV3(EASY_MAPS_GOOGLE_KEY)
        results = g.geocode(smart_str(address), exactly_one=False)
        if results is not None:
            return results[0]
        else:
            return "notfound"
    except (UnboundLocalError, ValueError, GeocoderServiceError) as e:
        return "notfound"


def daysBetween(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


dest = 'panthapath'
roomCount = 1
dest = '%' + dest + '%'
latitudeR = 0
longitudeR = 0
rr = google_v3(dest)
if rr != "notfound":
    r = rr[1]
    latitudeR = r[0] * 0.0174533
    longitudeR = r[1] * 0.0174533
cursor = connection.cursor()
cursor.execute("SELECT H.Hotel_Name,H.Address,H.Hotel_Location,H.Hotel_Country,H.Description,HR.FreeRoomCount"
               " as 'Num', min(HR.Price)*%s as 'Price', H.CompanyAdmin_id as ID , H.id as HID  FROM "
               "database_hotel_room HR  join database_hotel H on(HR.Hotel_id=H.id) where (lower(H.Hotel_Name) "
               "Like %s OR lower(H.Hotel_Location) Like %s OR lower(H.Hotel_Country) Like %s OR "
               "lower(H.Address) Like %s OR (acos(sin(%s) * sin(radians(H.Latitude)) + "
               "cos(%s) * cos(radians(H.Latitude)) * cos(radians(H.Longitude) - (%s))) * 6371 <= 5)) "
               "and Num >= %s GROUP BY H.Hotel_Name",
               [int(roomCount), dest, dest, dest, dest, latitudeR, latitudeR, longitudeR, int(roomCount)])
hotels = namedtuplefetchall(cursor)
for h in hotels:
    print(h.Hotel_Name)
