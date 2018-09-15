# ---------------------------------------------
# fit_analyzer.py
# the class to execute the fit process.
# See: the method of fitting:
# Zhou X, Andoy N M, Liu G, et al. Quantitative super-resolution imaging uncovers reactivity patterns on single
# nanocatalysts[J]. Nature nanotechnology, 2012, 7(4): 237.
# And also other papers about super-resolution imaging.
# Most of the fitting method can be found in the mentioned paper.
# ---------------------------------------------
import module_base
from PIL import Image
import numpy as np
import gc
import printer
import scipy.optimize as op
import scipy.constants as const
import math
import data
# import graph

from abc import abstractmethod

# import debug

# the number should be larger than the max frames of the tiff file.
VERY_BIG = 1000000


class FitAnalyzer:
    """The class to execute the fit of the data from the tiff file.
    It works as the context of the Strategy Pattern and also the Template Pattern.
    """

    def __init__(self):
        self.data_ = DataAdministrator()
        self.former_ = None
        self.stranger_counter_ = None
        self.fitter_ = None

    def fit(self, parameters):
        self.read_parameters(parameters)
        self.divide_data()
        while self.judge_end():
            self.read_data()
            self.form_sum()
            self.count_strange()
            self.fit_points()
            self.solve_data()
            # self.solve_points()
            accept_list = self.select()
            self.add_points(accept_list=accept_list)
            # self.solve_points()
            self.next_group()
            self.clean_tmp_data()
        return self.form_molecule()

    # Attention: the file path of the tiff path is also in the parameters.
    def read_parameters(self, parameters):
        """
        add parameters used in the fit process.
        :param parameters: type dict. key is the name of parameters, and the value is the value of parameters.
        :return: nothing.
        """
        # clean the former parameters at the start of fit! Or some paramters in the last fit will reserve.
        self.data_.clear_parameter()
        # print(type(parameters))
        for (key, value) in parameters.items():
            self.data_.add_parameter(key, value)
        self.data_.calculate_fraction()

    def read_data(self):
        pass

    def divide_data(self):
        pass

    def judge_end(self):
        pass

    def form_sum(self):
        self.former_ = FilterFactory().create_filter(
            self.data_.return_parameter('filter_type'), self.data_.parameter_dictionary())
        # self.data_.set_sum_matrix(self.former_.select(self.data_.data_matrix(), ))
        self.data_.set_sum_matrix(self.former_.filter(data_in=self.data_.data_matrix()))

    def count_strange(self):
        self.stranger_counter_ = StrangerFinderFactory().create_finder(
            self.data_.return_parameter('count_strange_mode'), self.data_.parameter_dictionary())
        # self.data_.set_founds(self.stranger_counter_.count_strange(self.data_.data_matrix()))
        self.data_.set_founds(self.stranger_counter_.count_strange(data_administrator=self.data_))

    def fit_points(self):
        result_list = self.data_.result_data()
        self.fitter_ = FitterFactory().create_fitter(
            fitter_type=self.data_.return_parameter('fit_method'), parameters=self.data_.parameter_dictionary(),
            sum_former=self.former_)
        founds = self.data_.founds()
        i = 0
        for point_found in founds:
            fit_result = self.fitter_.fit(data_administrator=self.data_, point_found=point_found)
            # when the fit is failed because of varied reasons.
            if fit_result is not None:
                result_list.append(fit_result)
            i += 1
            if i % 10000 == 0:
                self.data_.data_printer().print(i)

    def select(self):
        accept_list = np.ones((self.data_.result_number(), 1), int)
        for select_name in SelectorFactory().selector_list:
            if self.data_.return_parameter('filter_%s' % select_name) == 'on':
                selector = SelectorFactory().create_selector(
                    selector_name=select_name, parameters=self.data_.parameter_dictionary())
                selector.select(data_administrator=self.data_, accept_list=accept_list)
        return accept_list

    def add_points(self, accept_list):
        self.data_.add_points(accept_list=accept_list)

    def next_group(self):
        pass

    def form_molecule(self):
        molecule_former = data.MoleculeFormer(
            # chooser=data.point_chooser(self.data_.return_parameter('point_chooser')),
            chooser=data.point_chooser[self.data_.return_parameter('point_chooser')],
            time_threshold=self.data_.return_parameter('time_threshold'),
            distance_threshold=self.data_.return_parameter('pixel_threshold')
        )
        molecules = molecule_former.form_molecules(point_list=self.data_.point_list())
        # for debug and know the number of points.
        self.data_.data_printer().print('molecule numbers: %d' % molecules.length())
        self.data_.clean_points()
        return molecules

    def calculate_cycles(self):
        """
        this method is used to calculate how many cycles the process need to calculate the whole tiff file.
        used not in the base class, but in the derived classes.
        :return: int, how many cycles the fit process need.
        """
        img = Image.open(self.data_.return_parameter('graph_file'))
        self.data_.set_size(graph_size(img))
        size_all = self.data_.img_frames() * self.data_.img_x() * self.data_.img_y()
        max_size_per_time = 1024 * 1024 * self.data_.return_parameter('max_pictures')
        cycles = size_all / max_size_per_time
        cycles = int(cycles) + 1 if not cycles == int(cycles) else cycles
        self.data_.data_printer().print('cycles: %d' % int(cycles))
        return int(cycles)

    def solve_data(self):
        """
        calculate some information after the fit.
        :return:
        """
        self.solve_sigma()
        self.calculate_error()
        self.solve_points()

    def solve_points(self):
        """
        change the value of the points fit from the fit function according to the template of FitAnalyzer.
        :return:
        """
        pass

    def clean_tmp_data(self):
        self.data_.clean()

    # @TODO: to judge which one is better. Whatever, it will remain as a style of changeable part.
    def solve_sigma(self):
        """
        this implementation is not the fastest, but I think it's enough
        :return:
        """
        pixel_size = self.data_.return_parameter('pixel_size')
        for result in self.data_.result_data():
            result['x_sigma'] *= pixel_size
            result['y_sigma'] *= pixel_size
        """
        # another implementation. use matrix to do the calculation.
        x_sigma = [x['x_sigma'] for x in self.data_.result_data()]
        y_sigma = [x['y_sigma'] for x in self.data_.result_data()]
        x_sigma *= pixel_size
        y_sigma *= pixel_size
        for i in len(self.data_.result_data()):
            self.data_.result_data()[i]['x_sigma'] = x_sigma[i]
            self.data_.result_data()[i]['y_sigma'] = y_sigma[i]
        """

    def calculate_error(self):
        x_error_matrix = self.calculate_error_axis('x_sigma')
        for i in range(0, len(x_error_matrix)):
            self.data_.result_data()[i]['x_error'] = x_error_matrix[i]
        y_error_matrix = self.calculate_error_axis('y_sigma')
        for i in range(0, len(y_error_matrix)):
            self.data_.result_data()[i]['y_error'] = y_error_matrix[i]

    def calculate_error_axis(self, axis_name):
        pixel_size = self.data_.return_parameter('pixel_size')
        sigma_matrix = np.array([x[axis_name] for x in self.data_.result_data()])
        signal_matrix = np.array([x['signal'] for x in self.data_.result_data()])
        # debug.if_minus_in_nparray(sigma_matrix, 'sigma_matrix')
        # debug.if_minus_in_nparray(array=signal_matrix, info='signal_matrix')
        # polynomial_1 = np.square(sigma_matrix * pixel_size)
        polynomial_1 = np.square(sigma_matrix)
        polynomial_1 /= signal_matrix
        polynomial_2 = np.zeros(len(polynomial_1))
        polynomial_2 += math.pow(pixel_size, 2) / 12
        polynomial_2 /= signal_matrix
        # polynomial_3 = np.square(sigma_matrix * pixel_size)
        polynomial_3 = np.square(sigma_matrix)
        polynomial_3 = \
            np.square(polynomial_3) * np.square([x['stddev'] for x in self.data_.result_data()]) * 8 * const.pi
        polynomial_3 /= (math.pow(pixel_size, 2) * np.square(signal_matrix))
        # for (array, info) in [(polynomial_1, 'poly_1'), (polynomial_2, 'poly_2'), (polynomial_3, 'poly_3')]:
        #     debug.if_minus_in_nparray(array=array, info=info)
        return np.sqrt(polynomial_1 + polynomial_2 + polynomial_3)


