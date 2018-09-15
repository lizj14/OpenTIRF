# ---------------------------------------------
# data.py
# classes record the information in the program.
# ---------------------------------------------
import math
import module_base
import csv


class DataPoint:
    """
    this class records the data of the point fit from the tiff file, before attributed to molecules.
    """

    def __init__(self, frame_start=None, frame_end=None, intensity=None, x=None, y=None, x_sigma=None, y_sigma=None,
                 x_error=None, y_error=None, stddev=None):
        """
        the data to represent a shining point in the tiff.
        if any other attributes wanted: 1. inherit a new class from DataPoint. 2. add the new attribute into DataPoint.
        :param frame_start: the frame which the flash start.
        :param frame_end: the frame which the flash end.
        :param intensity:
        :param x: the coordinate of the point from data fitting.
        :param y:
        :param x_sigma: the standard deviation on the x coordinating
        where the value of flash is seemed as a 2D Gaussian distribution.
        :param y_sigma:
        :param x_error: the max value of error of the location on the x coordination.
        :param y_error:
        :param stddev:
        """
        self.frame_start_ = int(frame_start)
        self.frame_end_ = int(frame_end)
        self.intensity_ = float(intensity)
        self.x_ = float(x)
        self.y_ = float(y)
        self.x_sigma_ = float(x_sigma)
        self.y_sigma_ = float(y_sigma)
        self.x_error_ = float(x_error)
        self.y_error_ = float(y_error)
        self.stddev_ = float(stddev)

    def frame_start(self):
        return self.frame_start_

    def frame_end(self):
        return self.frame_end_

    def intensity(self):
        return self.intensity_

    def x(self):
        return self.x_

    def y(self):
        return self.y_

    def x_sigma(self):
        return self.x_sigma_

    def y_sigma(self):
        return self.y_sigma_

    def x_error(self):
        return self.x_error_

    def y_error(self):
        return self.y_error_

    def stddev(self):
        return self.stddev_

    # @TODO: better method of sort. consider error first.
    def __lt__(self, other):
        """
        used in sort of class DataPoint. work as '<'
        no compare with y because x is a float, and there is little possibility of same x.
        :param other: the class DataPoint to compare with.
        :return: T/F. if the point 'self' is smaller than 'other'
        """
        if self.frame_start() < other.frame_start():
            return True
        elif self.frame_start() > other.frame_start():
            return False
        else:
            if self.intensity() > other.intensity():
                return True
            elif self.intensity() < other.intensity():
                return False
            else:
                if self.x() < other.x():
                    return True
                else:
                    return False

    def to_string(self):
        return 'point from %s to %s at (%s, %s)' % (self.frame_start_, self.frame_end_, self.x_, self.y_)

    def to_dictionary(self):
        return {'x': self.x_, 'y': self.y_, 'frame_start': self.frame_start_, 'frame_end': self.frame_end_,
                'x_error': self.x_error_, 'y_error': self.y_error_, 'x_sigma': self.x_sigma_,
                'y_sigma': self.y_sigma_, 'intensity': self.intensity_, 'stddev': self.stddev_}


class PointChooser(module_base.Singleton):
    @staticmethod
    def better_point(point_a, point_b):
        pass


class IntensityChooser(PointChooser):
    @staticmethod
    def better_point(point_a, point_b):
        return point_a.intensity() < point_b.intensity()


class AccuracyChooser(PointChooser):
    @staticmethod
    def better_point(point_a, point_b):
        return point_a.x_error() ** 2 + point_a.y_error() ** 2 < point_b.x_error() ** 2 + point_b.y_error() ** 2


class NoChooser(PointChooser):
    @staticmethod
    def better_point(point_a, point_b):
        return True


point_chooser = {
    'intensity': IntensityChooser(),
    'accuracy': AccuracyChooser(),
    'no': NoChooser(),
}


def point_distance(point_a, point_b):
    """
    calculate distance between two points.
    :param point_a: class DataPoint.
    :param point_b: so as above.
    :return: float, the distance.
    """
    return math.sqrt((point_a.x() - point_b.x()) ** 2 + (point_a.y() - point_b.y()) ** 2)


