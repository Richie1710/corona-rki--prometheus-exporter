"""
This file keeps tests for corona_rki_prometheus_exporter
"""
import sys

sys.path.append("corona_rki_prometheus_exporter")
import exporter  # noqa: E402 # pylint: disable=C0413
from prometheus_client import Gauge  # type: ignore # pylint: disable=C0413,E0401  # noqa:402


def test_getcorona_information_from_rki():
    """
    Tests the getting of information from rki
    """
    response_bautzen = exporter.getcorona_information_from_rki("Bautzen")
    assert len(response_bautzen["features"]) > 0
    response_noneexisting = exporter.getcorona_information_from_rki(
        "Not \
        existing State"
    )
    assert len(response_noneexisting["features"]) == 0
    response_eichsfeld = exporter.getcorona_information_from_rki("Eichsfeld")
    assert len(response_eichsfeld["features"]) > 0
    assert response_eichsfeld["features"] != response_bautzen["features"]


def test_argument_parseing():
    """Tests the argument parsing
    """
    args = exporter.parse_arguments(["TEST"])
    assert args.gen == "TEST"


def test_process_request(mocker):
    """Tests the request processing
    """

    ewz = Gauge("EWZ_Bautzen", "Einwohnerzahl Bautzen")
    ewz_bl = Gauge("EWZ_Sachsen", "Einwohnerzahl Sachsen")
    cases = Gauge("Coronafaelle_Bautzen", "Coronafälle in Bautzen")
    death = Gauge("Todesfaelle_Bautzen", "Todesfälle Bautzen")
    cases7_per_100k = Gauge(
        "Inzidenz_bautzen",
        "Inzidenzwert auf 100.000 \
        Einwohner Bautzen",
    )
    cases7_bl_per_100k = Gauge(
        "Inzidenz_Sachsen",
        "Inzidenzwert auf 100.000 \
        Einwohner Sachsen",
    )
    mocker.patch(
        "exporter.getcorona_information_from_rki", return_value={"features": [{"attributes": {"EWZ_BL": 1, "EWZ": 2, "cases": 3, "death": 4, "cases7_per_100k": 5, "cases7_bl_per_100k": 6}}]},
    )

    for gauge in (
        (ewz, "EWZ"),
        (ewz_bl, "EWZ_BL"),
        (cases, "cases"),
        (death, "death"),
        (cases7_per_100k, "cases7_per_100k"),
        (cases7_bl_per_100k, "cases7_bl_per_100k"),
    ):
        exporter.process_request(gauge[0], gauge[1])
    # disable pylint W0212 because there is no getter function for getting values
    assert ewz_bl._value._value == 1  # pylint: disable=W0212
    assert ewz._value._value == 2  # pylint: disable=W0212
    assert cases._value._value == 3  # pylint: disable=W0212
    assert death._value._value == 4  # pylint: disable=W0212
    assert cases7_per_100k._value._value == 5  # pylint: disable=W0212
    assert cases7_bl_per_100k._value._value == 6  # pylint: disable=W0212