class FrameDivisionAnalyzer(FitAnalyzer):
    def __init__(self):
        FitAnalyzer.__init__(self)
        self.frame_step_ = None
        self.frame_now_ = None

    def divide_data(self):
        cycles = self.calculate_cycles()
        self.frame_step_ = int(self.data_.img_frames() / cycles) + 1
        self.frame_now_ = 0

    # @TODO: < or <= or other?
    def judge_end(self):
        return self.frame_now_ < self.data_.img_frames()

    def read_data(self):
        frames = self.frame_step_ if self.frame_now_ + self.frame_step_ < self.data_.img_frames() \
            else self.data_.img_frames() - self.frame_now_
        # data_matrix = np.zeros((frames, self.data_.img_x(), self.data_.img_y()), int)
        data_matrix = np.zeros((frames, self.data_.img_y(), self.data_.img_x()), int)

        start_frame = self.data_.return_parameter('start_frame')
        start_x, end_x = self.data_.return_parameter('start_x'), self.data_.return_parameter('end_x')
        start_y, end_y = self.data_.return_parameter('start_y'), self.data_.return_parameter('end_y')
        # print('start_x: %d, end_x: %d, start_y: %d, end_y: %d' % (start_x, end_x, start_y, end_y))
        img = Image.open(self.data_.return_parameter('graph_file'))
        for i in range(0, frames):
            img.seek(start_frame + self.frame_now_ + i)
            data_matrix[i] = np.array(img)[start_y:end_y, start_x:end_x]
        self.data_.set_data_matrix(data_matrix)

    def next_group(self):
        self.frame_now_ += self.frame_step_

    def solve_points(self):
        results = self.data_.result_data()
        start_frame, start_x, start_y = self.data_.return_parameter('start_frame'), \
                                        self.data_.return_parameter('start_x'), self.data_.return_parameter('start_y')
        for result in results:
            result['frame_start'] += self.frame_now_ + start_frame
            result['frame_end'] += self.frame_now_ + start_frame
            result['x'] += start_x
            result['y'] += start_y


