from epic_utils.decorator import ClassProperty
import math
from typing import Union


class ErrorHandler:
    def raiseError(typ, message : str):
        raise typ(message)
    def isType(obj, typ) -> bool:
        return isinstance(obj, typ)
    def isTypes(obj, types) -> bool:
        for typ in types:
            if isinstance(obj, typ):
                return True
        return False

class Converter:
    def dec2hex(value : int):
        h = hex(value)
        result = str.upper(h[2:])
        if len(result) < 2:
            result = "0" + result
        return result
class Vector2():
    def __init__(self, x : float, y : float):
        self.x : float = x
        self.y : float = y
    @property
    def this(self):
        return [self.x, self.y]    
    
    @property
    def sqrMagnitude(self):
        return self.x**2 + self.y**2
    @property
    def magnitude(self):
        return math.sqrt(self.sqrMagnitude)
    @property
    def normalized(self): 
        mag = self.magnitude
        return Vector2(self.x/mag, self.y/mag)
    
    def toTuple(self):
        return (self.x, self.y)
    def toList(self):
        return [self.x, self.y]
    
    @classmethod
    def sqrDistance(cls, vector1, vector2):
        if not (isinstance(vector1, Vector2) and isinstance(vector2, Vector2)):
            ErrorHandler.raiseError(TypeError, f"<Vector2, Vector2> expected, got <{type(vector1).__name__},{type(vector2).__name__}>")
        return abs(vector2.x - vector1.x)**2 + abs(vector2.y - vector1.y)**2
    @classmethod
    def distance(cls, vector1, vector2) -> float:
        if not (isinstance(vector1, Vector2) and isinstance(vector2, Vector2)):
            ErrorHandler.raiseError(TypeError, f"<Vector2, Vector2> expected, got <{type(vector1).__name__},{type(vector2).__name__}>")
        return math.sqrt(Vector2.sqrDistance(vector1, vector2))
    
    @classmethod
    def fromArray(cls, array : Union[list, tuple]):
        if not ErrorHandler.isTypes(array, [list, tuple]):
            ErrorHandler.raiseError(TypeError, f"<list|tuple> expected, got <{type(array).__name__}>")
        if len(array) < 2:
            ErrorHandler.raiseError(IndexError, f"length <2> expected, got length <{len(array)}>")
        return Vector2(array[0], array[1])
    @classmethod
    def fromDict(cls, dictionary : dict):
        if not ErrorHandler.isType(dictionary, dict):
            ErrorHandler.raiseError(TypeError, f"<dict> expected, got <{type(dictionary).__name__}>")
        keys = list(dictionary.keys())
        if not ("x" in keys and "y" in keys):
            ErrorHandler.raiseError(KeyError, f"keys <x,y> expected, got keys <{",".join(keys)}>")
        return Vector2(dictionary["x"], dictionary["y"])
    @classmethod
    def max(cls, *args):
        result = Vector2.negativeInfinity
        for vector in args:
            if not ErrorHandler.isType(vector, Vector2):
                continue
            result.x = max(result.x, vector.x)
            result.y = max(result.y, vector.y)
        return result
    @classmethod
    def min(cls, *args):
        result = Vector2.positiveInfinity
        for vector in args:
            if not ErrorHandler.isType(vector, Vector2):
                continue
            result.x = min(result.x, vector.x)
            result.y = min(result.y, vector.y)
        return result
    
    @classmethod
    def linearInterpolation(cls, start, end, time):
        return start + (end - start) * time
    
    @classmethod
    def bezierInterpolation(p0, p1, p2, time):
        tempA = Vector2.linearInterpolation(p0, p1, time)
        tempB = Vector2.linearInterpolation(p1, p2, time)
        return Vector2.linearInterpolation(tempA, tempB, time)
    
    @ClassProperty
    def up(cls):
        return Vector2(0, 1)
    @ClassProperty
    def down(cls):
        return Vector2(0, -1)
    @ClassProperty
    def left(cls):
        return Vector2(-1, 0)
    @ClassProperty
    def right(cls):
        return Vector2(1, 0)
    @ClassProperty
    def positiveInfinity(cls):
        return Vector2(math.inf, math.inf)
    @ClassProperty
    def negativeInfinity(cls):
        return Vector2(-math.inf, -math.inf)
    
    
    def __add__(self, value):
        if ErrorHandler.isType(value, Vector2):
            return Vector2(self.x + value.x, self.y + value.y)
        return Vector2(self.x + value, self.y + value)
    def __sub__(self, value):
        if ErrorHandler.isType(value, Vector2):
            return Vector2(self.x - value.x, self.y - value.y)
        return Vector2(self.x - value, self.y - value)    
    def __mul__(self, value):
        if ErrorHandler.isType(value, Vector2):
            return Vector2(self.x * value.x, self.y * value.y)
        return Vector2(self.x * value, self.y * value)
    def __div__(self, value):
        if ErrorHandler.isType(value, Vector2):
            if value.x == 0.0 or value.y == 0.0:
                ErrorHandler.raiseError(ZeroDivisionError, "")    
            return Vector2(self.x / value.x, self.y / value.y)
        if value == 0.0:
            ErrorHandler.raiseError(ZeroDivisionError, "")
        return Vector2(self.x / value, self.y / value)
    def __truediv__(self, value):
        if ErrorHandler.isType(value, Vector2):
            if value.x == 0.0 or value.y == 0.0:
                ErrorHandler.raiseError(ZeroDivisionError, "")    
            return Vector2(self.x / value.x, self.y / value.y)
        if value == 0.0:
            ErrorHandler.raiseError(ZeroDivisionError, "")
        return Vector2(self.x / value, self.y / value) 
    def __pow__(self, value):
        if ErrorHandler.isType(value, Vector2):
            return Vector2(self.x **value.x, self.y**value.y)
        return Vector2(self.x**value, self.y**value)
    
    def __str__(self):
        return f"Vector2({self.x}, {self.y})"

class Region2:
    def __init__(self, vector1 : Vector2, vector2 : Vector2):
        self.v1 : Vector2 = Vector2(min(vector1.x, vector2.x), min(vector1.y, vector2.y))
        self.v2 : Vector2 = Vector2(max(vector1.x, vector2.x), max(vector1.y, vector2.y))
    def isInside(self, vector : Vector2) -> bool:
        return self.v1.x <= vector.x and self.v1.y <= vector.y and self.v2.x >= vector.x and self.v2.y >= vector.y
    
    def __str__(self):
        return f"Region2({self.v1}, {self.v2})"

class Color():
    def __init__(self, r : int, g : int, b : int):
        self.r : int = r
        self.b : int = b
        self.g : int = g
    
    
    @property
    def hex(self):
        r = Converter.dec2hex(self.r)
        g = Converter.dec2hex(self.g)
        b = Converter.dec2hex(self.b)
        return r + g + b
    def toTuple(self) -> tuple:
        return (self.r, self.g, self.b)
    
    
    @classmethod
    def fromTuple(cl, tup : tuple):
        if len(tup) < 3:
            return False
        return Color(tup[0], tup[1], tup[2])
    @ClassProperty
    def white(cl):
        return Color(255, 255, 255)
    @ClassProperty
    def black(cl):
        return Color(0, 0, 0)
    @ClassProperty
    def red(cl):
        return Color(255, 0, 0)
    @ClassProperty
    def green(cl):
        return Color(0, 255, 0)
    @ClassProperty
    def blue(cl):
        return Color(0, 0, 255)
    
    def __str__(self):
        return f"Color({self.r}, {self.g}, {self.b})"
    