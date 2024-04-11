
class Endpoints:
    """
    Represents a line segment defined by two endpoints.
    Used for drawing objects in the origami design.

    Attributes:
        x1 (float): The x-coordinate of the first endpoint.
        y1 (float): The y-coordinate of the first endpoint.
        x2 (float): The x-coordinate of the second endpoint.
        y2 (float): The y-coordinate of the second endpoint.
        r1 (tuple): A tuple representing the first endpoint as (x, y).
        r2 (tuple): A tuple representing the second endpoint as (x, y).
        center (tuple): A tuple representing the center point of the line segment as (x, y).
    """

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.r1 = (x1, y1)
        self.r2 = (x2, y2)
        self.center = self.get_center()

    def get_center(self):
        """
        Calculates and returns the center point of the line segment.

        Returns:
            tuple: A tuple representing the center point of the line segment as (x, y).
        """
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
class Endpoints:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.r1 = (x1,y1)
        self.r2 = (x2,y2)
        self.center = self.get_center()
    def get_center(self):
        return ( (self.x1+self.x2)/2 , (self.y1+self.y2)/2 )