class XDivisionAnalyzer(FitAnalyzer):
    def __init__(self):
        FitAnalyzer.__init__(self)
        self.x_step_ = None
        self.x_now_ = None

    def solve_points(self):
        results = self.data_.result_data()
        start_frame, start_x, start_y = self.data_.return_parameter('start_frame'), \
                                        self.data_.return_parameter('start_x'), self.data_.return_parameter('start_y')
        for result in results:
            result['frame_start'] += start_frame
            result['frame_end'] += start_frame
            result['x'] += self.x_now_ + start_x
            # result['x'] += self.x_now_
            result['y'] += start_y

    def divide_data(self):
        cycles = self.calculate_cycles()
        self.x_step_ = int(self.data_.img_x() / cycles) + 1
        self.x_now_ = 0
        # self.x_now_ = self.data_.return_parameter('start_x')

    def judge_end(self):
        return self.x_now_ < self.data_.img_x()

    def read_data(self):
        x_length = self.x_step_ + self.data_.return_parameter('sum_size') - 1 \
            if self.x_now_ + self.x_step_ + self.data_.return_parameter('sum_size') - 1 < self.data_.img_x() \
            else self.data_.img_x() - self.x_now_
        # data_matrix = np.zeros((self.data_.img_frames(), x_length, self.data_.img_y()), int)
        # self.data_.data_printer().print('x_length: %d; x_now: %d' % (x_length, self.x_now_))
        data_matrix = np.zeros((self.data_.img_frames(), self.data_.img_y(), x_length), int)

        img = Image.open(self.data_.return_parameter('graph_file'))
        start_frame, end_frame = self.data_.return_parameter('start_frame'), self.data_.return_parameter('end_frame')
        start_x, end_x = self.data_.return_parameter('start_x'), self.data_.return_parameter('end_x')
        start_y, end_y = self.data_.return_parameter('start_y'), self.data_.return_parameter('end_y')
        # if img:
        #     print(self.data_.return_parameter('graph_file'))
        # for i in range(0, self.data_.img_frames()):
        # print('start_x: %d, end_x: %d, start_frame: %d, end_frame: %d, start_y: %d, end_y: %d' % (
        #     self.x_now_+start_x, self.x_now_+start_x+x_length, start_frame, end_frame, start_y, end_y))
        for i in range(start_frame, start_frame + self.data_.img_frames()):
            img.seek(i)
            data_tem = np.array(img)
            # print(data_tem.shape)
            # data_matrix[i] = data_tem[self.x_now_:self.x_now_ + x_length, :].copy()
            # the version without partition function.
            # data_matrix[i] = data_tem[:, self.x_now_:self.x_now_ + x_length].copy()
            # the version with partition
            data_matrix[i] = data_tem[start_y:end_y, self.x_now_+start_x:self.x_now_+start_x + x_length].copy()
            # In order to clear the memory. test several methods before.
            del data_tem
            gc.collect()
        self.data_.set_data_matrix(data_matrix)

    def next_group(self):
        self.x_now_ += self.x_step_


class FitAnalyzerFactory(module_base.Singleton):
    @staticmethod
    def create_analyzer(analyzer_type):
        return FitAnalyzerFactory.analyzers[analyzer_type]()

    analyzers = {
        'time_pattern': FrameDivisionAnalyzer,
        'x_axis_pattern': XDivisionAnalyzer,
    }


