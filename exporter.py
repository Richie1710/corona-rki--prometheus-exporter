"""
Provides an exporter for corona data
"""

import time
import requests
import argparse
import sys

from prometheus_client import Gauge, start_http_server, REGISTRY


def parse_arguments(arguments):
    """Parse Arguments

    Args:
        args (sys.argv): Arguments of script call
    """
    parser = argparse.ArgumentParser(
        description="get corona \
inzidenz from RKI"
    )
    parser.add_argument("gen", type=str, help="name of state", default="Bautzen")
    args = parser.parse_args(arguments)
    return args


def getcorona_information_from_rki(gen: str = "Bautzen") -> str:
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
returnGeometry=false&outSR=4326&f=json".format(
        gen
    )
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
        corona_data = getcorona_information_from_rki()
    featuredata = corona_data["features"][0]["attributes"]
    gaugename.set(featuredata[api_name])


if __name__ == "__main__":

    args = parse_arguments(sys.argv[1:])
    gen = args.gen
    for coll in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(coll)
    EWZ = Gauge("EWZ_{}".format(gen), "Einwohnerzahl {}".format(gen))
    EWZ_BL = Gauge("EWZ_BL", "Einwohnerzahl Bundesland")
    cases = Gauge("Coronafaelle_{}".format(gen), "Coronafälle in {}".format(gen))
    death = Gauge("Todesfaelle_{}".format(gen), "Todesfälle {}".format(gen))
    cases7_per_100k = Gauge(
        "Inzidenz_{}".format(gen),
        "Inzidenzwert auf 100.000 \
        Einwohner Bautzen",
    )
    cases7_bl_per_100k = Gauge(
        "Inzidenz_BL",
        "Inzidenzwert auf 100.000 \
        Einwohner BL",
    )
    start_http_server(8000)
    while True:
        corona_data = getcorona_information_from_rki(gen)
        for gauge in (
            (EWZ, "EWZ"),
            (EWZ_BL, "EWZ_BL"),
            (cases, "cases"),
            (death, "deaths"),
            (cases7_per_100k, "cases7_per_100k"),
            (cases7_bl_per_100k, "cases7_bl_per_100k"),
        ):
            process_request(gauge[0], gauge[1], corona_data)
        time.sleep(300)
