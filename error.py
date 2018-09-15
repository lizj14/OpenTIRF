# ---------------------------------------------
# error.py
# the class to represent the error and warn searched in the script
# ---------------------------------------------


# the base class of the error and warn.
class ScriptException:
    def __init__(self, line):
        self.line = line

    def to_string(self):
        pass

    # use to judge if it is an error.
    @staticmethod
    def is_error():
        return False

    @staticmethod
    def is_warn():
        return False

    # use for the sort of warns and errors: use the line.
    def __lt__(self, other):
        return self.line < other.line


# the abstract class of errors.
class Error(ScriptException):
    def __init__(self, line):
        ScriptException.__init__(self, line)

    @staticmethod
    def is_error():
        return True

    # overridden in the subclass of error
    def error_info(self):
        pass

    def to_string(self):
        return 'error: %d, %s' % (self.line, self.error_info())


# the abstract class of warns.
class Warn(ScriptException):
    def __init__(self, line):
        ScriptException.__init__(self, line)

    @staticmethod
    def is_warn():
        return True

    # the same as error_info()
    def warn_info(self):
        pass

    def to_string(self):
        return 'warn:  %d, %s' % (self.line, self.warn_info())


# --------------------------------------------
# Following are the specific errors and warns.
# --------------------------------------------

# the name of the parameter in script is unknown.
# the script can still run, but the program is suspicious to be wrong.
class WarnUnknownParameter(Warn):
    def __init__(self, line, parameter_name, value):
        Warn.__init__(self, line)
        self.parameter_name = parameter_name
        self.value = value

    def warn_info(self):
        return 'parameter named \'%s\' valued %s is unknown.' % (self.parameter_name, self.value)


# the type of literal cannot match the parameter
class ErrorInvalidType(Error):
    def __init__(self, line, parameter_name, wrong_type, right_type):
        Error.__init__(self, line)
        self.parameter_name = parameter_name
        self.wrong_type = wrong_type
        self.right_type = right_type

    def error_info(self):
        return 'the value of parameter \'%s\' should be %s, but %s given.' % (
            self.parameter_name, self.right_type, self.wrong_type)


# the type of object cannot match the object
# @type, string: all string.
class ErrorObjectInvalidType(Error):
    def __init__(self, line, object_name, wrong_type, right_type):
        Error.__init__(self, line)
        self.object_name = object_name
        self.wrong_type = wrong_type
        self.right_type = right_type

    def error_info(self):
        return 'the object of \'%s\' should be %s, but %s given.' \
               % (self.object_name, self.right_type, self.wrong_type)


class ErrorLiteralInvalidType(Error):
    def __init__(self, line, literal_val, wrong_type, right_type):
        Error.__init__(self, line)
        self.literal_val = literal_val
        self.wrong_type = wrong_type
        self.right_type = right_type

    def error_info(self):
        return 'the literal \'%s\' should be %s, but %s given.' % (
            self.literal_val, self.right_type, self.wrong_type)


# the object need mentioning before used. Or there will be no data in it.
class ErrorObjectNotMentioned(Error):
    def __init__(self, line, object_name):
        Error.__init__(self, line)
        self.object_name = object_name

    def error_info(self):
        return 'object \'%s\' is used without declaring before.' % self.object_name


# the name given to an object is reserved
# this is not meaningful, because it will name object using a string reserved will generate many error in syntax.
# and it will hardly handled by this error.
class ErrorNameReserved(Error):
    def __init__(self, line, object_name):
        Error.__init__(self, line)
        self.object_name = object_name

    def error_info(self):
        return 'name \'%s\' is reserved, can not given to an object.' % self.object_name


# the name given to an object is used before.
class ErrorNameReused(Error):
    def __init__(self, line, object_name):
        Error.__init__(self, line)
        self.object_name = object_name

    def error_info(self):
        return 'name \'%s\' has been used in the script before.' % self.object_name


