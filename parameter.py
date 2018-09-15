# ---------------------------------------------
# parameter.py
# the class to the administrator of the parameters and the value check of the parameter.
# ---------------------------------------------
import error

parameters_used = {
    'fit': [
        'sum_size', 'max_pictures', 'background_pictures', 'pixel_size', 'wave_length', 'EM_gain',
        'quantum_efficiency', 'camera_gain', 'electron_creation', 'pixel_threshold', 'low_threshold',
        'high_threshold', 'filter_error', 'filter_sigma', 'filter_xy_difference', 'count_strange_mode',
        'pattern_data_mode', 'point_chooser', 'time_threshold', 'fit_function', 'filter_type', 'fit_method',
    ],
    'scatter': [
        # 'scatter_bin', 'mark_alpha', 'mark_size', 'scatter_mode', 'mark_color',
        'scatter_mode',
    ],
    'time_line': [
        'time_line_mode',
    ],
    'correlation': [
        'correlation_formula', 'correlation_data_mode',
    ]
}

parameter_dependency = {
    'filter_error': {
        'on': ['error_low_limit', 'error_high_limit'],
    },
    'filter_sigma': {
        'on': ['sigma_low_limit', 'sigma_high_limit'],
    },
    'filter_xy_difference': {
        'on': ['difference_low_limit', 'difference_high_limit'],
    },
    'scatter_mode': {
        'normal': ['scatter_bin', 'mark_alpha', 'mark_size', 'mark_color', 'mark_shape', 'mark_shape'],
    },
    'correlation_formula': {
        'Pearson': [],
    },
    'correlation_data_mode': {
        'time_instant': [],
    },
}

parameters_int = (

)

parameters_positive_int = (
    'sum_size',
    'max_pictures',
)

parameters_non_negative_int = (
    'background_pictures',
    'time_threshold',
)

parameters_float = (

)

parameters_positive_float = (
    # non-physical constants:

    # physical constants
    'pixel_size',
    'wave_length',
    'EM_gain',
    'quantum_efficiency',
    'camera_gain',
    'electron_creation',
)

parameters_non_negative_float = (
    'pixel_threshold',
    'low_threshold',
    'high_threshold',
    'error_low_limit',
    'error_high_limit',
    'sigma_low_limit',
    'sigma_high_limit',
    'difference_low_limit',
    'difference_high_limit',
)

parameters_string = (
    'input_file_path',
    'output_file_path',
    'script_path',
)

parameters_selections = {
    'on_off': ['on', 'off'],
    'count_strange_mode': [
        'average_strategy',
        'medium_number_strategy',
        'quaternion_strategy',
    ],
    'pattern_data_mode': [
        'time_pattern',
        'x_axis_pattern',
    ],
    'filter_type': [
        'square',
    ],
    'fit_method': [
        'Levenberg-Marquardt',
    ],
    'fit_function': [
        '2D_Gaussian',
    ],
    'point_chooser': [
        'intensity',
        'accuracy',
        'no',
    ],
    'time_line_mode': [
        'central_point_selector',
        'cover_selector',
    ],
    'correlation_formula': [
        'Pearson',
    ],
    'correlation_data_mode': [
        'time_instant',
    ],
}

# now, filter_positive has been set to be on all the time.
parameters_on_off = (
    # 'filter_positive',
    'filter_error',
    'filter_sigma',
    'filter_xy_difference',
)