class DataAdministrator(module_base.Singleton):
    """The class to manage the data in the process of fit points.
    Inheriting class Singleton: there is only one group of data in the program. the limit of memory.
    Attributes:
        self.parameters_, dictionary: the parameters used in the fit process.
        self.data_matrix_: a 3D matrix of int, read from the tiff file, the gray scale value of the picture.
    """
    default_values = {
        'start_x': 0,
        'end_x': VERY_BIG,
        'start_frame': 0,
        'end_frame': VERY_BIG,
        'start_y': 0,
        'end_y': VERY_BIG,
    }

    def __init__(self):
        self.parameters_ = {}
        self.data_matrix_ = None
        self.graph_size_ = None
        self.sum_matrix_ = None
        self.founds_ = None
        self.printer_ = printer.PrinterFactory.return_printer()
        self.result_ = []
        self.fraction_ = None
        self.points_ = data.DataList()

    def clean(self):
        self.result_ = []

    def clean_points(self):
        self.points_ = data.DataList()

    def return_parameter(self, parameter_name):
        """return the value of parameter. If not existed, return the default value.
        Attributes:
            parameter_name: the name of the parameter to return.
        Return:
            the value of parameter. default to be None.
        """
        # return self.parameters_.get(parameter_name, None)
        return self.parameters_.get(parameter_name, DataAdministrator.default_values.get(parameter_name, None))

    def parameter_dictionary(self):
        return self.parameters_

    def clear_parameter(self):
        """
        clear the dictionary of parameter.
        :return:
        No return
        """
        self.parameters_.clear()

    def add_parameter(self, parameter_name, value):
        """
        add the value of parameter in the dictionary
        :param parameter_name: the name of the parameter.
        :param value: the value of the parameter.
        :return: nothing.
        """
        self.parameters_[parameter_name] = value

    def data_matrix(self):
        return self.data_matrix_

    def set_data_matrix(self, data_matrix):
        self.data_matrix_ = data_matrix

    def sum_matrix(self):
        return self.sum_matrix_

    def set_sum_matrix(self, sum_matrix):
        self.sum_matrix_ = sum_matrix

    def img_frames(self):
        return self.graph_size_[0]

    def img_x(self):
        # return self.graph_size_[1]
        return self.graph_size_[2]

    def img_y(self):
        # return self.graph_size_[2]
        return self.graph_size_[1]

    def set_size(self, size):
        self.graph_size_ = []
        if self.parameters_.get('start_frame') is not None and self.parameters_['end_frame'] < size[0]:
            self.graph_size_.append(self.parameters_['end_frame'] - self.parameters_['start_frame'])
        else:
            self.graph_size_.append(size[0])
        if self.parameters_.get('start_x') is not None and self.parameters_['end_x'] < size[2] \
                and self.parameters_.get('start_y') is not None and self.parameters_['end_y'] < size[1]:
            self.graph_size_ += [self.parameters_['end_y'] - self.parameters_['start_y'],
                                 self.parameters_['end_x'] - self.parameters_['start_x']]
        else:
            self.graph_size_ += [size[1], size[2]]
            # if self.parameters_['end_x'] <= size[2] and self.parameters_['end_y'] <= size[1] \
            #         and self.parameters_['end_frame'] <= size[0]:
            #     self.graph_size_ = [self.parameters_['end_frame'] - self.parameters_['start_frame'],
            #                         self.parameters_['end_y'] - self.parameters_['start_y'],
            #                         self.parameters_['end_x'] - self.parameters_['start-x']]
            # self.graph_size_ = size

    def data_printer(self):
        return self.printer_

    def set_founds(self, founds):
        self.founds_ = founds

    def founds(self):
        return self.founds_

    def result_data(self):
        return self.result_

    def result_number(self):
        return len(self.result_)

    def return_data_list(self, parameter_name):
        try:
            return np.array([x[parameter_name] for x in self.result_])
        except KeyError:
            return np.array([])

    def calculate_fraction(self):
        fraction = self.parameters_['camera_gain']
        fraction *= self.parameters_['electron_creation'] * self.parameters_['wave_length'] * const.e
        fraction /= (self.parameters_['EM_gain'] * self.parameters_['quantum_efficiency'] * const.h * const.c)
        self.fraction_ = fraction

    def return_fraction(self):
        return self.fraction_

    def add_points(self, accept_list):
        for i in range(0, len(accept_list)):
            if accept_list[i] != 0:
                info = self.result_[i]
                new_point = data.DataPoint(
                    frame_start=info['frame_start'], frame_end=info['frame_end'], intensity=info['intensity'],
                    x=info['x'], y=info['y'], x_sigma=info['x_sigma'], y_sigma=info['y_sigma'],
                    x_error=info['x_error'], y_error=info['y_error'], stddev=info['stddev'],
                )
                self.points_.add_data(new_point)

    def point_list(self):
        return self.points_


def check_frame_size(img):
    """
    check the max frame of the image.
    use a trick: the seek will stop if the expected number is larger than the number of frames of the tiff.
    :param img: type 'PIL.TiffImagePlugin.TiffImageFile', using Image.open(file) to define.
    :return: int, the length of the tiff file.
    """
    n = img.tell()
    try:
        img.seek(VERY_BIG)
    except EOFError:
        pass
    length = img.tell() + 1
    # back to the start state.
    img.seek(n)
    return length


def graph_size(img):
    """
    check the size of the image.
    :param img: type 'PIL.TiffImagePlugin.TiffImageFile', using Image.open(file) to define.
    :return: (int, int, int): frame, x, y
    """
    frame = check_frame_size(img)
    tem = np.array(img)
    (x, y) = tem.shape
    return frame, x, y


class FilterFactory(module_base.Singleton):
    def __init__(self):
        self.__square_filter = dict()

    def create_filter(self, type_filter, parameters):
        return FilterFactory.filter_chooser[type_filter](self, parameters)

    def create_square_filter(self, parameters):
        if self.__square_filter.get(parameters['sum_size'], None) is None:
            self.__square_filter[parameters['sum_size']] = SquareFilter(parameters['sum_size'])
        return self.__square_filter[parameters['sum_size']]

    filter_chooser = {
        'square': create_square_filter,
    }


class Filter:
    def __init__(self):
        self.coord_ = None

    def filter(self, data_in):
        """
        the filter.
        :param data_in: numpy.array. matrix of data.
        :return: matrix after filter.
        """
        pass

    def form_coordinate(self):
        pass

    def form_matrix(self, data_administrator, point_found):
        if isinstance(point_found, DataToFit):
            data_matrix = data_administrator.data_matrix()
            matrix = self.base_matrix()
            background = self.base_matrix()
            x, y = point_found.x_location(), point_found.y_location()
            matrix += np.sum(
                self.form_data(data_matrix, x, y, point_found.start_frame(), point_found.end_frame()), axis=0)
            if point_found.start_frame() != point_found.start_background():
                background += np.sum(
                    self.form_data(data_matrix, x, y, point_found.start_background(), point_found.start_frame()), axis=0
                )
            if point_found.end_frame() != point_found.end_background():
                background += np.sum(
                    self.form_data(data_matrix, x, y, point_found.end_frame(), point_found.end_background()), axis=0
                )
            # matrix -= background * (point_found.end_background() - point_found.start_frame()) / (
            #     point_found.start_background() - point_found.start_frame() + point_found.end_background()
            #     - point_found.end_frame()
            # )
            # matrix -= background * (point_found.end_background() - point_found.start_frame()) / (
            #     - point_found.start_background() + point_found.start_frame() + point_found.end_background()
            #     - point_found.end_frame()
            # )
            matrix -= background * (point_found.end_frame() - point_found.start_frame()) / (
                - point_found.start_background() + point_found.start_frame() + point_found.end_background()
                - point_found.end_frame()
            )
            return matrix.ravel()

    @abstractmethod
    def form_data(self, matrix, x, y, frame_from, frame_to):
        # # abstract method, just for no warning!! In fact, this implementation will never be called.
        return np.zeros((2, 2))
        # if use pass, it will still warn me... so ANNOYING!
        # pass

    @abstractmethod
    def base_matrix(self):
        return np.zeros((2, 2))

    def in_filter(self, x, y):
        pass


