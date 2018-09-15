# ---------------------------------------------
# data_analyzer.py
# the class to analyze the data of molecules.
# ---------------------------------------------
import fit_analyzer
from PIL import Image
import data
import numpy as np
from abc import abstractmethod
import module_base
import math
import graph


def img_matrix_sum(img, locations):
    frame = fit_analyzer.check_frame_size(img=img)
    data_sum = []
    for i in range(0, frame):
        img.seek(i)
        # data_sum.append((np.array(img)[locations[0], locations[1]]).sum())
        data_sum.append(np.array(img)[locations].sum())
    return data_sum


def central_point_selector(graph_file, graph_object):
    img = Image.open(graph_file)
    # frame, x, y = check_frame_size(img=img)
    x_min, x_max, y_min, y_max = graph_object.cover_range()
    # points = []
    x_in, y_in = [], []
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            # if graph_object.judge_points_inside(point=graph.Point(x=x + 0.5, y=y + 0.5)) == 1:
            if graph_object.judge_points_inside(point=graph.Point(x=x + 0.5, y=y + 0.5)):
                x_in.append(x)
                y_in.append(y)
    # Attention: the sequence in the numpy array! frame : y : x.
    locations = [tuple(y_in), tuple(x_in)]
    return img_matrix_sum(img=img, locations=locations)


def cover_selector(graph_file, graph_object):
    img = Image.open(graph_file)
    x_min, x_max, y_min, y_max = graph_object.cover_range()
    x_in, y_in = [], []
    points = set()
    for x in range(x_min + 1, x_max):
        for y in range(y_min + 1, y_max):
            if graph_object.judge_points_inside(point=graph.Point(x=x, y=y)):
                points.add((x - 1, y - 1))
                points.add((x - 1, y))
                points.add((x, y - 1))
                points.add((x, y))
    for (x, y) in points:
        x_in.append(x)
        y_in.append(y)
    locations = [tuple(y_in), tuple(x_in)]
    return img_matrix_sum(img=img, locations=locations)


time_line_summer = {
    'central_point_selector': central_point_selector,
    'cover_selector': cover_selector,
}


def district_analyze(data_molecule, graph_object, start_frame, end_frame):
    result, distribution = [], []
    points_in, points_out = 0, 0
    area = graph_object.area()
    time_distribution = dict()
    for i in range(start_frame, end_frame + 1):
        time_distribution[i] = 0
    for molecule in data_molecule.molecule_list():
        if molecule.start() > end_frame or molecule.end() < start_frame:
            continue
        location = graph.Point(x=molecule.x(), y=molecule.y())
        if graph_object.judge_points_inside(point=location):
            points_in += 1
            for frame_now in range(max(molecule.start(), start_frame), min(molecule.end(), end_frame) + 1):
                time_distribution[frame_now] += 1
        else:
            points_out += 1
    result.append('number of points inside: %d; outside: %d' % (points_in, points_out))
    result.append('area: %lf, density: %lf' % (area, points_in / area))
    not_alone = False
    shining_now = time_distribution[start_frame] != 0
    shining_on_now, shining_on = 0, []
    shining_off_now, shining_off = 0, []
    for key, value in time_distribution.items():
        distribution.append({'frame': key, 'number': value, 'exist': 1 if value > 0 else 0})
        if not not_alone and value > 1:
            not_alone = True
        if shining_now:
            if value == 0:
                shining_on.append(shining_on_now)
                shining_on_now = 0
                shining_off_now += 1
                shining_now = False
            else:
                shining_on_now += 1
        else:
            if value > 0:
                shining_off.append(shining_off_now)
                shining_off_now = 0
                shining_on_now += 1
                shining_now = True
            else:
                shining_off_now += 1
    if shining_now:
        shining_on.append(shining_on_now)
    else:
        shining_off.append(shining_off_now)
    if not_alone:
        result.append('not_alone')
    shining_on_after, shining_off_after = shining_on.copy(), shining_off.copy()
    if time_distribution[start_frame] == 0:
        shining_off_after.pop(0)
    else:
        shining_on_after.pop(0)
    if time_distribution[end_frame] == 0:
        if len(shining_off_after) != 0:
            shining_off_after.pop()
    elif len(shining_on_after) != 0:
        shining_on_after.pop()
    result.append('shining_on: %s, avg: %s' % (shining_on, np.mean(shining_on)))
    result.append('shining_off: %s, avg: %s' % (shining_off, np.mean(shining_off)))
    result.append('shining_on_after: %s, avg: %s' % (shining_on_after, np.mean(shining_on_after)))
    result.append('shining_off_after: %s, avg: %s' % (shining_off_after, np.mean(shining_off_after)))
    return result, distribution


