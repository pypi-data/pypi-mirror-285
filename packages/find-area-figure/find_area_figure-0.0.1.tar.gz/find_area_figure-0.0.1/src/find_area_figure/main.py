from math import pi, sqrt

class Calculate:
    def circle(self, radius):
        return round(radius * pi, 2)
    def triangle(self, a, b, c):
        p = (a + b + c) // 2
        res = sqrt(p*(p-a)*(p-b)*(p-c))
        is_rectangular = False
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    if a ** 2 == b ** 2 + c ** 2:
                        is_rectangular = True
                    else:
                        continue
        print(is_rectangular)
        return res