class SquareFilter(Filter):
    def __init__(self, size):
        Filter.__init__(self)
        self.size = size

    def filter(self, data_in):
        (frames, x_length, y_length) = data_in.shape
        sum_matrix = np.zeros((frames, x_length - self.size + 1, y_length - self.size + 1), int)
        for x in range(0, self.size):
            for y in range(0, self.size):
                # print('%s %s' % (x, y))
                sum_matrix += data_in[:, x:x + x_length - self.size + 1, y:y + y_length - self.size + 1]
                gc.collect()
        return sum_matrix

    def form_coordinate(self):
        """
        form the matrix used as the coordinate in the fit process.
        :return: numpy.array 2, self.size ** 2
        """
        if self.coord_ is not None:
            return self.coord_
        coordinate = np.zeros((2, self.size ** 2))
        x = 0
        y = 0
        for i in range(0, self.size ** 2):
            coordinate[0][i] = x
            coordinate[1][i] = y
            y += 1
            if y == self.size:
                y = 0
                x += 1
        self.coord_ = coordinate
        return coordinate

    def form_data(self, matrix, x, y, frame_from, frame_to):
        # return matrix[frame_from:frame_to, x:x + self.size, y:y + self.size]
        return matrix[frame_from:frame_to, y:y + self.size, x:x + self.size]

    def base_matrix(self):
        return np.zeros((self.size, self.size))

    def in_filter(self, x, y):
        return 0 < x < self.size and 0 < y < self.size


class StrangerFinder:
    def __init__(self):
        pass

    def count_strange(self, data_administrator):
        pass


class TwoThresholdFinder(StrangerFinder):
    def __init__(self, low_threshold, high_threshold):
        StrangerFinder.__init__(self)
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    # @abstractmethod
    def calculate_special_matrix(self, data_administrator):
        """
        This method is used to calculate the special matrix used in the method count_strange.
        This implementation is a .... joke. It is an abstract method, but without returning anything, the method
        count_strange will warn in the pyCharm... you know, it's obviously annoying, which I can't stand. So I make the
        abstract method return something, whose formula is the same with real result.
        :param data_administrator:
        :return: a, b,
        a: special matrix, the matrix which the program need to find strange points later;
        b: to_find: tuple, the list of the location of the points found in the matrix. frame, x, y.
        """
        return np.zeros((2, 2)), ((0, 1), (0, 1), (0, 1))

    def count_strange(self, data_administrator):
        """
        find the strange points using the two threshold method.
        :param data_administrator: class DataAdministrator.
        :return: six lists: start_frames, end_frames, start_background, end_background, x_locations, y_locations.
        """
        special_matrix, to_find = self.calculate_special_matrix(data_administrator)
        background_pictures = data_administrator.return_parameter('background_pictures')
        # start_frames, end_frames, start_background, end_background, x_locations, y_locations = [], [], [], [], [], []
        to_fit = []
        for i in range(0, len(to_find[0])):
            # to show that the program is running.
            if i % 100000 == 0:
                data_administrator.data_printer().print(i)
            # in this method, if the previous frame is also special, then the data has been used.
            frame, y, x = to_find[0][i], to_find[1][i], to_find[2][i]
            # if i > 0 and special_ma trix[to_find[0][i - 1]][to_find[1][i]][to_find[2][i]] > 0:
            #     continue
            if frame > 0 and special_matrix[frame - 1][y][x] > 0:
                continue
            # frame_end, add_up = frame + 1, special_matrix[frame][x][y]
            frame_end, add_up = frame + 1, special_matrix[frame][y][x]
            # while frame_end < special_matrix.shape[0] and special_matrix[frame_end][x][y] > 0:
            while frame_end < special_matrix.shape[0] and special_matrix[frame_end][y][x] > 0:
                # add_up += special_matrix[frame_end][x][y]
                add_up += special_matrix[frame_end][y][x]
                frame_end += 1
            # compare the add up number with the threshold.
            # print(add_up)
            if add_up < self.high_threshold - self.low_threshold:
                continue
            back_start, back_end = frame, frame_end
            while frame - back_start < background_pictures \
                    and back_start - 1 >= 0 > special_matrix[back_start - 1][y][x]:
                back_start -= 1
            while back_end - frame_end <= background_pictures and back_end < special_matrix.shape[0] \
                    and special_matrix[back_end][y][x] < 0:
                back_end += 1
            # this means that there is not background picture.
            if back_start == frame and back_end == frame_end:
                continue
            to_fit.append(DataToFit(
                start_frame=frame, end_frame=frame_end, start_background=back_start, end_background=back_end,
                x_location=x, y_location=y))
            # start_frames.append(frame)
            # end_frames.append(frame_end)
            # start_background.append(back_start)
            # end_background.append(back_end)
            # x_locations.append(x)
            # y_locations.append(y)
        data_administrator.data_printer().print('prepare for fit: %d' % len(to_fit))
        return to_fit
        # return [start_frames, end_frames, start_background, end_background, x_locations, y_locations]


