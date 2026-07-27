import pandas as pd
from django.test import SimpleTestCase

from .services import (
    build_column_map,
    extract_purchase_order_number,
    order_label_from_number,
    parse_date,
    split_ecount_product_option,
)


class PurchaseOrderFormatTests(SimpleTestCase):
    def test_extracts_order_number_from_ecount_document_header(self):
        raw = pd.DataFrame([
            ['발주서', None, None],
            ['전표번호 : 20260605-2', None, None],
            ['수신·거래처 : YIWU', None, None],
        ])

        self.assertEqual(extract_purchase_order_number(raw), '20260605-2')

    def test_extracts_order_number_from_adjacent_cell(self):
        raw = pd.DataFrame([['전표번호', '20260709-2']])

        self.assertEqual(extract_purchase_order_number(raw), '20260709-2')

    def test_splits_combined_product_and_option(self):
        product, option = split_ecount_product_option(
            'ECLL 캐리어파우치 7종1세트_AB [디즈니옐로우]'
        )

        self.assertEqual(product, 'ECLL 캐리어파우치 7종1세트_AB')
        self.assertEqual(option, '디즈니옐로우')

    def test_formats_order_label_without_changing_stored_number(self):
        order_number = '20260709-2'

        self.assertEqual(order_label_from_number(order_number), '7/9 발주')
        self.assertEqual(order_number, '20260709-2')


class InboundScheduleFormatTests(SimpleTestCase):
    def test_maps_new_detailed_inbound_headers(self):
        columns = ['상품코드', '이지어드민 상품코드', '상품명', '옵션명', '입고 예정일', '수량', '비고']

        mapped = build_column_map(columns)

        self.assertEqual(mapped['product_code'], '상품코드')
        self.assertEqual(mapped['supplier_option_name'], '이지어드민 상품코드')
        self.assertEqual(mapped['product_name'], '상품명')
        self.assertEqual(mapped['option_name'], '옵션명')
        self.assertEqual(mapped['inbound_date'], '입고 예정일')
        self.assertEqual(mapped['inbound_qty'], '수량')
        self.assertEqual(mapped['memo'], '비고')

    def test_parses_iso_inbound_date(self):
        self.assertEqual(str(parse_date('2026-07-23')), '2026-07-23')