# the class used to check the parameters.
class ParameterChecker:
    def __init__(self):
        self.parameter_checkers = {}

    def initialize(self):
        self.parameter_checkers.clear()
        self.add_parameter(parameters_int, ParameterChecker.check_int)
        self.add_parameter(parameters_float, ParameterChecker.check_float)
        # for (key, value) in parameters_selections:
        for key in list(parameters_selections.keys()):
            if key != 'on_off':
                self.parameter_checkers[key] = ParameterChecker.check_selection
        self.add_parameter(parameters_on_off, ParameterChecker.check_on_off)
        self.add_parameter(parameters_string, ParameterChecker.check_string)
        self.add_parameter(parameters_non_negative_float, ParameterChecker.check_non_negative)
        self.add_parameter(parameters_non_negative_int, ParameterChecker.check_non_negative_int)
        self.add_parameter(parameters_positive_float, ParameterChecker.check_positive_float)
        self.add_parameter(parameters_positive_int, ParameterChecker.check_positive_int)

    def add_parameter(self, list_of_key, value_function):
        for key in list_of_key:
            self.parameter_checkers[key] = value_function

    # check the parameters using the dictionary inside the class
    def check_valid(self, line, parameter, value):
        # return self.parameter_checkers[parameter](line, parameter, value)
        # there is no keyword...
        # print(parameter)
        return self.parameter_checkers.get(
            parameter, unknown_parameter)(line, parameter, value)

    # the function used to check type.
    @staticmethod
    def check_type(line, parameter, value, right_type):
        if type(value) == right_type:
            return None
        else:
            return error.ErrorInvalidType(
                line=line, parameter_name=parameter, wrong_type=type(value), right_type=right_type)

    @staticmethod
    def check_int(line, parameter, value):
        return ParameterChecker.check_type(line=line, parameter=parameter, value=value, right_type=int)

    @staticmethod
    def check_float(line, parameter, value):
        return ParameterChecker.check_type(line=line, parameter=parameter, value=value, right_type=float)

    @staticmethod
    def check_string(line, parameter, value):
        return ParameterChecker.check_type(line=line, parameter=parameter, value=value, right_type=str)

    @staticmethod
    def check_positive(line, parameter, value):
        if value <= 0:
            return error.ErrorParameterNonPositive(line, parameter, value)
        return None

    @staticmethod
    def check_non_negative(line, parameter, value):
        if value < 0:
            return error.ErrorParameterNegative(line, parameter, value)
        return None

    @staticmethod
    def check_positive_int(line, parameter, value):
        check_first = ParameterChecker.check_int(line, parameter, value)
        if check_first is not None:
            return check_first
        else:
            return ParameterChecker.check_positive(line, parameter, value)

    @staticmethod
    def check_positive_float(line, parameter, value):
        check_first = ParameterChecker.check_float(line, parameter, value)
        if check_first is not None:
            return check_first
        else:
            return ParameterChecker.check_positive(line, parameter, value)

    @staticmethod
    def check_non_negative_int(line, parameter, value):
        check_first = ParameterChecker.check_int(line, parameter, value)
        if check_first is not None:
            return check_first
        else:
            return ParameterChecker.check_non_negative(line, parameter, value)

    @staticmethod
    def check_non_negative_float(line, parameter, value):
        check_first = ParameterChecker.check_float(line, parameter, value)
        if check_first is not None:
            return check_first
        else:
            return ParameterChecker.check_non_negative(line, parameter, value)

    # now, the implantation of printing list is converting to string directly.
    @staticmethod
    def check_selection(line, parameter, value):
        if value in parameters_selections[parameter]:
            return None
        else:
            return error.ErrorNotCandidate(line, parameter, value, str(parameters_selections[parameter]))

    # use check_selection
    @staticmethod
    def check_on_off(line, parameter, value):
        if value in parameters_selections['on_off']:
            return None
        else:
            return error.ErrorNotCandidate(line, parameter, value, str(parameters_selections['on_off']))

    def return_parameters(self):
        return list(self.parameter_checkers.keys())


def unknown_parameter(line, parameter, value):
    return error.WarnUnknownParameter(line, parameter, value)


# the first edition: without class
# # use a dictionary to select the check criterion of the values.
# def check_valid(parameter, value):
#     return parameter_checkers[parameter](parameter, value)


# @TODO grey or gray?
scatter_parameter_selections = {
    'mark_color': [
        'red', 'black', 'white', 'blue', 'yellow', 'green', 'grey',
    ],
    'scatter_mode': [
        'normal',
    ],
    'mark_shape': [
        'circle', 'cross',
    ]
}


class ScatterParameterChecker(ParameterChecker):
    def __init__(self):
        ParameterChecker.__init__(self)

    def initialize(self):
        self.parameter_checkers = {
            'scatter_bin': ParameterChecker.check_int,
            'mark_alpha': ParameterChecker.check_non_negative_int,
            'mark_size': ParameterChecker.check_positive_int,
            'scatter_mode': ScatterParameterChecker.check_selection,
            'mark_color': ScatterParameterChecker.check_selection,
            'mark_shape': ScatterParameterChecker.check_selection,
        }

    @staticmethod
    def check_selection(line, parameter, value):
        if value in scatter_parameter_selections[parameter]:
            return None
        else:
            return error.ErrorNotCandidate(line, parameter, value, str(scatter_parameter_selections[parameter]))