class DataToFit:
    """
    The class of the result of count strange.
    """

    def __init__(self, start_frame, end_frame, start_background, end_background, x_location, y_location):
        self.start_frame_ = start_frame
        self.end_frame_ = end_frame
        self.start_background_ = start_background
        self.end_background_ = end_background
        self.x_location_ = x_location
        self.y_location_ = y_location

    def start_frame(self):
        return self.start_frame_

    def end_frame(self):
        return self.end_frame_

    def start_background(self):
        return self.start_background_

    def end_background(self):
        return self.end_background_

    def x_location(self):
        return self.x_location_

    def y_location(self):
        return self.y_location_


class AverageFinder(TwoThresholdFinder):
    def __init__(self, low_threshold, high_threshold):
        TwoThresholdFinder.__init__(self, low_threshold, high_threshold)

    def calculate_special_matrix(self, data_administrator):
        average_matrix = np.average(data_administrator.sum_matrix(), axis=0)
        stddev_matrix = np.std(data_administrator.sum_matrix(), axis=0)
        limit_matrix = average_matrix + self.low_threshold * stddev_matrix
        special_matrix = (data_administrator.sum_matrix() - limit_matrix) / stddev_matrix
        to_find = np.where(special_matrix > 0)
        # data_administrator.data_printer().print('%d' % len(to_find))
        return special_matrix, to_find


class MediumFinder(TwoThresholdFinder):
    def __init__(self, low_threshold, high_threshold):
        TwoThresholdFinder.__init__(self, low_threshold, high_threshold)

    def calculate_special_matrix(self, data_administrator):
        median_matrix = np.median(data_administrator.sum_matrix(), axis=0)
        distance_matrix = np.percentile(data_administrator.sum_matrix(), q=75, axis=0) - median_matrix
        limit_matrix = median_matrix + self.low_threshold * distance_matrix
        special_matrix = (data_administrator.sum_matrix() - limit_matrix) / distance_matrix
        to_find = np.where(special_matrix > 0)
        # data_administrator.data_printer().print('%d' % len(to_find))
        return special_matrix, to_find


class QuaternionFinder(TwoThresholdFinder):
    def __init__(self, low_threshold, high_threshold):
        TwoThresholdFinder.__init__(self, low_threshold, high_threshold)

    def calculate_special_matrix(self, data_administrator):
        quarter_matrix = np.percentile(data_administrator.sum_matrix(), q=75, axis=0)
        distance_matrix = quarter_matrix - np.percentile(data_administrator.sum_matrix(), q=25, axis=0)
        limit_matrix = quarter_matrix + distance_matrix * self.low_threshold
        special_matrix = (data_administrator.sum_matrix() - limit_matrix) / distance_matrix
        to_find = np.where(special_matrix > 0)
        # data_administrator.data_printer().print('%d' % len(to_find[0]))
        return special_matrix, to_find


class StrangerFinderFactory(module_base.Singleton):
    def __init__(self):
        self.__average_finder = dict()
        self.__quartet_finder = dict()
        self.__medium_finder = dict()

    def create_finder(self, type_finder, parameters):
        return StrangerFinderFactory.finder_chooser[type_finder](self, parameters)

    def create_average_finder(self, parameters):
        if self.__average_finder.get((parameters['low_threshold'], parameters['high_threshold'])) is None:
            self.__average_finder[(parameters['low_threshold'], parameters['high_threshold'])] = AverageFinder(
                parameters['low_threshold'], parameters['high_threshold'])
        return self.__average_finder[(parameters['low_threshold'], parameters['high_threshold'])]

    def create_medium_finder(self, parameters):
        if self.__medium_finder.get((parameters['low_threshold'], parameters['high_threshold'])) is None:
            self.__medium_finder[(parameters['low_threshold'], parameters['high_threshold'])] = MediumFinder(
                parameters['low_threshold'], parameters['high_threshold']
            )
        return self.__medium_finder[(parameters['low_threshold'], parameters['high_threshold'])]

    def create_quaternion_finder(self, parameters):
        # print('%s %s' % (parameters['low_threshold'], parameters['high_threshold']))
        if self.__quartet_finder.get((parameters['low_threshold'], parameters['high_threshold'])) is None:
            self.__quartet_finder[(parameters['low_threshold'], parameters['high_threshold'])] = QuaternionFinder(
                parameters['low_threshold'], parameters['high_threshold']
            )
        return self.__quartet_finder[(parameters['low_threshold'], parameters['high_threshold'])]

    finder_chooser = {
        'average_strategy': create_average_finder,
        'medium_number_strategy': create_medium_finder,
        'quaternion_strategy': create_quaternion_finder,
    }


