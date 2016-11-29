import pygame

line1 = [(1, 1), (5, 5)]
line2 = [(2, 3), (4, 8)]

def slope(p1, p2) :
   return (p2[1] - p1[1]) * 1. / (p2[0] - p1[0])

def y_intercept(slope, p1) :
   return p1[1] - 1. * slope * p1[0]

def didIntersect(line0, line1):
    m1 = slope(line0[0], line0[1])
    print(m1)
    b1 = y_intercept(slope(line0[0], line0[1]), line0[0])
    print(b1)
    m2 = slope(line1[0], line1[1])
    print(m2)
    b2 = y_intercept(slope(line1[0], line1[1]), line1[0])
    print(b2)
    if m1 == m2: return None
    b = b2 - b1
    m = m1 - m2
    x = b/m
    y = m1 * x + b1
    return (x, y)



print(didIntersect(line1, line2))
