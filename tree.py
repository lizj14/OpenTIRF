# -----------------------------------
# tree.py
# this class is the node of abstract syntax tree.
# See: the script part of the program is the imitation of the program of compiler class in Tsinghua, Department of
# Computer Science.
# -----------------------------------

# the node of the entire structure
PROGRAM = 0

# I decide not to cancel the set_stmt
# the node of a set procedure of a parameter
SET_STMT = PROGRAM + 1

# the node of the reading picture
READ_PICTURE = SET_STMT + 1

# the node of the parameter statement(one statement for the set list)
PARAMETER = READ_PICTURE + 1

# the node of reading graph
READ_GRAPH = PARAMETER + 1

# the node of file_path from which the program read data.
FILE_PATH = READ_GRAPH + 1

# the node of the literal
LITERAL = FILE_PATH + 1

# the node of the file path to which the program write result
OUT_PATH = LITERAL + 1

# the node of the fit process
FIT = OUT_PATH + 1

# the node of the read_molecule structure
READ_MOLECULE = FIT + 1

# the node of the definition of scatter mode
SCATTER = READ_MOLECULE + 1

# the node of the mark structure.
MARK = SCATTER + 1

# the node of writing molecules
WRITE_MOLECULE = MARK + 1

# the node of an object
DATA_OBJECT = WRITE_MOLECULE + 1

# the node of a new object
NEW_OBJECT = DATA_OBJECT + 1

POLYGON = NEW_OBJECT + 1

TIME_LINE = POLYGON + 1

DISTRICT_ANALYZE = TIME_LINE + 1

CIRCLE = DISTRICT_ANALYZE + 1

FILTER = CIRCLE + 1

CORRELATION = FILTER + 1

MERGE = CORRELATION + 1


MARK_SUB = MERGE + 1


# a number that is surely bigger than the frames of the picture.
# VERY_BIG = 1000000


# the abstract class of all node in the abstract syntax tree
# parameter @tag, int; the tag of the node. no use now, but may be useful in the future.
# parameter @line, int: the no of line in the program.
# parameter @handler, class Tree: the object to resolve the search of parameters.
# I think that it is not necessary to add lexpos, because the grammer of the script is not so complicated.
class Tree:
    def __init__(self, tag, line):
        self.tag = tag
        self.line_no = line
        self.handler = None

    # the visitor mode to use.
    # @visitor: the visitor object to use.
    def accept(self, visitor):
        visitor.visitTree(self)

    # return the line no of node
    def line(self):
        return self.line_no

    # the function of finding the value of parameter through the handler link.
    def handle_parameter(self, parameter):
        if self.handler is None:
            return None
        else:
            return self.handler.handle_parameter(parameter)

    # the path is somewhat different.
    # @path, string: the path of string input into the script, need adding the prefix part of the path.
    def handle_input_path(self, path):
        if self.handler is None:
            return path
        else:
            search_path = self.handler.handle_parameter('input_file_path')
            if search_path is None:
                return path
            else:
                return '%s%s' % (search_path, path)

    def handle_output_path(self, path):
        if self.handler is None:
            return path
        else:
            search_path = self.handler.handle_parameter('output_file_path')
            if search_path is None:
                return path
            else:
                return '%s%s' % (search_path, path)

    # the first edition: the line number and the throw of Error is here.
    # def handle_parameter(self, line, parameter):
    #     self.handler.handle_parameter(line, parameter)
    #     if self.handler is None:

    # use to set the handler link.
    def set_handler(self, handler):
        self.handler = handler


# Up to now, I think it is no use setting expr, because the script will not need calculating.
# class Expr(Tree):
#     def __init__(self, tag):
#         Tree.__init__(self, tag)
#         self.value = None
#         self.type = None


# the node of the whole program.
# @self.stmt_list: list of statement. the statement that the program is ordered to do.
class Program(Tree):
    def __init__(self, line, stmt_list):
        Tree.__init__(self, PROGRAM, line)
        self.stmt_list = stmt_list

    def accept(self, visitor):
        visitor.visitProgram(self)