class Fitter:
    def __init__(self, fit_function, sum_former):
        # after thinking, I decide to make coordinate_matrix, guess members, in order to reduce the number of formal
        # parameters.
        self.fit_function_ = fit_function
        self.sum_former_ = sum_former
        self.coordinate_matrix_ = None
        self.guess_ = None
        self.matrix_ = None

    def fit(self, data_administrator, point_found):
        self.coordinate_matrix_ = self.sum_former_.form_coordinate()
        central_coordinate = [np.average(self.coordinate_matrix_[0, :]), np.average(self.coordinate_matrix_[1, :])]
        # self.guess_ = self.fit_function_.guess_parameters(central_coordinate)
        # the matrix has been ravelled in the method of Filter(sum_former_).
        # Attention: ravel() is in function Filter.form_matrix()!
        self.matrix_ = self.sum_former_.form_matrix(data_administrator, point_found)
        max_signal = np.max(self.matrix_)
        self.guess_ = self.fit_function_.guess_parameters(central_coordinate=central_coordinate, max_signal=max_signal)
        parameter_list = self.fit_point()
        # solve the list, get a dictionary.
        result = self.fit_function_.solve_result(result=parameter_list, sum_former=self.sum_former_)
        if result is None:
            return None
        result['stddev'] = self.fit_function_.calculate_stddev(
            real_data=self.matrix_, fit_parameters=parameter_list, coordinate=self.coordinate_matrix_,
            fraction=data_administrator.return_fraction())
        result['signal'] = np.sum(self.matrix_) * data_administrator.return_fraction()
        result['frame_start'] = point_found.start_frame()
        result['frame_end'] = point_found.end_frame() - 1
        result['x'] += point_found.x_location()
        result['y'] += point_found.y_location()
        # print('%s %s %s %s' % (result['x'], point_found.x_location(), result['y'], point_found.y_location()))
        return result

    @abstractmethod
    def fit_point(self):
        pass


class LMFitter(Fitter):
    def __init__(self, fit_function, sum_former):
        Fitter.__init__(self, fit_function, sum_former)

    def fit_point(self):
        try:
            # p0: the initial guess for parameters.
            result = op.curve_fit(
                f=self.fit_function_.function(), xdata=self.coordinate_matrix_, ydata=self.matrix_, p0=self.guess_)
            # this process is to get the list of parameters from the result of function: op.curve_fit.
            parameter_list = result[0]
            return parameter_list
            # this implementation has been discarded because the solve_result is the same among different Fitters.
            # return self.fit_function_.solve_result(result=parameter_list, sum_former=self.sum_former_)
        # the fit may fail, then throw a runtime error.
        except RuntimeError:
            return None


# @TODO: need parameter 'fit_method', 'fit_function'
class FitterFactory(module_base.Singleton):
    def __init__(self):
        self.__fitter_ = {}

    def create_fitter(self, fitter_type, parameters, sum_former):
        return FitterFactory.fitter_chooser[fitter_type](self, parameters, sum_former)

    def create_LM_fitter(self, parameters, sum_former):
        if self.__fitter_.get(('lm', parameters['fit_function'], sum_former)) is None:
            self.__fitter_[('lm', parameters['fit_function'], sum_former)] = LMFitter(
                FunctionFactory().create_func(parameters['fit_function']), sum_former)
            # print(self.__fitter_.keys())
        return self.__fitter_[('lm', parameters['fit_function'], sum_former)]

    fitter_chooser = {
        'Levenberg-Marquardt': create_LM_fitter,
    }


def fit_2D_Gaussian(x_data, intensity, x_loc, sigma_x, y_loc, sigma_y):
    """
    a kind of fit function.
    :param x_data: list, data of the coordinate.
    :param intensity: float, intensity of the shining.
    :param x_loc: float, the location of point on the x axis
    :param sigma_x: float, the sigma on the x axis.
    :param y_loc: same with x.
    :param sigma_y: same with x.
    :return: the value of the 2D Gaussian.
    """
    return intensity * np.exp(-0.5 * ((x_data[0] - x_loc) / sigma_x) ** 2 - 0.5 * ((x_data[1] - y_loc) / sigma_y) ** 2)


class Function:
    def __init__(self, func):
        self.func_ = func

    def function(self):
        return self.func_

    def calculate(self, coordinate, parameters):
        """
        return the calculate result using parameters derived by fitting data.
        need to be different among functions because different functions using different number of parameters...
        If without this feature, I will not write class Function, and a dictionary is enough.
        :param coordinate: numpy.array, use to calculate as argument using the function.
        :param parameters: the parameters in the function, different in the derived classes.
        :return: float or numpy.array( mostly numpy.array)
        """
        pass

    def guess_parameters(self, central_coordinate, max_signal=100.0):
        pass

    def solve_result(self, result, sum_former):
        pass

    def calculate_stddev(self, real_data, fit_parameters, coordinate, fraction):
        """
        calculate the std of the difference between real data and fit data
        :param real_data: numpy of float, the real data from the experiment.
        :param fit_parameters: list of float, the parameters from the fit.
        :param coordinate: numpy of float/int, the coordinate of data.
        :param fraction: float, the fraction from experiment number to the number of fluorescence.
        :return:
        """
        fit_data = self.calculate(coordinate=coordinate, parameters=fit_parameters)
        difference_data = (fit_data - real_data) * fraction
        return np.std(difference_data)


