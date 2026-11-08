"""Festival tours shown on the home page.

Dates are the approximate windows the tours run each year (several of these
festivals follow lunar calendars, so real dates shift a little year to year).
:func:`upcoming_festival_tours` returns each tour with its *next* occurrence,
so a festival that has already passed this year is offered for next year.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

INCLUSIONS = [
    "Accommodation in premium hotels",
    "Daily breakfast and dinner",
    "All transfers and sightseeing",
    "Professional tour guide",
    "Entry fees to monuments",
    "Cultural performances",
    "Festival special activities",
]

# key, title, package name (kept for the booking hand-off), season, places,
# photo, (start month, day), (end month, day), price in ₹, description, itinerary
FESTIVAL_TOURS = [
    ("sankranti", "Sankranti & Pongal", "Sankranti & Pongal Special", "Winter", "Tamil Nadu & Gujarat",
     "media/pongal.jpg", (1, 14), (1, 16), 15000,
     "Experience the harvest festivals of Tamil Nadu and Gujarat with traditional celebrations, kite flying and cultural performances.",
     ["Day 1: Arrival in Chennai, temple visit", "Day 2: Pongal celebrations, cultural programme", "Day 3: Departure"]),
    ("republic", "Republic Day", "Republic Day Special", "Winter", "Delhi & Agra",
     "media/republic-day-parade.jpg", (1, 26), (1, 28), 15000,
     "Witness the Republic Day parade in Delhi and explore the historic monuments of Agra.",
     ["Day 1: Republic Day parade", "Day 2: Delhi city tour", "Day 3: Taj Mahal visit"]),
    ("holi", "Holi", "Holi Special", "Spring", "Jaipur & Hampi",
     "media/holi.jpg", (3, 25), (3, 27), 12000,
     "Celebrate the festival of colours in Jaipur and explore the ruins of Hampi.",
     ["Day 1: Arrival in Jaipur", "Day 2: Holi celebrations", "Day 3: Hampi exploration"]),
    ("ram-navami", "Ram Navami & Baisakhi", "Ram Navami & Baisakhi", "Spring", "Ajanta & Sanchi",
     "media/ram-mandir-ayodhya.jpg", (5, 5), (5, 6), 12000,
     "Visit sacred temples and experience the spiritual atmosphere of these two festivals.",
     ["Day 1: Temple visits", "Day 2: Festival celebrations", "Day 3: Cultural programmes"]),
    ("independence", "Independence Day", "Independence Day Special", "Monsoon", "Delhi & Agra",
     "media/india-gate-evening.jpg", (8, 15), (8, 17), 10000,
     "Be part of the Independence Day celebrations in Delhi and visit the Taj Mahal.",
     ["Day 1: Flag hoisting ceremony", "Day 2: Delhi heritage tour", "Day 3: Agra visit"]),
    ("ganesh", "Ganesh Chaturthi", "Ganesh Chaturthi Special", "Monsoon", "Mumbai",
     "media/ganesh-chaturthi.jpg", (9, 7), (9, 18), 10000,
     "Experience the Ganesh Chaturthi celebrations in Mumbai with their processions.",
     ["Day 1: Arrival in Mumbai", "Day 2: Ganesh Visarjan", "Day 3: City tour"]),
    ("navratri", "Navratri & Durga Puja", "Navratri & Durga Puja", "Autumn", "Ahmedabad & Hampi",
     "media/akshardham-delhi.jpg", (9, 21), (10, 24), 13000,
     "Dance to Garba in Ahmedabad and see the Durga Puja celebrations.",
     ["Day 1: Garba night", "Day 2: Durga Puja celebrations", "Day 3: Cultural programmes"]),
    ("diwali", "Diwali", "Festival of Lights Tour", "Autumn", "Taj Mahal & Red Fort",
     "media/red-fort-night.jpg", (10, 15), (11, 15), 18000,
     "Experience Diwali celebrations at the Taj Mahal and the Red Fort.",
     ["Day 1: Diwali celebrations", "Day 2: Taj Mahal visit", "Day 3: Red Fort tour"]),
    ("christmas", "Christmas & New Year", "Christmas & New Year", "Winter", "Goa & Mumbai",
     "media/se-cathedral-goa.jpg", (12, 23), (1, 1), 15000,
     "Celebrate Christmas and New Year in Goa and Mumbai.",
     ["Day 1: Christmas celebrations", "Day 2: Beach activities", "Day 3: New Year celebrations"]),
]


@dataclass(frozen=True)
class FestivalTour:
    key: str
    title: str
    package_name: str
    season: str
    places: str
    photo: str
    start: date
    end: date
    price: int
    description: str
    itinerary: list[str]

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    @property
    def date_range(self) -> str:
        """Compact range like '14–16 Jan', '21 Sep – 24 Oct' or '23 Dec – 1 Jan'."""
        if (self.start.year, self.start.month) == (self.end.year, self.end.month):
            return f"{self.start.day}–{self.end.day} {self.start:%b}"
        return f"{self.start.day} {self.start:%b} – {self.end.day} {self.end:%b}"

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "title": self.title,
            "packageName": self.package_name,
            "season": self.season,
            "places": self.places,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "days": self.days,
            "price": self.price,
            "description": self.description,
            "itinerary": self.itinerary,
            "inclusions": INCLUSIONS,
        }


def _occurrence(year: int, start_md: tuple[int, int], end_md: tuple[int, int]) -> tuple[date, date]:
    start = date(year, *start_md)
    end_year = year + 1 if end_md < start_md else year  # e.g. 23 Dec – 1 Jan
    return start, date(end_year, *end_md)


def upcoming_festival_tours(today: date) -> list[FestivalTour]:
    """Every tour at its next occurrence (ongoing ones included), soonest first."""
    tours = []
    for key, title, package, season, places, photo, start_md, end_md, price, description, itinerary in FESTIVAL_TOURS:
        # A tour that wraps the year (23 Dec – 1 Jan) may still be running from last year.
        start, end = _occurrence(today.year - 1, start_md, end_md)
        if end < today:
            start, end = _occurrence(today.year, start_md, end_md)
        if end < today:
            start, end = _occurrence(today.year + 1, start_md, end_md)
        tours.append(FestivalTour(key, title, package, season, places, photo, start, end, price, description, itinerary))
    return sorted(tours, key=lambda tour: tour.start)
