import logging

from farpenpy import Report
from farpenpy.subreports.apportionment import ApportionmentItem


def test_load_farpen_document(caplog):
    caplog.set_level(logging.INFO)

    report = Report(filename="./tests/report.pdf")
    available_reports = report.process()

    assert len(available_reports["ApportionmentSubReport"]) > 0
    assert isinstance(available_reports["ApportionmentSubReport"][0], ApportionmentItem)

    assert isinstance(
        available_reports["ApportionmentSubReport"][0].valor11_total, float
    )
