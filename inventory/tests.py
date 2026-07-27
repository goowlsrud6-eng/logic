import pandas as pd
from django.test import SimpleTestCase

from .services import (
    extract_purchase_order_number,
    order_label_from_number,
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
