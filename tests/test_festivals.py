"""Festival tours on the home page always show their next dates."""
from datetime import date

from itihaas.data.festivals import FESTIVAL_TOURS, upcoming_festival_tours


def by_key(today):
    return {tour.key: tour for tour in upcoming_festival_tours(today)}


def test_every_tour_is_current_or_upcoming():
    today = date(2026, 11, 8)
    tours = upcoming_festival_tours(today)
    assert len(tours) == len(FESTIVAL_TOURS)
    assert all(tour.end >= today for tour in tours)
    assert [tour.start for tour in tours] == sorted(tour.start for tour in tours)


def test_passed_festival_rolls_to_next_year():
    holi = by_key(date(2026, 11, 8))["holi"]
    assert (holi.start, holi.end) == (date(2027, 3, 25), date(2027, 3, 27))


def test_ongoing_festival_stays_this_year():
    diwali = by_key(date(2026, 11, 8))["diwali"]
    assert diwali.start == date(2026, 10, 15) and diwali.start <= date(2026, 11, 8) <= diwali.end


def test_christmas_wraps_into_new_year():
    christmas = by_key(date(2026, 6, 1))["christmas"]
    assert (christmas.start, christmas.end) == (date(2026, 12, 23), date(2027, 1, 1))
    assert christmas.days == 10
    assert christmas.date_range == "23 Dec – 1 Jan"
    # On 1 January the trip that began last December is still on.
    assert by_key(date(2027, 1, 1))["christmas"].start == date(2026, 12, 23)


def test_date_range_formats():
    tours = by_key(date(2026, 1, 1))
    assert tours["sankranti"].date_range == "14–16 Jan"
    assert tours["navratri"].date_range == "21 Sep – 24 Oct"


def test_home_page_shows_festivals_and_signature(client):
    page = client.get("/").get_data(as_text=True)
    assert "Visit India's monuments with the people who know them" in page
    assert "27.1751° N, 78.0421° E" in page
    assert page.count('class="festival"') == len(FESTIVAL_TOURS)
    assert "bg-audio" not in page  # no autoplaying audio
