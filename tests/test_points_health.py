#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦麦积分管家 · 单元测试
覆盖账户体检与抽奖评估的边界情况。纯标准库，运行：
    python tests/test_points_health.py
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill", "scripts"))
from points_health import health_report, lottery_value, mall_rank  # noqa: E402


class TestHealthReport(unittest.TestCase):
    def test_zero_balance_gray(self):
        r = health_report({"availablePoint": "0", "frozenPoint": "0",
                           "currentMouthExpirePoint": "0"})
        self.assertEqual(r["risk_color"], "灰")
        self.assertEqual(r["risk_level"], "空仓")

    def test_no_expiring_green(self):
        r = health_report({"availablePoint": "5200", "currentMouthExpirePoint": "0"})
        self.assertEqual(r["risk_color"], "绿")

    def test_yellow_band_10_to_30(self):
        # 620/3120 ≈ 19.9% → 黄
        r = health_report({"availablePoint": "3120", "currentMouthExpirePoint": "620"})
        self.assertEqual(r["risk_color"], "黄")

    def test_red_band_over_30(self):
        # 1100/2400 ≈ 45.8% → 红
        r = health_report({"availablePoint": "2400", "currentMouthExpirePoint": "1100"})
        self.assertEqual(r["risk_color"], "红")

    def test_expiring_exceeds_available(self):
        # 数据异常：过期 > 可用，比例应封顶 100%，不得报错
        r = health_report({"availablePoint": "500", "currentMouthExpirePoint": "900"})
        self.assertEqual(r["expiring_ratio"], 1.0)
        self.assertEqual(r["risk_color"], "红")

    def test_string_and_float_inputs(self):
        r = health_report({"availablePoint": "3120.7", "currentMouthExpirePoint": 620})
        self.assertEqual(r["available"], 3120)

    def test_total_includes_frozen(self):
        r = health_report({"availablePoint": "100", "frozenPoint": "50"})
        self.assertEqual(r["total"], 150)

    def test_missing_fields_default_zero(self):
        r = health_report({})
        self.assertEqual(r["total"], 0)
        self.assertEqual(r["risk_color"], "灰")


class TestLotteryValue(unittest.TestCase):
    def test_expected_value_with_weights(self):
        lot = {"drawPoint": "100", "prizes": [
            {"name": "A", "value": 200, "weight": 1},
            {"name": "B", "value": 0, "weight": 1},
        ]}
        r = lottery_value(lot)
        self.assertEqual(r["expected_value"], 100.0)
        self.assertIn("持平", r["verdict"])

    def test_bad_lottery(self):
        lot = {"drawPoint": "100", "prizes": [{"name": "A", "value": 5, "weight": 1}]}
        self.assertIn("不划算", lottery_value(lot)["verdict"])

    def test_no_probability_data(self):
        lot = {"drawPoint": "100", "prizes": [{"name": "A", "value": 5}]}
        r = lottery_value(lot)
        self.assertIsNone(r["expected_value"])
        self.assertIn("无法计算", r["note"])

    def test_empty_prizes(self):
        r = lottery_value({"drawPoint": "100", "prizes": []})
        self.assertIsNone(r["expected_value"])


class TestMallRank(unittest.TestCase):
    def test_only_on_shelf_sorted(self):
        products = [
            {"spuName": "A", "point": "300", "status": 2},
            {"spuName": "B", "point": "100", "status": 2},
            {"spuName": "下架", "point": "1", "status": 4},
            {"spuName": "售罄", "point": "1", "status": 3},
        ]
        top = mall_rank(products)
        self.assertEqual([t["name"] for t in top], ["B", "A"])

    def test_top_n(self):
        products = [{"spuName": f"P{i}", "point": str(100 + i), "status": 2} for i in range(8)]
        self.assertEqual(len(mall_rank(products, top_n=5)), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