class DataList:
    def __init__(self, file_name=None):
        """
        self.data_: expect to be a list of class DataPoint.
        :param file_name:
        """
        self.data_ = []
        if file_name is not None:
            self.read_data_from_csv(file_name)

    def sort(self):
        """
        the __lt__ function of class DataPoint is defined as above.
        :return: Nothing.
        """
        self.data_.sort()

    # @TODO: There maybe better way of implement csv reader, where several types need it.
    def read_data_from_csv(self, file_name):
        """
        read the data from a csv file. into a data_list.
        It is not used in the program now, but once used in the early version, and maybe reused later.
        :param file_name: the file path of the csv file.
        :return: nothing.
        """
        input_file = open(file_name)
        reader = csv.DictReader(input_file)
        for row in reader:
            self.data_.append(
                DataPoint(frame_start=row['frame_start'], frame_end=row['frame_end'], intensity=row['intensity'],
                          x=row['x'], y=row['y'], x_sigma=row['x_sigma'], y_sigma=row['y_sigma'],
                          x_error=row['x_error'], y_error=row['y_error'], stddev=row['stddev']))
        self.sort()

    # @TODO: the same as above
    def write_data_into_csv(self, file_name):
        """
        Also no use now, but maybe in future.
        :param file_name: the file path to write into.
        :return: nothing.
        """
        out_file = open(file_name, 'w')
        fieldnames = [
            'frame_start', 'frame_end', 'intensity', 'x', 'y', 'x_error', 'y_error', 'x_sigma', 'y_sigma',
            'stddev',
        ]
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        for point in self.data_:
            writer.writerow(point.to_dictionary())

    def length(self):
        return len(self.data_)

    def clear(self):
        self.data_.clear()

    def add_data(self, data_point):
        self.data_.append(data_point)

    def return_point(self, no):
        if no < len(self.data_):
            return self.data_[no]
        else:
            return None

    def to_string(self):
        return 'data_list: %d data in list' % len(self.data_)


class Molecule:
    def __init__(self, first_data):
        self.data_history_ = []
        if isinstance(first_data, DataPoint):
            self.data_history_.append(first_data)
            self.frame_start = first_data.frame_start()
            self.frame_end = first_data.frame_end()

    def main_point(self):
        """
        this point is used for the
        :return: the first point in the list inside the object.
        """
        if len(self.data_history_) == 0:
            return None
        else:
            return self.data_history_[0]

    def add_point(self, new_point, chooser):
        """
        if the new_point is better than the best now, it will be added at the first place in the list, which means that
        it is the best point.
        :param new_point:
        :param chooser: class PointChooser, deciding which point to be better.
        :return: new_point, if add successfully; None, if the object is not DataPoint, and the insertion fails.
        """
        if isinstance(new_point, DataPoint):
            if chooser.better_point(new_point, self.main_point()):
                self.data_history_.insert(0, new_point)
            else:
                self.data_history_.append(new_point)
            if new_point.frame_end() > self.frame_end:
                self.frame_end = new_point.frame_end()
            return new_point
        else:
            return None

    def x(self):
        return self.main_point().x()

    def y(self):
        return self.main_point().y()

    def start(self):
        return self.frame_start

    def end(self):
        return self.frame_end

    def x_error(self):
        return self.main_point().x_error()

    def y_error(self):
        return self.main_point().y_error()

    def x_sigma(self):
        return self.main_point().x_sigma()

    def y_sigma(self):
        return self.main_point().y_sigma()

    def intensity(self):
        return self.main_point().intensity()

    def stddev(self):
        return self.main_point().stddev()

    def same_molecule(self, new_point, distance_threshold):
        """
        to judge if the point is part of the molecule using distance between molecule and new_point.
        :param new_point: class DataPoint
        :param distance_threshold: float.
        :return:
        """
        # if point_distance(self.main_point(), new_point) <= distance_threshold:
        #     return True
        # else:
        #     return False
        for point in self.data_history_:
            if point_distance(point, new_point) <= distance_threshold:
                return True
        return False

    def in_time_judge(self, time_now, time_threshold):
        """
        judge if the molecule is still active for the work attributing points to molecules.
        :param time_now: int, the frame no now.(int: frame is an integer!)
        :param time_threshold: int, the threshold over which the point will not be considered part of the molecule.
        :return: T/F, bool.
        """
        if time_now - self.frame_end <= time_threshold:
            return True
        else:
            return False

    def to_dictionary(self):
        return {'x': self.x(), 'y': self.y(), 'frame_start': self.start(), 'frame_end': self.end(),
                'x_error': self.x_error(), 'y_error': self.y_error(), 'x_sigma': self.x_sigma(),
                'y_sigma': self.y_sigma(), 'intensity': self.intensity(), 'stddev': self.stddev()}

    def add_time(self, t):
        self.frame_end += t
        self.frame_start += t


# @TODO: a special implementation of Molecule, using average data instead of best data. and a simple proxy.
class AvgMolecule(Molecule):
    def __init__(self, first_data):
        Molecule.__init__(self, first_data)
        self.x_ = None
        self.y_ = None

    def x(self):
        """
        use a simple proxy. when using x(), calculate it, and x will not change until add point.
        :return:
        """
        if len(self.data_history_) == 0:
            return None
        if self.x_ is None:
            xs = [point.x() for point in self.data_history_]
            self.x_ = sum(xs) / len(xs)
        return self.x_

    def add_point(self, new_point, chooser):
        # refresh the x_ and y_
        self.x_ = None
        self.y_ = None
        Molecule.add_point(self, new_point, chooser)