# the file does not exist,
class ErrorFileNotFound(Error):
    def __init__(self, line, file_path):
        Error.__init__(self, line)
        self.file_path = file_path

    def error_info(self):
        return 'cannot find the file: %s' % self.file_path


# the file has existed, the data will be overridden.
class WarnFileOverridden(Warn):
    def __init__(self, line, file_path):
        Warn.__init__(self, line)
        self.file_path = file_path

    def warn_info(self):
        return 'the file has existed, and will be overridden: %s' % self.file_path


# the file path to write has been used more than one time in the script.
class ErrorFileWritenTwice(Error):
    def __init__(self, line, file_path):
        Error.__init__(self, line)
        self.file_path = file_path

    def error_info(self):
        return 'the file path is used to write into more than one time in the script: %s' % self.file_path


# the parameter need in the function is not found before.
class ErrorParameterNeed(Error):
    def __init__(self, line, parameter_name, function_name):
        Error.__init__(self, line)
        self.parameter_name = parameter_name
        self.function_name = function_name

    def error_info(self):
        return 'function %s need parameter %s before.' % (self.function_name, self.parameter_name)


# the fit function need to be in the read_graph structure.
class ErrorFitOutside(Error):
    def __init__(self, line):
        Error.__init__(self, line)

    def error_info(self):
        return 'fit function need to be in the read_graph structure.'


# the read_graph function should not be in the read_graph structure.
class ErrorReadGraphInside(Error):
    def __init__(self, line):
        Error.__init__(self, line)

    def error_info(self):
        return 'the read_graph function can\'t be in the read_graph structure.'


# the length of the segment while marking should not be minus.
class ErrorParameterNonPositive(Error):
    def __init__(self, line, parameter_name, value):
        Error.__init__(self, line)
        self.parameter_name = parameter_name
        self.value = value

    def error_info(self):
        return 'the parameter \'%s\' should be positive, but now : %s' \
               % (self.parameter_name, self.value)


# the length of the segment while marking should not be minus.
class ErrorParameterNegative(Error):
    def __init__(self, line, parameter_name, value):
        Error.__init__(self, line)
        self.parameter_name = parameter_name
        self.value = value

    def error_info(self):
        return 'the parameter \'%s\' should not be negative, but now : %s' % (self.parameter_name, self.value)


# the value of the parameter is not the candidate
class ErrorNotCandidate(Error):
    def __init__(self, line, parameter_name, value, candidates):
        Error.__init__(self, line)
        self.parameter_name = parameter_name
        self.value = value
        self.candidates = candidates

    def error_info(self):
        return 'the value of parameter \'%s\': %s is not candidate of %s'\
               % (self.parameter_name, self.value, str(self.candidates))


# there are logical relationship between some parameters, so one should not bigger than the other.
# @parameter_small: the name of the parameter that should be small.
# @real_value_small: the value of the parameter that should be small, which is large.
class WarnSizeRelationship(Warn):
    def __init__(self, line, parameter_small, parameter_large, real_value_small, real_value_large):
        Warn.__init__(self, line)
        self.parameter_small = parameter_small
        self.parameter_large = parameter_large
        self.real_value_small = real_value_small
        self.real_value_large = real_value_large

    def warn_info(self):
        return 'the value of parameter \'%s\' should be smaller than parameter \'%s\', but now %s >= %s' % (
            self.parameter_small, self.parameter_large, self.real_value_small, self.real_value_large
        )


# if the script does not provide the path of script file, it will use default file path.
# @script_path, string: with file path
class WarnDefaultScriptPath(Warn):
    def __init__(self, line, script_path):
        Warn.__init__(self, line)
        self.script_path = script_path

    def warn_info(self):
        return 'the script has not provide the file path to write the script file, it will use default :%s'\
               % self.script_path


class WarnEmptyMerge(Warn):
    def __init__(self, line):
        Warn.__init__(self, line)

    def warn_info(self):
        return 'merge no data will generate an empty molecule list, which is meaningless in most situations.'