# class Parameter(Tree):
#     def __init__(self, parameter_name):
#         Tree.__init__(self, PARAMETER)
#         self.parameter_name = parameter_name
#
#     def accept(self, visitor):
#         visitor.visitParameter(self)

# the node of order: read_picture.
# @self.picture_object, class newObject: the object referred to the picture read here, which can be used later
# in the other part of the program
# planned to set in a symbol table.
# @self.file_path, FilePath node: the file path of the picture.
class ReadPicture(Tree):
    def __init__(self, line, picture_object, file_path):
        Tree.__init__(self, READ_PICTURE, line)
        self.picture_object = picture_object
        self.file_path = file_path

    def accept(self, visitor):
        visitor.visitReadPicture(self)


# the node of order: read_graph. with a looping structure inside it.
# @self.file_path, FilePath node: the file_path of the data file.
# @self.stmt_list, list of the nodes of the statement: the orders of the graph.
# @self.mode, Literal node: the mode of parting the data. No such memory for calculating all at one time.
class ReadGraph(Tree):
    def __init__(self, line, file_path, stmt_list):
        Tree.__init__(self, READ_GRAPH, line)
        self.file_path = file_path
        self.stmt_list = stmt_list
        # self.mode = mode

    def accept(self, visitor):
        visitor.visitReadGraph(self)

    def handle_parameter(self, parameter):
        """
        when the parameter wanted is 'graph_file', the node will answer the request.
        the value of 'graph_file' considers the value of 'input_file_path' at exactly the node of ReadGraph, not Fit.
        :param parameter: string, the name of the parameter.
        :return: the value of the parameter.
        """
        if parameter == 'graph_file':
            return self.handle_input_path(self.file_path.file_path.value)
        else:
            return Tree.handle_parameter(self, parameter)


# the node of file_path. need to do the check of the file_path
# @file_path, Literal node: the string of file_path.
class FilePath(Tree):
    def __init__(self, line, file_path):
        Tree.__init__(self, FILE_PATH, line)
        self.file_path = file_path

    def accept(self, visitor):
        visitor.visitFilePath(self)


# the single statement in a setList
# @key, string: the name of the parameter to set;
# this is nearly only where name without object... but I think here string is enough.
# @value, literal: the value of the parameter
class ParaStmt(Tree):
    def __init__(self, line, parameter, value):
        Tree.__init__(self, PARAMETER, line)
        self.key = parameter
        self.value = value

    def accept(self, visitor):
        visitor.visitParaStmt(self)

    def form_key_value(self):
        return self.key, self.value.value


# the statement in a ScatterSetList, similar with ParaStmt
# no use now, but maybe useful in the future, if they need different analysis later.
class ScatterSetStmt(ParaStmt):
    def __init__(self, line, parameter, value):
        ParaStmt.__init__(self, line, parameter, value)

    def accept(self, visitor):
        visitor.visitScatterSetStmt(self)


# the whole statement of a set structure.
# @set_list, the list of ParaStmt node: the setList of the set structure
class SetStmt(Tree):
    def __init__(self, line, set_list):
        Tree.__init__(self, SET_STMT, line)
        self.set_list = set_list
        self.set_dictionary = {}

    def accept(self, visitor):
        visitor.visitSetStmt(self)

    def handle_parameter(self, parameter):
        searched = self.set_dictionary.get(parameter)
        if searched is None:
            if self.handler is not None:
                return self.handler.handle_parameter(parameter)
            else:
                return None
        else:
            # return self.set_dictionary[parameter]
            return searched


# the node of a literal
# @value, int or float or string: the value of the literal.
# attention: now, I have not defined the type of the literal. may set then.
# attention 2: the string is without ''
class Literal(Tree):
    def __init__(self, line, value):
        Tree.__init__(self, LITERAL, line)
        self.value = value
        self.type = None

    def accept(self, visitor):
        visitor.visitLiteral(self)

    # set_type means the expected type of the literal, not the exact type.
    # If the above two are different, then the program will throw error.
    def set_type(self, type_to_set):
        self.type = type_to_set


