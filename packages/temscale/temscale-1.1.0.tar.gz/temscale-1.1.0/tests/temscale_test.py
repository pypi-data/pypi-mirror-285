import unittest
from temscale import temscale


class TestTemscale(unittest.TestCase):
    """test of temscale class functions"""

    def test_constructor(self):
        tem = temscale.Temscale(100, "C")
        self.assertEqual(tem.get_value(), 100)
        self.assertEqual(tem.get_type(), "C")

    def test_eq(self):
        tem1 = temscale.Temscale(100, "C")
        tem2 = temscale.Temscale(50, "F")
        self.assertFalse(tem1 == tem2)
        tem1 = temscale.Temscale(10, "C")
        self.assertTrue(tem1 == tem2)

    def test_ne(self):
        tem1 = temscale.Temscale(100, "C")
        tem2 = temscale.Temscale(50, "F")
        self.assertTrue(tem1 != tem2)
        tem1 = temscale.Temscale(10, "C")
        self.assertFalse(tem1 != tem2)

    def test_lt(self):
        tem1 = temscale.Temscale(100, "C")
        tem2 = temscale.Temscale(50, "C")
        self.assertFalse(tem1 < tem2)
        tem1 = temscale.Temscale(10, "C")
        self.assertTrue(tem1 < tem2)

    def test_gt(self):
        tem1 = temscale.Temscale(100, "C")
        tem2 = temscale.Temscale(50, "C")
        self.assertTrue(tem1 > tem2)
        tem1 = temscale.Temscale(10, "C")
        self.assertFalse(tem1 > tem2)

    def test_le(self):
        tem1 = temscale.Temscale(100, "C")
        tem2 = temscale.Temscale(50, "C")
        self.assertFalse(tem1 <= tem2)
        tem1 = temscale.Temscale(10, "C")
        self.assertTrue(tem1 <= tem2)
        tem1 = temscale.Temscale(50, "C")
        self.assertTrue(tem1 <= tem2)

    def test_ge(self):
        tem1 = temscale.Temscale(100, "C")
        tem2 = temscale.Temscale(50, "C")
        self.assertTrue(tem1 >= tem2)
        tem1 = temscale.Temscale(10, "C")
        self.assertFalse(tem1 >= tem2)
        tem1 = temscale.Temscale(50, "C")
        self.assertTrue(tem1 >= tem2)

    def test_set_value(self):
        tem = temscale.Temscale(100, "C")
        self.assertEqual(tem.get_value(), 100)

    def test_set_type(self):
        tem = temscale.Temscale(100, "C")
        self.assertEqual(tem.get_type(), "C")

    def test_get_value(self):
        tem = temscale.Temscale(100, "C")
        self.assertEqual(tem.get_value(), 100)

    def test_get_type(self):
        tem = temscale.Temscale(100, "C")
        self.assertEqual(tem.get_type(), "C")

    def test_to_celsius(self):
        tem_k = temscale.Temscale(100, "K")
        tem_f = temscale.Temscale(100, "F")
        tem_k.to_celsius()
        tem_f.to_celsius()
        self.assertEqual(tem_k.get_value(), -173.14999999999998)
        self.assertEqual(tem_f.get_value(), 37.77777777777778)

    def test_to_kelvin(self):
        tem_c = temscale.Temscale(100, "C")
        tem_f = temscale.Temscale(100, "F")
        tem_c.to_kelvin()
        tem_f.to_kelvin()
        self.assertEqual(tem_c.get_value(), 373.15)
        self.assertEqual(tem_f.get_value(), 310.9277777777778)

    def test_to_fahrenheit(self):
        tem_c = temscale.Temscale(100, "C")
        tem_k = temscale.Temscale(100, "K")
        tem_c.to_fahrenheit()
        tem_k.to_fahrenheit()
        self.assertEqual(tem_c.get_value(), 212.0)
        self.assertEqual(tem_k.get_value(), -279.67)

    def test_to_convert(self):
        tem = temscale.Temscale(100, "C")
        tem.convert("F")
        self.assertEqual(round(tem.get_value(), 2), 212.0)
        tem.convert("K")
        self.assertEqual(round(tem.get_value(), 2), 373.15)
        tem.convert("C")
        self.assertEqual(round(tem.get_value(), 2), 100)


if __name__ == '__main__':
    unittest.main()
