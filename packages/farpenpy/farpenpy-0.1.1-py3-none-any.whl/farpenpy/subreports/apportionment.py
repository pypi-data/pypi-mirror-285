import re
from decimal import Decimal
from typing import Annotated, List

from pydantic import BaseModel, PlainSerializer

from farpenpy.subreports import SubReport

DecimalField = Annotated[
    float, PlainSerializer(lambda x: Decimal(x), return_type=Decimal)
]


class ApportionmentItem(BaseModel):
    codigo: str
    cns: str
    nome: str
    comarca: str
    valor1_proprios: DecimalField
    valor2_comp: DecimalField
    valor3_receb: DecimalField
    valor4_total_atos: DecimalField
    valor5_rateio: DecimalField
    valor6_total_rat: DecimalField
    valor7_outros: DecimalField
    valor8_sub_total: DecimalField
    valor9_compl: DecimalField
    valor10_proj_cid: DecimalField
    qtds_pc: str
    valor11_total: DecimalField
    valor12_atos_pagos: DecimalField
    valor13_rend_totais: DecimalField


class ApportionmentSubReport(SubReport):
    def __init__(self) -> None:
        super().__init__()
        self._regex_apportionment = (
            r"(?i)^(?P<codigo>\d+) "
            r"+(?P<cns>\d+) +(?P<nome>RCPN  ([-'0-9a-zÀ-ÿ]+?\s{1})+)\s{2,}(?P<"
            r"comarca>([-'0-9a-zÀ-ÿ]+?\s{1})+)\s{2,}R\$ (?P<valor1_proprios>[0"
            r"-9.,]+) +R\$ (?P<valor2_comp>[0-9.,]+) +R\$ (?P<valor3_receb>[0-"
            r"9.,]+) +R\$ (?P<valor4_total_atos>[0-9.,]+) +R\$ (?P<valor5_rate"
            r"io>[0-9.,]+) +R\$ (?P<valor6_total_rat>[0-9.,]+) +R\$ (?P<valor7"
            r"_outros>[0-9.,]+) +R\$ (?P<valor8_sub_total>[0-9.,]+) +R\$ (?P<v"
            r"alor9_compl>[0-9.,]+) +R\$ (?P<valor10_proj_cid>[0-9.,]+) +\((?P"
            r"<qtds_pc>[A-Z0-9\-]+)\) +R\$ (?P<valor11_total>[0-9.,]+) +R\$ (?"
            r"P<valor12_atos_pagos>[0-9.,]+) +R\$ (?P<valor13_rend_totais>[0-9"
            r".,]+)$"
        )

    def trigger(self, page_data) -> bool:
        return page_data[0].endswith("Relatório de Rateio")

    def handler(self, page_data) -> List[ApportionmentItem]:
        found_data = []

        def to_decimal(value) -> Decimal:
            return Decimal(value.replace(".", "").replace(",", "."))

        for line in page_data:
            match = re.match(self._regex_apportionment, line)
            if match:
                item = ApportionmentItem(
                    codigo=match["codigo"],
                    cns=match["cns"],
                    nome=match["nome"],
                    comarca=match["comarca"],
                    valor1_proprios=to_decimal(match["valor1_proprios"]),
                    valor2_comp=to_decimal(match["valor2_comp"]),
                    valor3_receb=to_decimal(match["valor3_receb"]),
                    valor4_total_atos=to_decimal(match["valor4_total_atos"]),
                    valor5_rateio=to_decimal(match["valor5_rateio"]),
                    valor6_total_rat=to_decimal(match["valor6_total_rat"]),
                    valor7_outros=to_decimal(match["valor7_outros"]),
                    valor8_sub_total=to_decimal(match["valor8_sub_total"]),
                    valor9_compl=to_decimal(match["valor9_compl"]),
                    valor10_proj_cid=to_decimal(match["valor10_proj_cid"]),
                    qtds_pc=match["qtds_pc"],
                    valor11_total=to_decimal(match["valor11_total"]),
                    valor12_atos_pagos=to_decimal(match["valor12_atos_pagos"]),
                    valor13_rend_totais=(to_decimal(match["valor13_rend_totais"])),
                )

                found_data.append(item)

        return found_data
