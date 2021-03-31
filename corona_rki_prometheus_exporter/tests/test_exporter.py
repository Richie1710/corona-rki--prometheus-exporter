from prometheus_client import Gauge  # type: ignore
import exporter # type: ignore


def test_getcorona_information_from_rki():
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
    args = exporter.parse_arguments(["TEST"])
    assert args.gen == "TEST"


def test_process_request(mocker):

    EWZ = Gauge("EWZ_Bautzen", "Einwohnerzahl Bautzen")
    EWZ_BL = Gauge("EWZ_Sachsen", "Einwohnerzahl Sachsen")
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
        "exporter.getcorona_information_from_rki",
        return_value={
            "features": [
                {
                    "attributes": {
                        "EWZ_BL": 1,
                        "EWZ": 2,
                        "cases": 3,
                        "death": 4,
                        "cases7_per_100k": 5,
                        "cases7_bl_per_100k": 6,
                    }
                }
            ]
        },
    )

    for gauge in (
        (EWZ, "EWZ"),
        (EWZ_BL, "EWZ_BL"),
        (cases, "cases"),
        (death, "death"),
        (cases7_per_100k, "cases7_per_100k"),
        (cases7_bl_per_100k, "cases7_bl_per_100k"),
    ):
        exporter.process_request(gauge[0], gauge[1])
    assert EWZ_BL._value._value == 1
    assert EWZ._value._value == 2
    assert cases._value._value == 3
    assert death._value._value == 4
    assert cases7_per_100k._value._value == 5
    assert cases7_bl_per_100k._value._value == 6
