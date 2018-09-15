# ---------------------------------------------
# graph.py
# classes about various kinds of graph.
# ---------------------------------------------
# import random
import math

POLYGON = 1
CIRCLE = POLYGON + 1


# the class to describe a single point
class Point:
    def __init__(self, x, y):
        self.x_loc = float(x)
        self.y_loc = float(y)

    # after thinking, I choose to package x and y.
    def x(self):
        return self.x_loc

    def y(self):
        return self.y_loc

    def show_info(self, printer):
        printer.print('x: ' + str(self.x()) + ' y: ' + str(self.y()))


class Graph:
    def __init__(self, graph_type):
        self.type_ = graph_type

    def judge_points_inside(self, point):
        pass

    def area(self):
        pass

    def show_info(self, printer):
        pass

    def cover_range(self):
        pass


# the class stand for a polygon
class Polygon(Graph):
    # attention: the points must be in sequence! Or the graph will be different from your imaginary.
    def __init__(self, points):
        Graph.__init__(self, POLYGON)
        self.points = points
        self.lines = []
        # calculate the lines when __init__. Seems no reason to wait.
        self.form_lines()

    # use this def to form lines from points
    def form_lines(self):
        for i in range(0, len(self.points) - 1):
            self.lines.append(LineSegment(self.points[i], self.points[i + 1]))
        # don't forget the line between the first and the last.
        self.lines.append(LineSegment(self.points[len(self.points) - 1], self.points[0]))

    # to judge if a point is in the polygon
    # make a random ray from the point, to see how much times the ray intersect with the border of the polygon
    # if odd: in; if even: out.
    def judge_points_inside(self, point):
        """
        intersect_times = 0
        slope = random.uniform(-2, 2)
        direction = random.choice([-1, 1])
        ray = Rays(point, slope, direction)
        for i in range(0, len(self.lines)):
            intersect_times += if_intersection(self.lines[i], ray)
        # if intersect_times % 2 == 0:
        #     return 0
        # else:
        #     return 1
        return intersect_times % 2 != 0
        """
        angle = 0.0
        if point.x() == self.points[0].x() and point.y() == self.points[0].y():
            return True
        for l in self.lines:
            if l.in_segment(point):
                return True
        for i in range(0, len(self.points)-1):
            if point.x() == self.points[i+1].x() and point.y() == self.points[i+1].y():
                return True
            angle += calculate_angle(self.points[i], self.points[i+1], point)
            # print(angle)
        angle += calculate_angle(self.points[len(self.points)-1], self.points[0], point)
        # print('%lf, %lf' % (point.x(), point.y()))
        # print(angle)
        # should be ==0, but the accuracy of calculation is limited.
        return not (math.pi / 4 >= angle >= -math.pi / 4)

    # calculate the area of the polygon
    # use the method of the sum of the cross products of vectors from the points and the origin point
    def area(self):
        area_sum = 0.0
        for i in range(0, len(self.points) - 1):
            area_sum += 0.5 * cross_product_from_origin(self.points[i], self.points[i + 1])
        # don't forget to add the first.
        area_sum += 0.5 * cross_product_from_origin(self.points[len(self.points) - 1], self.points[0])
        area_sum = math.fabs(area_sum)
        return area_sum

    def show_info(self, printer):
        printer.print('polygon : ')
        for p in self.points:
            p.show_info(printer=printer)

    def cover_range(self):
        x_s, y_s = [point.x() for point in self.points], [point.y() for point in self.points]
        x_min, x_max = int(min(x_s)) - 1, int(max(x_s)) + 1
        y_min, y_max = int(min(y_s)) - 1, int(max(y_s)) + 1
        return x_min, x_max, y_min, y_max


class Circle(Graph):
    def __init__(self, center_point, radius):
        Graph.__init__(self, graph_type=CIRCLE)
        self.center_point = center_point
        self.radius = radius

    def judge_points_inside(self, point):
        return self.radius >= euclid_distance(point_1=self.center_point, point_2=point)

    def area(self):
        return math.pi * self.radius ** 2

    def show_info(self, printer):
        printer.print('circle : radius = %lf' % self.radius)
        self.center_point.show_info(printer=printer)

    def cover_range(self):
        return int(self.center_point.x() - self.radius) - 1, int(self.center_point.x() + self.radius) + 1, \
               int(self.center_point.y() - self.radius) - 1, int(self.center_point.y() + self.radius) + 1