class MoleculeList:
    def __init__(self):
        self.molecule_list_ = []
        # self.active_list_ = []
        # self.del_list_ = []

    # def form_molecule_list(self, point_list):
    #     # clean the data in the object.
    #     # Each time, the process that attributes points to molecules will start from empty lists.
    #     self.active_list_ = []
    #     self.del_list_ = []
    #     self.molecule_list_ = []

    def to_string(self):
        return 'molecule_list: %d molecules in list' % len(self.molecule_list_)

    def read_data_from_csv(self, file_name):
        """
        read the data from a csv file. into a molecule list.
        Attention: Each molecule only has the data of main point.
        :param file_name: the file path of the csv file.
        :return: nothing.
        """
        input_file = open(file_name)
        reader = csv.DictReader(input_file)
        for row in reader:
            self.molecule_list_.append(Molecule(
                DataPoint(frame_start=row['frame_start'], frame_end=row['frame_end'], intensity=row['intensity'],
                          x=row['x'], y=row['y'], x_sigma=row['x_sigma'], y_sigma=row['y_sigma'],
                          x_error=row['x_error'], y_error=row['y_error'], stddev=row['stddev'])))

    def write_data_into_csv(self, file_name):
        """
        Write the data into a csv file.
        :param file_name: the file path to write into.
        :return: nothing.
        """
        out_file = open(file_name, 'w', newline='')
        fieldnames = [
            'frame_start', 'frame_end', 'intensity', 'x', 'y', 'x_error', 'y_error', 'x_sigma', 'y_sigma',
            'stddev',
        ]
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        for molecule in self.molecule_list_:
            writer.writerow(molecule.to_dictionary())

    def add_molecule(self, new_molecule):
        self.molecule_list_.append(new_molecule)

    def length(self):
        return len(self.molecule_list_)

    def return_molecule(self, no):
        if no < self.length():
            return self.molecule_list_[no]
        else:
            return None

    def molecule_list(self):
        return self.molecule_list_

    # @TODO: the function about scatter.
    def write_to_scatter(self, scatter):
        pass

    # @TODO: has not finished it yet.
    def merge_molecule_list(self, molecule_list):
        if self.length() == 0:
            time_max_now = 0
        else:
            time_max_now = max([molecule.end() for molecule in self.molecule_list()])
        for molecule in molecule_list:
            data_dict = molecule.to_dictionary()
            new_molecule = Molecule(
                DataPoint(frame_start=data_dict['frame_start'], frame_end=data_dict['frame_end'],
                          intensity=data_dict['intensity'], x=data_dict['x'], y=data_dict['y'],
                          x_sigma=data_dict['x_sigma'], y_sigma=data_dict['y_sigma'],
                          x_error=data_dict['x_error'], y_error=data_dict['y_error'], stddev=data_dict['stddev']))
            new_molecule.add_time(time_max_now)
            self.add_molecule(new_molecule=new_molecule)


class MoleculeFormer:
    def __init__(self, chooser, time_threshold, distance_threshold):
        self.active_list_ = []
        self.del_list_ = []
        self.molecules_ = MoleculeList()
        self.chooser = chooser
        self.time_threshold_ = time_threshold
        self.distance_threshold_ = distance_threshold

    def form_molecules(self, point_list):
        """
        form the molecule list
        :param point_list: class DataList, the list of DataPoint to form the molecule list.
        :return: the molecule list formed.
        """
        for i in range(0, point_list.length()):
            check_result = self.check_molecules(point_list.return_point(i))
            if check_result == -1:
                self.molecules_.add_molecule(Molecule(point_list.return_point(i)))
                self.active_list_.append(self.molecules_.length()-1)
            else:
                self.molecules_.return_molecule(check_result).add_point(
                    new_point=point_list.return_point(i), chooser=self.chooser)
            """
            # this part of code is made to debug. I want to find why the molecule generation process does not
            # work as I design. 0 to 2 is because there is fault point in the result of the test case from 
            # frame 0 to frame 2. many other proper candidate.
            point = point_list.return_point(i)
            if point.frame_start() == 0 and point.frame_end() == 2:
                print('point at %s , %s, from %s to %s, check result: %s' % (
                    point.x(), point.y(), point.frame_start(), point.frame_end(), check_result
                ))
            """

            self.clear_active()
        return self.molecules_

    def check_molecules(self, point_now):
        """
        check if the point is a new molecule or part of existing molecule.
        :param point_now: class DataPoint, the new point.
        :return: int, if >=0 : the number of the existing molecule that the new point belongs to.
                  return -1 if the molecule is a new one.
        """
        for no in self.active_list_:
            if self.molecules_.return_molecule(no).in_time_judge(point_now.frame_start(), self.time_threshold_):
                if self.molecules_.return_molecule(no).same_molecule(point_now, self.distance_threshold_):
                    return no
            else:
                self.del_list_.append(no)
        return -1

    def clear_active(self):
        for no in self.del_list_:
            self.active_list_.remove(no)
        self.del_list_ = []
