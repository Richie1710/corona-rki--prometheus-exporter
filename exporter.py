import time
import requests

from prometheus_client import Gauge, start_http_server, REGISTRY
GEN = "Bautzen"


def getcorona_information_from_rki(gen: str) -> str:
    """Get Corona Information from RKI and returns as json

    Args:
        gen (str): Name of district to search for

    Returns:
        any: json data
    """
    url = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/\
rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=\
GEN%20%3D%20'{}'&outFields=EWZ_BL,EWZ,cases_per_population,cases,\
deaths,death_rate,cases7_per_100k,cases7_bl_per_100k,cases7_bl,\
death7_bl,cases7_lk,death7_lk,cases7_per_100k_txt&\
returnGeometry=false&outSR=4326&f=json".format(gen)
    req = requests.get(url)
    req.raise_for_status()
    return req.json()


def process_request(gaugename: Gauge, api_name: str, corona_data=None):
    """Write Data to gauge

    Args:
        gaugename (Gauge): Prometheus Gauge
        api_name (str): Name of API in RKI Json Data
        corona_data (str(json)), optional): Json Data from RKI. If no data \
        given it will fetch new. Defaults to None.
    """
    if not corona_data:
        corona_data = getcorona_information_from_rki(GEN)
    featuredata = corona_data["features"][0]["attributes"]
    gaugename.set(featuredata[api_name])


if __name__ == '__main__':
    for coll in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(coll)
    EWZ = Gauge('EWZ_Bautzen', 'Einwohnerzahl Bautzen')
    EWZ_BL = Gauge('EWZ_Sachsen', 'Einwohnerzahl Sachsen')
    cases = Gauge('Coronafaelle_Bautzen', 'Coronafälle in Bautzen')
    death = Gauge('Todesfaelle_Bautzen', 'Todesfälle Bautzen')
    cases7_per_100k = Gauge('Inzidenz_bautzen', 'Inzidenzwert auf 100.000 \
        Einwohner Bautzen')
    cases7_bl_per_100k = Gauge('Inzidenz_Sachsen', 'Inzidenzwert auf 100.000 \
        Einwohner Sachsen')
    start_http_server(8000)
    while True:
        corona_data = getcorona_information_from_rki(GEN)
        for gauge in ((EWZ, "EWZ"), (EWZ_BL, "EWZ_BL"), (cases, "cases"),
                      (death, "death"), (cases7_per_100k, "cases7_per_100k"),
                      (cases7_bl_per_100k, "cases7_bl_per_100k")):
            process_request(gauge[0], gauge[1], corona_data)
        time.sleep(300)
