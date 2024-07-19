import unittest

from src.find_area_figure import Calculate
class TestCalculate(unittest.TestCase):
  def setUp(self):
    self.calculator = Calculate()
  def test_circle(self):
    self.assertEqual(self.calculator.circle(5), 15.71)
  def test_triangle(self):
    self.assertEqual(self.calculator.triangle(3,4, 5), 6)

if __name__ == "__init__":
  unittest.main()
