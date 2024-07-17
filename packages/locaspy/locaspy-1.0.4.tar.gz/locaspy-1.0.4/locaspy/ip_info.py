import requests

def get_ip():
    try:
        response = requests.get('http://ipinfo.io/json')
        info = response.json()
        return info['ip']
    except requests.exceptions.RequestException:
        return None

def get_data(ip_address, data_type=None):
    try:
        response = requests.get(f'http://ipinfo.io/{ip_address}/json')
        info = response.json()

        lat, lon = info.get('loc').split(',')

        weather_response = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true')
        weather_info = weather_response.json()

        osm_url = f'https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}'

        data = {
            "ip_address": info.get('ip'),
            "city": info.get('city'),
            "region": info.get('region'),
            "country": info.get('country'),
            "country_code": info.get('country'),
            "isp": info.get('org'),
            "languages": info.get('languages', 'N/A'),
            "postal_code": info.get('postal', 'N/A'),
            "latitude": lat,
            "longitude": lon,
            "url": osm_url,
            "currency": info.get('currency', 'N/A'),
            "temperature": weather_info['current_weather']['temperature'],
            "weather": weather_info['current_weather']['weathercode']
        }

        if data_type:
            return {key: data[key] for key in data if key.startswith(data_type)}

        return data

    except requests.exceptions.RequestException:
        return None
