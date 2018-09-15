# ---------------------------------------------
# printer.py
# the class to print result, in order to control the indentation
# ---------------------------------------------
import tree
import io


class Printer:
    # UNIT is the steps moving each time.
    # it works as a static variable.
    UNIT = 2

    def __init__(self):
        self.blank = 0

    # decrease the indentation.
    def decrease(self):
        self.blank -= self.UNIT

    # increase the indentation.
    def increase(self):
        self.blank += self.UNIT

    # print the string.
    def print(self, to_print):
        print('%s%s' % (' ' * self.blank, str(to_print)))

    def next_line(self):
        self.print('\n')

    # print a dictionary, usually for the setting list.with type check
    def print_dict(self, dict_to_print):
        if not type(dict_to_print) == dict:
            print('not a dict')
            return
        for (key, value) in dict_to_print:
            self.print('%s %s' % (key, value))

    # print a list with type check.
    def print_list(self, list_to_print):
        if not type(list_to_print) == list:
            print('not a list')
            return
        for value in list_to_print:
            self.print(value)

    def print_string(self, string_to_print):
        self.print('\'%s\'' % string_to_print)


# write to a file(txt)
class FilePrinter(Printer):
    def __init__(self, file):
        Printer.__init__(self)
        self.print_to = file

    def print(self, to_print):
        # self.print_to.write('%s%s' % (' ' * self.blank, to_print))
        self.print_to.write('%s%s\n' % (' '*self.blank, to_print))


class PrinterFactory:
    # def __init__(self):
    #     pass
    #
    # factory_ = None
    #
    # # @staticmethod
    # # def printer_factory():
    # #     if printer_ is None:
    #
    # @class method
    # def printer_factory(cls):
    #     if cls.factory_ is None:
    #         cls.factory_ = PrinterFactory()
    #     return cls.factory_
    #
    # def make_printer(self, print_to = None):
    #     if print_to is None:
    #         return

    @classmethod
    def return_printer(cls, print_to=None):
        if print_to is None:
            return Printer()
        elif type(print_to) == io.TextIOWrapper:
            return FilePrinter(print_to)