# calculate the cross product from two vectors.
# input two points. the two vectors are from origin to the points.
def cross_product_from_origin(p1, p2):
    return p1.x() * p2.y() - p2.x() * p1.y()


def euclid_distance(point_1, point_2):
    return math.sqrt((point_1.x() - point_2.x()) ** 2 + (point_1.y() - point_2.y()) ** 2)


class Line:
    # well, I find that python don't support function overloading. So I can have only one __init__
    def __init__(self, input_1, input_2):
        # input two points
        if isinstance(input_1, Point) and isinstance(input_2, Point):
            if input_1.x() == input_2.x() and input_1.y() != input_2.y():
                self.slope = float('inf')
                self.intercept_x = input_1.x()
            else:
                self.slope = (input_2.y() - input_1.y()) / (input_2.x() - input_1.x())
                self.intercept = (input_1.y() * input_2.x() - input_2.y() * input_1.x()) / (input_2.x() - input_1.x())
        # input a point and a slope. attention: slope cannot be int! must be float.
        elif isinstance(input_1, Point) and isinstance(input_2, float):
            self.slope = input_2
            self.intercept = input_1.y() - self.slope * input_1.x()

    def in_line(self, p):
        if self.slope == float('inf'):
            return p.x() == self.intercept_x
        if p.y() == p.x() * self.slope + self.intercept:
            return 1
        else:
            return 0

    def vertical(self):
        return self.slope == float('inf')


# segment of line. a line with start and end
class LineSegment(Line):
    def __init__(self, input_1, input_2):
        Line.__init__(self, input_1, input_2)
        if self.slope == float('inf'):
            self.min_y = min(input_1.y(), input_2.y())
            self.max_y = max(input_1.y(), input_2.y())
        else:
            self.min_x = min(input_1.x(), input_2.x())
            self.max_x = max(input_1.x(), input_2.x())

    # to judge if the point is in the line segment. Attention: the point is sure on the line!.
    def in_segment(self, p):
        if self.in_line(p):
            if self.slope != float('inf'):
                return self.min_x <= p.x() <= self.max_x
            else:
                return self.min_y <= p.y() <= self.max_y
        else:
            return 0

    # calculate the length of the line segment
    # pythagoras theorem
    def length(self):
        if not self.vertical():
            return (self.max_x - self.min_x) * math.sqrt(1 + math.pow(self.slope, 2))
        else:
            return self.max_y - self.min_y


# a line with one end.
class Rays(Line):
    def __init__(self, input_1, input_2, direction):
        Line.__init__(self, input_1, input_2)
        self.direction = direction
        self.start_point = input_1

    # to judge if the point is in the ray.
    def in_rays(self, p):
        if self.in_line(p):
            # check the direction
            return (self.start_point.x() - p.x()) * self.direction >= 0
        else:
            return 0


# find the intersection of two line.
def find_intersection(line_a, line_b):
    # both horizon or vertical
    if line_a.slope == line_b.slope:
        return None
    if line_a.vertical():
        x = line_a.intercept_x
        y = x * line_b.slope + line_b.intercept
    elif line_b.vertical():
        x = line_b.intercept_x
        y = x * line_a.slope + line_a.intercept
    else:
        x = (line_b.intercept - line_a.intercept) / (line_a.slope - line_b.slope)
        y = x * line_a.slope + line_a.intercept
    return Point(x, y)


# @TODO: there is defect of this function. However, it is not used now.
# find if the intersection of a line_segment and a ray is inside the line_segment and the ray.
def if_intersection(segment, ray):
    if isinstance(segment, LineSegment) and isinstance(ray, Rays):
        # print('if_intersection')
        p = find_intersection(segment, ray)
        if p is not None and segment.in_segment(p) and ray.in_rays(p):
            return 1
        else:
            return 0
    else:
        print('wrong type')


def calculate_angle(point_a, point_b, point_c):
    """
    calculate the angle formed by the three points.
    :param point_a:
    :param point_b:
    :param point_c: class graph.Point, the center point.
    :return: float
    """
    angle1 = math.atan2(point_b.y() - point_c.y(), point_b.x() - point_c.x())
    angle2 = math.atan2(point_a.y() - point_c.y(), point_a.x() - point_c.x())
    angle = angle2 - angle1
    if angle > math.pi:
        angle -= math.pi
    elif angle < -math.pi:
        angle += math.pi
    return angle
