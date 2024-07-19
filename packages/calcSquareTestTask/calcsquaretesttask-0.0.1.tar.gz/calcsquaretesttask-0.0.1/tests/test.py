import unittest
from math import pi
# import sys
# sys.path.insert(0, '../calc_square')
from src.calcSquareTestTask.main import Circle, Triangle, calculate_square


class Test(unittest.TestCase):
    def test_circle(self):
        circle = Circle(5)
        self.assertAlmostEqual(circle.square(), pi * 25)

    def test_calc_area_circle(self):
        circle = Circle(5)
        self.assertAlmostEqual(calculate_square(circle), pi * 25)

    def test_circle_er(self):
        with self.assertRaises(ValueError):
            Circle(-5)

    def test_traingle(self):
        triangle = Triangle(3,4,5)
        self.assertAlmostEqual(triangle.square(), 6)

    def test_traingle(self):
        triangle = Triangle(3,4,5)
        self.assertAlmostEqual(calculate_square(triangle), 6)

    def test_traingle_right(self):
        triangle = Triangle(3,4,5)
        self.assertTrue(triangle.is_right())

    def test_traingle_er(self):
        with self.assertRaises(ValueError):
            Triangle(1,1,10)

    def test_calculate_area_er(self):
        with self.assertRaises(TypeError):
            calculate_square("not a shape")

if __name__ == '__main__':
    unittest.main()