class Function2DGaussian(Function):
    def __init__(self):
        Function.__init__(self, fit_2D_Gaussian)

    def calculate(self, coordinate, parameters):
        return self.func_(coordinate, parameters[0], parameters[1], parameters[2], parameters[3], parameters[4])

    def guess_parameters(self, central_coordinate, max_signal=100.0):
        # So far, I don't think it is reasonable, but best among solutions I have now.
        return [max_signal, central_coordinate[0], 1.0, central_coordinate[1], 1.0]

    # @TODO: more about the help file of curve_fit.
    def solve_result(self, result, sum_former):
        """
        solve the result from the function op.curve_fit.
        :param result: list from class Fit.the sequence is the same as the guess or the function link to this
         Func. want more, see:
        :param sum_former: class Filter, used to judge if the point is in the range of the filter.
        :return: a dictionary, the key is the meaning of the value, and the value is the value.
        """
        if result is None:
            return None
        if not sum_former.in_filter(result[1], result[3]):
            return None
        return {
            'intensity': abs(result[0]),
            'x': result[1], 'x_sigma': abs(result[2]),
            'y': result[3], 'y_sigma': abs(result[4])
        }
        # [result[0][0], result[0][1], abs(result[0][2]), result[0][3], abs(result[0][4])]


class FunctionFactory(module_base.Singleton):
    """
    this factory is more easy, because every derived class of class Function use the only one flyweight.
    """

    def __init__(self):
        self.__funcs_ = {}

    def create_func(self, function_name):
        if self.__funcs_.get(function_name, None) is None:
            self.__funcs_[function_name] = FunctionFactory.functions[function_name]
        return self.__funcs_[function_name]

    functions = {
        '2D_Gaussian': Function2DGaussian(),
    }


class Selector:
    def __init__(self):
        pass

    def select(self, data_administrator, accept_list):
        pass


class TwoBorderSelector(Selector):
    def __init__(self, low_border, high_border):
        Selector.__init__(self)
        self.low_border_ = low_border
        self.high_border_ = high_border

    def select_array(self, array_to_select, accept_list):
        not_in_range = np.where(array_to_select < self.low_border_)
        for l in not_in_range:
            accept_list[l] = int(0)
        not_in_range = np.where(array_to_select > self.high_border_)
        for l in not_in_range:
            accept_list[l] = int(0)


class AxisSelector(TwoBorderSelector):
    def __init__(self, low_border, high_border, parameter_name):
        TwoBorderSelector.__init__(self, low_border=low_border, high_border=high_border)
        self.parameter_name_ = parameter_name

    def select(self, data_administrator, accept_list):
        self.select_axis(data_administrator=data_administrator, accept_list=accept_list, axis_name='x')
        self.select_axis(data_administrator=data_administrator, accept_list=accept_list, axis_name='y')

    def select_axis(self, data_administrator, accept_list, axis_name):
        value_list = data_administrator.return_data_list(parameter_name='%s_%s' % (self.parameter_name_, axis_name))
        self.select_array(array_to_select=value_list, accept_list=accept_list)


class DifferenceSelector(TwoBorderSelector):
    def __init__(self, low_threshold, high_threshold):
        TwoBorderSelector.__init__(self, low_border=low_threshold, high_border=high_threshold)

    def select(self, data_administrator, accept_list):
        value_list = \
            data_administrator.return_data_list(parameter_name='sigma_x') / \
            data_administrator.return_data_list(parameter_name='sigma_y')
        self.select_array(array_to_select=value_list, accept_list=accept_list)


class SelectorFactory(module_base.Singleton):
    def __init__(self):
        self.__selectors_ = dict()

    def create_selector(self, selector_name, parameters):
        return SelectorFactory.selectors[selector_name](self, selector_name, parameters)

    def create_axis_selector(self, selector_name, parameters):
        # low_limit = parameters['%s_low_limit'] % selector_name
        # high_limit = parameters['%s_high_limit'] % selector_name
        low_limit, high_limit = self.get_two_border(selector_name, parameters)
        if self.__selectors_.get((selector_name, low_limit, high_limit), None) is None:
            self.__selectors_[(selector_name, low_limit, high_limit)] = AxisSelector(
                low_border=low_limit, high_border=high_limit, parameter_name=selector_name
            )
        return self.__selectors_[(selector_name, low_limit, high_limit)]

    @staticmethod
    def get_two_border(selector_name, parameters):
        return parameters['%s_low_limit' % selector_name], parameters['%s_high_limit' % selector_name]

    def create_xy_difference_selector(self, selector_name, parameters):
        low_limit, high_limit = self.get_two_border(selector_name=selector_name, parameters=parameters)
        if self.__selectors_.get((selector_name, low_limit, high_limit), None) is None:
            self.__selectors_[(selector_name, low_limit, high_limit)] = DifferenceSelector(
                low_threshold=low_limit, high_threshold=high_limit)
        return self.__selectors_[(selector_name, low_limit, high_limit)]

    selector_list = [
        'error', 'sigma', 'xy_difference',
    ]

    selectors = {
        'error': create_axis_selector,
        'sigma': create_axis_selector,
        'xy_difference': create_xy_difference_selector,
    }


# I found a method to finish this work more elegantly and universally... well, just after I have finished this method.
# See method return_parameter() and dict default_values in class DataAdministrator.
# def read_data_range(self, data_administrator):
#     start_frame = data_administrator.return_parameter('start_frame')
#     start_frame = 0 if start_frame is None else start_frame
#     end_frame = data_administrator.return_parameter('end_frame')
#     end_frame = VERY_BIG if end_frame is None else end_frame
#     start_x = data_administrator.return_parameter('start_x')
#     start_x = 0 if start_x is None else start_x
#     end_x = data_administrator.return_parameter('end_x')
#     end_x = VERY_BIG if end_x is None else end_x
#     start_y = data_administrator.return_parameter('start_y')
#     start_y = 0 if start_y is None else start_y