# the visitor to solve the nodes in the tree while printing the tree.
# there is a printer inside the Writer Class to control the indentation of the program.
class WriteVisitor(tree.Visitor):
    def __init__(self, writer=None):
        tree.Visitor.__init__(self)
        self.printer = PrinterFactory.return_printer(writer)

    def visitProgram(self, program):
        # use the visitor to solve the statements in the list.
        for statement in program.stmt_list:
            statement.accept(self)
        self.printer.print('end')
        # self.printer.decrease()

    # the mode has been removed from read_graph structure
    def visitReadGraph(self, read_graph):
        self.printer.print('read_graph')
        self.printer.increase()
        # read_graph.mode.accept(self)
        read_graph.file_path.accept(self)
        # self.printer.print(read_graph.mode)
        for statement in read_graph.stmt_list:
            statement.accept(self)
        self.printer.print('end')
        self.printer.decrease()

    def visitFilePath(self, file_path):
        # self.printer.print('file_path')
        # self.printer.increase()
        # self.printer.print(file_path.file_path)
        file_path.file_path.accept(self)
        # self.printer.decrease()

    def visitReadPicture(self, read_picture):
        self.printer.print('read_picture')
        self.printer.increase()
        # self.printer.print(read_picture.file_name)
        read_picture.picture_object.accept(self)
        read_picture.file_path.accept(self)
        self.printer.decrease()

    def visitSetStmt(self, set_stmt):
        self.printer.print('set')
        self.printer.increase()
        for para in set_stmt.set_list:
            para.accept(self)
        self.printer.print('end')
        self.printer.decrease()

    def visitParaStmt(self, para_stmt):
        self.printer.print('%s' % para_stmt.key)
        self.printer.increase()
        para_stmt.value.accept(self)
        self.printer.decrease()

    def visitLiteral(self, literal):
        if type(literal.value) == int:
            self.printer.print('%d' % literal.value)
        elif type(literal.value) == float:
            self.printer.print('%f' % literal.value)
        else:
            self.printer.print_string(literal.value)

    def visitDataObject(self, data_object):
        self.printer.print(data_object.name)

    def visitNewObject(self, new_object):
        self.printer.print(new_object.name)

    def visitFit(self, fit):
        self.printer.print('fit')
        self.printer.increase()
        fit.new_object.accept(self)
        if fit.start_x is not None:
            fit.start_x.accept(self)
            fit.start_y.accept(self)
            fit.end_x.accept(self)
            fit.end_y.accept(self)
        if fit.start_frame is not None:
            fit.start_frame.accept(self)
            fit.end_frame.accept(self)
        self.printer.decrease()

    def visitMark(self, mark):
        self.printer.print('mark')
        self.printer.increase()
        mark.picture_object.accept(self)
        # mark.data_object.accept(self)
        # mark.scatter_object.accept(self)
        mark.out_file.accept(self)
        if mark.start_frame is not None:
            mark.start_frame.accept(self)
        if mark.end_frame is not None:
            mark.end_frame.accept(self)
        if mark.segment_frame is not None:
            mark.segment_frame.accept(self)
        for mark_sub in mark.mark_list:
            mark_sub.accept(self)
        self.printer.decrease()

    def visitMarkSub(self, mark_sub):
        mark_sub.data_object.accept(self)
        self.printer.increase()
        mark_sub.scatter_object.accept(self)
        # for node in [mark_sub.start_frame, mark_sub.end_frame, mark_sub.segment_frame]:
        #     if node is not None:
        #         node.accept(self)
        self.printer.decrease()

    def visitScatter(self, scatter):
        self.printer.print('scatter')
        self.printer.increase()
        scatter.new_object.accept(self)
        for scatter_set in scatter.scatter_list:
            scatter_set.accept(self)
        self.printer.print('end')
        self.printer.decrease()

    def visitWriteMolecule(self, write_molecule):
        self.printer.print('write_molecule')
        self.printer.increase()
        write_molecule.data_object.accept(self)
        write_molecule.out_file.accept(self)
        self.printer.decrease()

    def visitOutFile(self, out_file):
        out_file.out_file.accept(self)

    def visitReadMolecule(self, read_molecule):
        self.printer.print('read_molecule')
        self.printer.increase()
        read_molecule.new_object.accept(self)
        read_molecule.file_path.accept(self)
        self.printer.decrease()

    # the solution now: call the visit of paraStmt.
    def visitScatterSetStmt(self, scatter_set_stmt):
        self.visitParaStmt(scatter_set_stmt)

    def visitTimeLine(self, time_line):
        self.printer.print('time_line')
        self.printer.increase()
        time_line.data_object.accept(self)
        time_line.out_path.accept(self)
        self.printer.decrease()

    def visitPolygon(self, polygon):
        self.printer.print('polygon')
        self.printer.increase()
        for point in polygon.point_list:
            point[0].accept(self)
            point[1].accept(self)
        self.printer.decrease()

    def visitCircle(self, circle):
        self.printer.print('circle')
        self.printer.increase()
        circle.new_object.accept(self)
        circle.center_x.accept(self)
        circle.center_y.accept(self)
        circle.radius.accept(self)
        self.printer.decrease()

    def visitDistrictAnalyze(self, district_analyze):
        self.printer.print('district_analyze')
        self.printer.increase()
        district_analyze.data_object.accept(self)
        district_analyze.graph_object.accept(self)
        district_analyze.out_file.accept(self)
        district_analyze.start_frame.accept(self)
        district_analyze.end_frame.accept(self)
        self.printer.decrease()

    def visitCorrelation(self, correlation):
        self.printer.print('correlation')
        self.printer.increase()
        correlation.data_a.accept(self)
        correlation.data_b.accept(self)
        correlation.ouf_file.accept(self)
        self.printer.decrease()

    def visitFilter(self, filter_object):
        self.printer.print('filter')
        self.printer.increase()
        filter_object.data_object.accept(self)
        filter_object.new_object.accept(self)
        if filter_object.graph_object is not None:
            filter_object.graph_object.accept(self)
        if filter_object.start_frame is not None:
            filter_object.start_frame.accept(self)
            filter_object.end_frame.accept(self)

    def visitMerge(self, merge):
        self.printer.print('merge')
        self.printer.increase()
        merge.new_object.accept(self)
        for data_object in merge.data_object_list:
            data_object.accept(self)
        self.printer.decrease()
