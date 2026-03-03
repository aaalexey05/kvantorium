import json
import re
from urllib.parse import parse_qs, quote_plus, unquote, urlencode, urlparse
from urllib.request import Request, urlopen


FALLBACK_CITY = "Барнаул"


def _google_embed(query: str):
    return f"https://www.google.com/maps?q={quote_plus(query)}&output=embed"


def _looks_like_embed(map_url: str):
    value = (map_url or "").strip().lower()
    return bool(value) and ("/embed" in value or "output=embed" in value)


def _basic_address_valid(address: str):
    value = (address or "").strip()
    if len(value) < 8:
        return False
    if value.count(" ") < 1:
        return False
    return True


def _nominatim_geocode(address: str):
    query = urlencode({"q": address, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{query}"
    request = Request(
        url,
        headers={
            "User-Agent": "kvantorium-lms/1.0 (contact-map-preview)",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=2.5) as response:
        data = json.loads(response.read().decode("utf-8"))
        if not data:
            return None
        first = data[0]
        lat = first.get("lat")
        lon = first.get("lon")
        if not lat or not lon:
            return None
        return {"lat": lat, "lon": lon, "display_name": first.get("display_name", "")}


def _extract_google_query(raw_map_url: str):
    parsed = urlparse(raw_map_url)
    query = parse_qs(parsed.query)

    q_value = (query.get("q", [None])[0] or query.get("query", [None])[0] or "").strip()
    if q_value:
        return q_value

    path = unquote(parsed.path or "")
    if "/place/" in path:
        place_part = path.split("/place/", 1)[1].split("/", 1)[0]
        if place_part:
            return place_part.replace("+", " ")

    coord_match = re.search(r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)", path)
    if coord_match:
        return f"{coord_match.group(1)},{coord_match.group(2)}"
    return ""


def _normalize_embed_url(raw_map_url: str):
    value = (raw_map_url or "").strip()
    if not value:
        return "", ""

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        return "", "Ссылка карты должна начинаться с http:// или https://."

    host = parsed.netloc.lower()
    query = parse_qs(parsed.query)

    if "google." in host:
        if "/maps/embed" in parsed.path:
            pb_value = (query.get("pb", [""])[0] or "").strip()
            if pb_value:
                return "", "Embed-ссылка c параметром pb нестабильна. Используем адрес."

        google_query = _extract_google_query(value)
        if google_query:
            return _google_embed(google_query), ""
        return "", "Не удалось распознать ссылку Google Maps. Используем адрес."

    if _looks_like_embed(value):
        return value, ""

    return "", "Ссылка карты не распознана, используем адрес из формы."


def build_contact_map_context(address: str, map_url: str, fallback_city: str = FALLBACK_CITY):
    raw_address = (address or "").strip()
    raw_map_url = (map_url or "").strip()

    normalized_embed_url, map_url_notice = _normalize_embed_url(raw_map_url)
    if normalized_embed_url:
        return {
            "embed_url": normalized_embed_url,
            "map_valid": True,
            "map_notice": "",
            "resolved_address": raw_address or fallback_city,
        }

    if not raw_address:
        return {
            "embed_url": _google_embed(fallback_city),
            "map_valid": False,
            "map_notice": map_url_notice or "Введите адрес: пока показывается карта города по умолчанию.",
            "resolved_address": fallback_city,
        }

    if not _basic_address_valid(raw_address):
        return {
            "embed_url": _google_embed(raw_address),
            "map_valid": True,
            "map_notice": map_url_notice or "Показана приблизительная точка. Можно уточнить улицу и дом.",
            "resolved_address": raw_address,
        }

    geocode_failed = False
    try:
        geo = _nominatim_geocode(raw_address)
    except Exception:
        geo = None
        geocode_failed = True

    if geocode_failed:
        return {
            "embed_url": _google_embed(raw_address),
            "map_valid": True,
            "map_notice": map_url_notice if raw_map_url and map_url_notice else "",
            "resolved_address": raw_address,
        }

    if not geo:
        return {
            "embed_url": _google_embed(raw_address),
            "map_valid": True,
            "map_notice": map_url_notice or "Не удалось точно определить координаты, показан поиск по адресу.",
            "resolved_address": raw_address,
        }

    lat_lon = f"{geo['lat']},{geo['lon']}"
    return {
        "embed_url": _google_embed(lat_lon),
        "map_valid": True,
        "map_notice": map_url_notice if raw_map_url and map_url_notice else "",
        "resolved_address": geo.get("display_name") or raw_address,
    }
