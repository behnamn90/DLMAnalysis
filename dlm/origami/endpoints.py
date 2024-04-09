
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