# the node of a dataObject.
# @name, string: the name of the object
# @type, int(consider using a dictionary): the type of the object. maybe no use in the following program.
class DataObject(Tree):
    def __init__(self, line, name):
        Tree.__init__(self, DATA_OBJECT, line)
        self.name = name
        self.type = None

    def accept(self, visitor):
        visitor.visitDataObject(self)

    # object_type, int: using dictionary
    def set_type(self, object_type):
        self.type = object_type


# the node of defining a new object
# @name, string: the name of an object
# @type, int(so as DataObject): given later. the type of the object.
class NewObject(Tree):
    def __init__(self, line, name):
        Tree.__init__(self, NEW_OBJECT, line)
        self.name = name
        self.type = None

    def accept(self, visitor):
        visitor.visitNewObject(self)

    def set_type(self, object_type):
        self.type = object_type


# the node of the fit structure
# @new_object, newObject node: the object to save the generated information of the fit process.
class Fit(Tree):
    def __init__(self, line, new_object,
                 start_x=None, start_y=None, end_x=None, end_y=None, start_frame=None, end_frame=None):
        Tree.__init__(self, FIT, line)
        self.new_object = new_object
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.start_frame = start_frame
        self.end_frame = end_frame

    def accept(self, visitor):
        visitor.visitFit(self)


class DistrictAnalyze(Tree):
    def __init__(self, line, data_object, graph_object, out_file, start_frame, end_frame):
        Tree.__init__(self, line=line, tag=DISTRICT_ANALYZE)
        self.data_object = data_object
        self.graph_object = graph_object
        self.out_file = out_file
        self.start_frame = start_frame
        self.end_frame = end_frame

    def accept(self, visitor):
        visitor.visitDistrictAnalyze(self)


class Filter(Tree):
    def __init__(self, line, data_object, new_object, graph_object=None, start_frame=None, end_frame=None):
        Tree.__init__(self, line=line, tag=FILTER)
        self.data_object = data_object
        self.new_object = new_object
        self.graph_object = graph_object
        self.start_frame = start_frame
        self.end_frame = end_frame

    def accept(self, visitor):
        visitor.visitFilter(self)


class Merge(Tree):
    def __init__(self, line, new_object, data_object_list, mode):
        Tree.__init__(self, line=line, tag=MERGE)
        self.new_object = new_object
        self.data_object_list = data_object_list
        self.mode = mode

    def accept(self, visitor):
        visitor.visitMerge(self)


class Correlation(Tree):
    def __init__(self, line, data_object_a, data_object_b, out_file):
        Tree.__init__(self, line=line, tag=CORRELATION)
        self.data_a = data_object_a
        self.data_b = data_object_b
        self.out_file = out_file

    def accept(self, visitor):
        visitor.visitCorrelation(self)


class TimeLine(Tree):
    """
    The node of time_line analyzing.
    """
    def __init__(self, line, data_object, out_path):
        Tree.__init__(self, tag=TIME_LINE, line=line)
        self.data_object = data_object
        self.out_path = out_path

    def accept(self, visitor):
        visitor.visitTimeLine(self)


class Polygon(Tree):
    """
    the node of the new polygon.
    """
    def __init__(self, line, new_object, point_list):
        Tree.__init__(self, tag=POLYGON, line=line)
        self.new_object = new_object
        self.point_list = point_list

    def accept(self, visitor):
        visitor.visitPolygon(self)


class Circle(Tree):
    """The node of new circle"""
    def __init__(self, line, new_object, center_x, center_y, radius):
        Tree.__init__(self, tag=CIRCLE, line=line)
        self.new_object = new_object
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def accept(self, visitor):
        visitor.visitCircle(self)


