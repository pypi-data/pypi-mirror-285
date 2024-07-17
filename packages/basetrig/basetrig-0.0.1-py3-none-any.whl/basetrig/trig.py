import math
import itertools
from typing import Optional

class trig:
    def __init__(self):
        """
        Constructor for the trig class.
        """
        pass

    def  __degrees_radians(self,degree):
        """
        Converts degrees to radians.

        Parameters:
            degree (int): The degree value to be converted to radians.

        Returns:
            float: The radian value.
        """
        ridans=math.radians(degree)
        return ridans

    def sin𝜃(self,*,angle) :
        """
        Calculate the sine of the given angle in degrees.

        Parameters:
            angle (int): The angle in degrees.

        Returns:
            float: The sine of the angle.
        """
        ridans=self.__degrees_radians(angle)
        return math.sin(ridans) 

    def cos𝜃(self,*,angle) : 
        """
        Calculate the cosine of the given angle in degrees.

        Parameters:
            angle (int): The angle in degrees.

        Returns:
            float: The cosine of the angle.
        """
        ridans=self.__degrees_radians(angle)
        return math.cos(ridans)

    def tan𝜃(self,*,angle):
        """
        Calculate the tangent of the given angle in degrees.

        Parameters:
            angle (int): The angle in degrees.

        Returns:
            float: The tangent of the angle.
        """
        ridans=self.__degrees_radians(angle)
        return math.tan(ridans)
    
    def cot𝜃(self,*,angle):
        """
        Calculate the cotangent of the given angle in degrees.

        Parameters:
            angle (int): The angle in degrees.

        Returns:
            float: The cotangent of the angle.
        """
        ridans=self.__degrees_radians(angle)
        return 1/math.tan(ridans)
    
    def sec𝜃(self,*,angle):
        """ 
        Calculate the secant of the given angle in degrees.

        Parameters:
            angle (int): The angle in degrees.

        Returns:
            float: The secant of the angle.
        """
        ridans=self.__degrees_radians(angle)    
        return 1/math.cos(ridans)

    def csc𝜃(self,*,angle):
        """
        Calculate the cosecant of the given angle in degrees.

        Parameters:
            angle (int): The angle in degrees.

        Returns:
            float: The cosecant of the angle.
        """
        ridans=self.__degrees_radians(angle)  
        return 1/math.sin(ridans)

class geometry:
    def __init__(
            self,
            *,
            a:Optional[int]=None,
            b:Optional[int]=None,
            c:Optional[int]=None,
            𝜃a:Optional[int]=None,
            𝜃b:Optional[int]=None,
            𝜃c:Optional[int]=None
        ):
        """
        Initializes a new instance of the class with the given parameters.

        Parameters:
            a (Optional[int]): The first parameter.
            b (Optional[int]): The second parameter.
            c (Optional[int]): The third parameter.
            𝜃a (Optional[int]): The first angle parameter.
            𝜃b (Optional[int]): The second angle parameter.
            𝜃c (Optional[int]): The third angle parameter.

        Raises:
            ValueError: If exactly two parameters are not provided or if exactly one angle parameter is not provided.
        """
        self._a=a
        self._b=b
        self._c=c
        self._𝜃a=𝜃a
        self._𝜃b=𝜃b
        self._𝜃c=𝜃c

        params=[a,b,c]
        params_=[𝜃a,𝜃b,𝜃c]
        if not (0 < params.count(None) < 2):
            raise ValueError("Exactly two parameters must be provided")
        if not (1 == params_.count(None) or params_.count(None) == 3):
            raise ValueError("Exactly one parameters must be provided")
    @property
    def area(self):
        """
        Calculates the area of a triangle based on the given parameters.

        Returns:
            float: The area of the triangle.

        Raises:
            None
        """
        res=itertools.product((self._a,self._b,self._c), repeat=2)
        degrees=[self._𝜃a,self._𝜃b,self._𝜃c]
        return [0.5 * p[0] * p[1] * math.sin(math.radians(item))
                for p in res
                for item in degrees
                if p[0] != p[1] and None not in (p + (item,))][0]
    
    @property
    def get_a(self):
        """
        Calculate and return the value of the second side of a right-angled triangle.

        Returns:
            float: The length of the second side of the right-angled triangle.
        """
        self._a=(self._b**2+self._c**2-2*self._b*self._c*math.cos(math.radians(self._𝜃a)))**0.5
        return self._a

    @property
    def get_b(self):
        """
        Calculate and return the value of the first side of a right-angled triangle.

        Returns:
            float: The length of the first side of the right-angled triangle.
        """
        self._b=(self._a**2+self._c**2-2*self._a*self._c*math.cos(math.radians(self._𝜃b)))**0.5
        return self._b

    @property
    def get_c(self):
        """
        Calculate and return the value of the third side of a right-angled triangle.

        Returns:
            float: The length of the third side of the right-angled triangle.
        """
        self._c=(self._a**2+self._b**2-2*self._a*self._b*math.cos(math.radians(self._𝜃c)))**0.5
        return self._c