from math import pi, sqrt

class Shape():
    def square(self):
        raise NotImplementedError
    
class Circle(Shape):
    def __init__(self, radius: float = 1.0):
        if radius >= 0.0:
            self.radius = radius
        else:
             raise ValueError("Ошибка! Радиус не может быть меньше 0")
    
    def square(self) -> float:
        return pi * (self.radius ** 2)

class Triangle(Shape):
    def __init__(self, a: float = 1.0, 
                 b: float = 1.0, 
                 c: float = 3.0):
        if a <= 0 or b <= 0 or c <= 0:
            raise ValueError("Ошибка! У треугольника все стороны должны быть положительными!")
        if a + b <= c or  a + c <= b or b + c <= a:
            raise ValueError("Ошибка! Треугольника с такими сторонами не существует!")
        self.a = a
        self.b = b
        self.c = c
    def square(self) -> float:
        # Вычисление полупериметра
        p = (self.a + self.b + self.c) / 2
        return sqrt(p * (p-self.a) * (p - self.b) * (p - self.c))
    
    def is_right(self) -> bool:
        # Проверка по теореме Пифагора
        sides = [self.a, self.b, self.c]
        sides.sort()
        return sides[0] ** 2 + sides[1] ** 2 == sides[2] ** 2
    
def calculate_square(shape):
    if not hasattr(shape, 'square'):
        raise TypeError("Input must be a shape object")
    return shape.square()
        
