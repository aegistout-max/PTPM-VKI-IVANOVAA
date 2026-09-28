import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from delivery_service import calculate_delivery_cost

ERROR = (-1, "0000-00-00")


class TestDeliveryLimits(unittest.TestCase):
    def test_rejects_weight_below_minimum(self):
        self.assertEqual(calculate_delivery_cost(0.09, 100, "обычный"), ERROR)

    def test_rejects_weight_above_maximum(self):
        self.assertEqual(calculate_delivery_cost(50.1, 100, "обычный"), ERROR)

    def test_rejects_distance_below_minimum(self):
        self.assertEqual(calculate_delivery_cost(1, 0, "обычный"), ERROR)

    def test_rejects_distance_above_maximum(self):
        self.assertEqual(calculate_delivery_cost(1, 5001, "обычный"), ERROR)

    def test_rejects_unknown_package_type(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "коробка"), ERROR)

    def test_rejects_package_type_in_wrong_case(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "Обычный"), ERROR)

    def test_rejects_empty_package_type(self):
        self.assertEqual(calculate_delivery_cost(1, 100, ""), ERROR)

    def test_accepts_minimum_weight(self):
        self.assertEqual(calculate_delivery_cost(0.1, 1, "обычный"), (205, "2026-09-04"))

    def test_accepts_maximum_weight(self):
        self.assertEqual(calculate_delivery_cost(50, 1, "обычный"), (307, "2026-09-04"))

    def test_accepts_minimum_distance(self):
        self.assertEqual(calculate_delivery_cost(1, 1, "обычный"), (205, "2026-09-04"))

    def test_accepts_maximum_distance(self):
        self.assertEqual(calculate_delivery_cost(1, 5000, "обычный"), (25200, "2026-09-13"))


class TestDeliveryTariffs(unittest.TestCase):
    def test_calculates_base_cost_for_light_package(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "обычный"), (700, "2026-09-04"))

    def test_applies_medium_weight_coefficient(self):
        self.assertEqual(calculate_delivery_cost(10, 100, "обычный"), (840, "2026-09-04"))

    def test_applies_heavy_weight_coefficient(self):
        self.assertEqual(calculate_delivery_cost(25, 100, "обычный"), (1050, "2026-09-04"))

    def test_weight_exactly_five_has_no_coefficient(self):
        self.assertEqual(calculate_delivery_cost(5, 100, "обычный"), (700, "2026-09-04"))

    def test_weight_exactly_twenty_uses_heavy_coefficient(self):
        self.assertEqual(calculate_delivery_cost(20, 100, "обычный"), (1050, "2026-09-04"))

    def test_adds_fragile_surcharge(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "хрупкий"), (1000, "2026-09-04"))

    def test_adds_dangerous_surcharge(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "опасный"), (1700, "2026-09-04"))


class TestDeliveryDate(unittest.TestCase):
    def test_short_distance_takes_one_day(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "обычный")[1], "2026-09-04")

    def test_five_hundred_km_takes_one_day(self):
        self.assertEqual(calculate_delivery_cost(1, 500, "обычный")[1], "2026-09-04")

    def test_thousand_km_takes_two_days(self):
        self.assertEqual(calculate_delivery_cost(1, 1000, "обычный")[1], "2026-09-05")

    def test_long_distance_date_grows(self):
        self.assertEqual(calculate_delivery_cost(1, 2500, "обычный")[1], "2026-09-08")


class TestExpressDelivery(unittest.TestCase):
    def test_express_increases_cost(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "обычный", True), (1050, "2026-09-04"))

    def test_express_increases_cost_for_fragile(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "хрупкий", True), (1500, "2026-09-04"))

    def test_express_short_route_takes_at_least_one_day(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "обычный", True)[1], "2026-09-04")

    def test_express_halves_days_on_long_route(self):
        self.assertEqual(calculate_delivery_cost(1, 2000, "обычный", True)[1], "2026-09-05")


if __name__ == "__main__":
    unittest.main()