# the node of the scatter setting structure
# @new_object, newObject node: the generated object.
# @scatter_list, the list of ScatterSetStmt node: the parameters of the scatter.
class Scatter(Tree):
    def __init__(self, line, new_object, scatter_list):
        Tree.__init__(self, SCATTER, line)
        self.new_object = new_object
        self.scatter_list = scatter_list
        self.scatter_dictionary = {}

    def accept(self, visitor):
        visitor.visitScatter(self)

    def handle_parameter(self, parameter):
        searched = self.scatter_dictionary.get(parameter)
        if searched is None:
            if self.handler is None:
                return None
            else:
                return self.handler.handle_parameter(parameter=parameter)
        else:
            return searched


# the node of the mark structure
# @picture_object, dataObject node: the object of the background picture.
# @data_object, dataObject node: the object of the data of the molecules.
# @scatter_object, dataObject node: the object of the data of the scatter used.
# @out_file, OutFile node: the file to save the picture get.
# @start_frame, literal node: the frame from which the scatter begin.
# @end_frame, literal node: the frame to which the scatter end.
class Mark(Tree):
    def __init__(
            self, line, picture_object, out_file, mark_list, start_frame=None, end_frame=None, segment_frame=None):
        Tree.__init__(self, MARK, line)
        self.picture_object = picture_object
        self.out_file = out_file
        self.mark_list = mark_list
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.segment_frame = segment_frame

    def accept(self, visitor):
        visitor.visitMark(self)


class MarkSub(Tree):
    def __init__(self, line, data_object, scatter_object):
        Tree.__init__(self, MARK_SUB, line=line)
        self.data_object = data_object
        self.scatter_object = scatter_object

    def accept(self, visitor):
        visitor.visitMarkSub(self)


# the node of the writing molecule structure.
# @data_object, dataObject node: the data_object to write.
# @out_file, outFile node: the file to put the result in.
class WriteMolecule(Tree):
    def __init__(self, line, data_object, out_file):
        Tree.__init__(self, WRITE_MOLECULE, line)
        self.data_object = data_object
        self.out_file = out_file

    def accept(self, visitor):
        visitor.visitWriteMolecule(self)


# the node of the reading molecule structure.
# @new_object, newObject node: the object to save the information read from the file.
# @file_path, filePath node: the file path to read data from
class ReadMolecule(Tree):
    def __init__(self, line, new_object, file_path):
        Tree.__init__(self, READ_MOLECULE, line)
        self.new_object = new_object
        self.file_path = file_path

    def accept(self, visitor):
        visitor.visitReadMolecule(self)


# the node of the outFile
# @out_file, literal node: the file path of the output file.
class OutFile(Tree):
    def __init__(self, line, out_file):
        Tree.__init__(self, OUT_PATH, line)
        self.out_file = out_file

    def accept(self, visitor):
        visitor.visitOutFile(self)


# Absolutely an abstract object, with no implementation
class Visitor:
    def __init__(self):
        pass

    def visitProgram(self, program):
        pass

    def visitReadPicture(self, read_picture):
        pass

    def visitReadGraph(self, read_graph):
        pass

    def visitFilePath(self, file_path):
        pass

    def visitSetStmt(self, set_stmt):
        pass

    def visitParaStmt(self, para_stmt):
        pass

    def visitLiteral(self, literal):
        pass

    def visitFit(self, fit):
        pass

    def visitMark(self, mark):
        pass

    def visitScatter(self, scatter):
        pass

    def visitWriteMolecule(self, write_molecule):
        pass

    def visitReadMolecule(self, read_molecule):
        pass

    def visitDataObject(self, data_object):
        pass

    def visitNewObject(self, new_object):
        pass

    def visitOutFile(self, out_file):
        pass

    def visitScatterSetStmt(self, scatter_set_stmt):
        pass

    def visitPolygon(self, polygon):
        pass

    def visitTimeLine(self, time_line):
        pass

    def visitCircle(self, circle):
        pass

    def visitDistrictAnalyze(self, district_analyze):
        pass

    def visitFilter(self, filter_object):
        pass

    def visitCorrelation(self, correlation):
        pass

    def visitMerge(self, merge):
        pass

    def visitMarkSub(self, mark_sub):
        pass