def filter_molecule(old_molecule_list, graph_object=None, start_frame=None, end_frame=None):
    molecule_list = old_molecule_list.molecule_list()
    new_list = data.MoleculeList()
    tem_list = []
    if graph_object is not None:
        for molecule in molecule_list:
            # point = data.DataPoint(x=molecule.x(), y=molecule.y())
            point = graph.Point(x=molecule.x(), y=molecule.y())
            if graph_object.judge_points_inside(point=point):
                tem_list.append(molecule)
    else:
        tem_list = molecule_list
    if start_frame is not None:
        for molecule in tem_list:
            if not (molecule.start() > end_frame or molecule.end() < start_frame):
                new_list.add_molecule(new_molecule=molecule)
    else:
        for molecule in tem_list:
            new_list.add_molecule(new_molecule=molecule)
    print('old: %d, after filter: %d' % (old_molecule_list.length(), new_list.length()))
    return new_list


def merge_molecules(old_lists, merge_mode):
    new_list = data.MoleculeList()

    if merge_mode == 'same_time':
        for molecule_list in old_lists:
            for molecule in molecule_list.molecule_list():
                new_list.add_molecule(new_molecule=molecule)
    elif merge_mode == 'normal':
        for molecule_list in old_lists:
            new_list.merge_molecule_list(molecule_list=molecule_list)
    return new_list


def Pearson(data_a, data_b):
    """
    calculate the Pearson correlation of two list
    :param data_a: list of float
    :param data_b:  list of float
    :return: float, the result of Pearson correlation
    """
    if len(data_b) != len(data_a):
        print('error length')
        return 0.0
    a, b = np.array(data_a), np.array(data_b)
    length = len(a)
    value = np.sum(a*b) - np.sum(a) * np.sum(b) / length
    value /= math.sqrt((np.sum(a*a)-np.sum(a)**2/2)*(np.sum(b*b)-np.sum(b)**2/2))
    return value


class CorrelationCalculator(module_base.Singleton):
    def __init__(self):
        pass

    def calculate(self, data_a, data_b, method):
        return self.calculate_correlation(data_a, data_b, CorrelationCalculator.correlation_method[method])

    @abstractmethod
    def calculate_correlation(self, data_a, data_b, method):
        pass

    correlation_method = {
        'Pearson': Pearson,
    }


class TimeInstantAnalyzer(CorrelationCalculator):
    def calculate_correlation(self, data_a, data_b, method):
        time_list_a = [molecule.start() for molecule in data_a.molecule_list()]
        time_list_b = [molecule.start() for molecule in data_b.molecule_list()]
        if len(time_list_a) > len(time_list_b):
            time_list_a, time_list_b = time_list_b, time_list_a
        no_b, t_a, t_b = 0, [], []
        for no_a in range(0, len(time_list_a)):
            last_a = 0 if no_a == 0 else time_list_a[no_a-1]
            t_a.append(time_list_a[no_a] - last_a)
            while no_b != len(time_list_b) and time_list_b[no_b] < time_list_a[no_a]:
                no_b += 1
            # happens when A's biggest time is larger than the largest of B.
            if no_b == len(time_list_b):
                t_a.pop()
                break
            last_b = 0 if no_b == 0 else time_list_b[no_b-1]
            last_b_t = time_list_b[no_b] if no_b == 0 else time_list_b[no_b] - time_list_b[no_b-1]
            if time_list_b[no_b] - time_list_a[no_a] > time_list_a[no_a] - last_b:
                t_b.append(last_b_t)
            else:
                t_b.append(time_list_b[no_b] - last_b)
        return 'The correlation of two data is %lf' % method(t_a, t_b)


class CorrelationFactory(module_base.Singleton):
    def __init__(self):
        pass

    def return_correlation(self, type_name, parameter):
        return self.correlation_analyzers[type_name](parameter)

    @staticmethod
    def time_instant(parameter):
        # del parameter has nothing to do. I just hate the Warn to stay. del parameter will not influence outside.
        del parameter
        return TimeInstantAnalyzer()

    correlation_analyzers = {
        'time_instant': time_instant,
    }
