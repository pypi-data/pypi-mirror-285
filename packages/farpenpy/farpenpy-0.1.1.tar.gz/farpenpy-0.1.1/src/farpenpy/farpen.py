from collections import defaultdict
from typing import List

from pypdf import PdfReader

from farpenpy.logger import log
from farpenpy.subreports import SubReport
from farpenpy.subreports.apportionment import ApportionmentSubReport


class Report:
    def __init__(self, filename):
        log.info(f"Load Farpen PDF file {filename}")
        self._reader = PdfReader(filename)
        self._enabled_subreports: List[SubReport] = [ApportionmentSubReport()]

    def process(self):
        sub_reports = defaultdict(list)

        for idx, current_page in enumerate(self._reader.pages):
            data = current_page.extract_text(extraction_mode="layout")
            data = data.split("\n")

            for sub_report in self._enabled_subreports:
                sub_reports[sub_report.__class__.__name__].extend(
                    sub_report.process(data)
                )

            log.debug(f"Report - processed page {idx=}")

        log.info("Report - All pages processed")

        return sub_reports
