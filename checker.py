# ---------------------------------------------
# checker.py
# the class to check before run the program.
# ---------------------------------------------
import tree
import symbol
import parameter
import error
import os


# class used to check the script before executing.
# @self.in_read_graph: if the script is in read_graph structure, where the statement can use is different.
# @type_define_, int: the number of the type to define.
class Checker(tree.Visitor):
    def __init__(self):
        tree.Visitor.__init__(self)
        self.in_read_graph_ = []
        self.type_define_ = None
        self.table = symbol.table_instance()
        self.errors = []
        self.warns = []
        self.out_file_name = set({})
        self.parameter_checker = parameter.ParameterChecker()
        # @TODO:I think it's better to use it in __init__(),
        # but there is problem to do with inheritance system
        self.parameter_checker.initialize()
        self.scatter_parameter_checker = parameter.ScatterParameterChecker()
        self.scatter_parameter_checker.initialize()
        # set the reserved names of parameters and scatter parameters.
        self.table.read_reserve(
            self.parameter_checker.return_parameters() + self.scatter_parameter_checker.return_parameters())

    def in_read_graph(self):
        return len(self.in_read_graph_) != 0

    # show the errors and warns after type check.
    # return True: the program can continue.
    # return False: there is error inside program, and the program should be ended.
    def show_errors(self):
        exceptions = self.errors + self.warns
        sorted(exceptions)
        for exception in exceptions:
            print(exception.to_string())
        print('error: %d; warn: %d.' % (len(self.errors), len(self.warns)))
        if len(self.errors):
            return False
        elif len(self.warns):
            ok = input('there is warn in script.\ninput Y to continue or N to stop.')
            if ok == 'N':
                return False
        return True

    def visitProgram(self, program):
        for statement in program.stmt_list:
            statement.accept(self)
        if len(program.stmt_list) > 0:
            if not self.check_parameter(program.stmt_list[len(program.stmt_list) - 1], 'script_path'):
                whole_path = program.stmt_list[len(program.stmt_list) - 1].handle_output_path('script.txt')
                # self.errors.append(error.WarnDefaultScriptPath(0, whole_path))
                self.add_error(error.WarnDefaultScriptPath(0, whole_path))

    def add_error(self, error_to_add):
        if error_to_add.is_error():
            # print('add error!')
            self.errors.append(error_to_add)
        elif error_to_add.is_warn():
            # print('add warn!')
            self.warns.append(error_to_add)

    # def add_warn(self, warn_to_add):
    #     self.warns.append(warn_to_add)

    # change to use int directly.
    def type_define(self, type_no):
        # self.type_define_ = symbol.dataType[type_name]
        self.type_define_ = type_no

    def type_demand(self):
        return self.type_define_

    # data_object, class DataObject: the data_object to judge the type.
    # true_type, int: the number of the type of the symbol needed.
    def check_type(self, data_object, true_type):
        if data_object.type == true_type:
            return
        else:
            # @TODO: Is it necessary? I am still considering.
            # data_object.type = symbol.dataType['wrong_type']
            self.add_error(error.ErrorObjectInvalidType(
                data_object.line(), data_object.name,
                symbol.symbol_string[data_object.type], symbol.symbol_string[true_type]))

    # the program is able to hold multi-layer nested structure,(pay attention to the stack structure)
    #  but in the using of the program, there should not be.
    def visitReadGraph(self, read_graph):
        if self.in_read_graph():
            self.add_error(error.ErrorReadGraphInside(read_graph.line()))
            return
        self.in_read_graph_.append(read_graph.line())
        read_graph.file_path.accept(self)
        for statement in read_graph.stmt_list:
            statement.accept(self)
        self.in_read_graph_.pop()

    # the type_define technology is not being used now.
    def visitReadPicture(self, read_picture):
        # self.type_define(symbol.dataType['s_picture'])
        read_picture.picture_object.set_type(symbol.dataType['s_picture'])
        read_picture.picture_object.accept(self)
        read_picture.file_path.accept(self)

    def visitFilePath(self, file_path):
        file_path.file_path.set_type(str)
        file_path.file_path.accept(self)
        whole_path = file_path.handle_input_path(file_path.file_path.value)
        if not os.path.exists(whole_path):
            self.add_error(error.ErrorFileNotFound(file_path.line(), whole_path))

    def visitOutFile(self, out_file):
        out_file.out_file.set_type(str)
        out_file.out_file.accept(self)
        whole_path = out_file.handle_output_path(out_file.out_file.value)
        if os.path.exists(whole_path):
            self.add_error(error.WarnFileOverridden(out_file.line(), whole_path))
        # check if the output path has been used in the script.
        # if True, the file will be written into twice in one script executing.
        if whole_path in self.out_file_name:
            self.add_error(error.ErrorFileWritenTwice(out_file.line(), whole_path))
        else:
            self.out_file_name.add(whole_path)

    def visitParaStmt(self, para_stmt):
        # key is only a string, no accept function.
        para_stmt.value.accept(self)
        # attention: para_stmt.value is a Literal object, not the value of Literal!
        # if no error, check is None; else, check is the error itself.
        check = self.parameter_checker.check_valid(para_stmt.line(), para_stmt.key, para_stmt.value.value)
        if check is not None:
            self.add_error(check)

    def visitScatterSetStmt(self, scatter_set_stmt):
        scatter_set_stmt.value.accept(self)
        check = self.scatter_parameter_checker.check_valid(
            scatter_set_stmt.line(), scatter_set_stmt.key, scatter_set_stmt.value.value)
        # I think thank that it means None...Anyway, I cannot remember where NameError from/
        if check is not NameError and check is not None:
            self.add_error(check)

    def visitSetStmt(self, set_stmt):
        for statement in set_stmt.set_list:
            statement.accept(self)
            set_stmt.set_dictionary[statement.key] = statement.value.value

    # there seems to be nothing to do...
    def visitLiteral(self, literal):
        if literal.type is None:
            return
        else:
            # if literal.type != type(literal.value):
            if not isinstance(literal.value, literal.type):
                self.add_error(
                    error.ErrorLiteralInvalidType(literal.line(), literal.value, type(literal.value), literal.type))

    def visitDataObject(self, data_object):
        symbol_search = self.table.search_symbol(data_object.name)
        if symbol_search is None:
            self.add_error(error.ErrorObjectNotMentioned(data_object.line(), data_object.name))
            data_object.set_type(symbol.dataType['wrong_type'])
        # else:
        #     data_object.set_type(symbol_search.return_type())
        elif symbol_search.return_type() != data_object.type:
            self.add_error(
                error.ErrorObjectInvalidType(
                    line=data_object.line(), object_name=data_object.name,
                    wrong_type=symbol.symbol_string[symbol_search.return_type()],
                    right_type=symbol.symbol_string[data_object.type]))

    # before called, the new_object.type has been defined.
    def visitNewObject(self, new_object):
        symbol_search = self.table.search_symbol(new_object.name)
        # the situation that the symbol has existed.
        if symbol_search is not None:
            if symbol_search.is_reserved():
                self.add_error(error.ErrorNameReserved(new_object.line(), new_object.name))
            else:
                self.add_error(error.ErrorNameReused(new_object.line(), new_object.name))
        else:
            self.table.create_symbol(new_object.name, new_object.type)

    def visitFit(self, fit):
        # check if the fit statement is in the read_graph structure.
        # print('check fit')
        if not self.in_read_graph():
            self.add_error(error.ErrorFitOutside(fit.line()))
            return
        # check when only part of the data is to be fit.
        if fit.start_x is not None:
            for literal in [fit.start_x, fit.start_y, fit.end_x, fit.end_y]:
                literal.set_type(int)
                literal.accept(self)
            if type(fit.start_x.value) is int and type(fit.end_x.value) is int:
                if fit.start_x.value >= fit.end_x.value:
                    self.add_error(error.WarnSizeRelationship(
                        line=fit.line(), parameter_small='start_x', real_value_small=fit.start_x.value,
                        parameter_large='end_x', real_value_large=fit.end_x.value))
            if type(fit.start_y.value) is int and type(fit.end_y.value) is int:
                if fit.start_y.value >= fit.end_y.value:
                    self.add_error(error.WarnSizeRelationship(
                        line=fit.line(), parameter_small='start_y', real_value_small=fit.start_y.value,
                        parameter_large='end_y', real_value_large=fit.end_y.value
                    ))
        if fit.start_frame is not None:
            for literal in [fit.start_frame, fit.end_frame]:
                literal.set_type(int)
                literal.accept(self)
            if type(fit.start_frame.value) is int and type(fit.end_frame.value) is int:
                if fit.start_frame.value >= fit.end_frame.value:
                    self.add_error(error.WarnSizeRelationship(
                        line=fit.line(), parameter_small='start_frame', real_value_small=fit.start_frame.value,
                        parameter_large='end_frame', real_value_large=fit.end_frame.value
                    ))

        # check if the parameter has been defined.
        for parameter_to_check in parameter.parameters_used['fit']:
            if not self.check_parameter(fit, parameter_to_check):
                self.add_error(error.ErrorParameterNeed(fit.line(), parameter_to_check, 'fit'))
        fit.new_object.set_type(symbol.dataType['s_data_molecule'])
        fit.new_object.accept(self)

    def visitDistrictAnalyze(self, district_analyze):
        district_analyze.data_object.set_type(symbol.dataType['s_data_molecule'])
        district_analyze.data_object.accept(self)
        district_analyze.graph_object.set_type(symbol.dataType['s_area'])
        district_analyze.graph_object.accept(self)
        district_analyze.out_file.accept(self)
        district_analyze.start_frame.set_type(int)
        district_analyze.start_frame.accept(self)
        district_analyze.end_frame.set_type(int)
        district_analyze.end_frame.accept(self)
        if district_analyze.start_frame.value > district_analyze.end_frame.value:
            self.add_error(error.WarnSizeRelationship(
                line=district_analyze.line(), parameter_small='start_frame',
                real_value_small=district_analyze.start_frame.value,
                parameter_large='end_frame', real_value_large=district_analyze.end_frame.value))

    def visitCorrelation(self, correlation):
        correlation.data_a.set_type(symbol.dataType['s_data_molecule'])
        correlation.data_a.accept(self)
        correlation.data_b.set_type(symbol.dataType['s_data_molecule'])
        correlation.data_b.accept(self)
        correlation.out_file.accept(self)
        for parameter_to_check in parameter.parameters_used['correlation']:
            if not self.check_parameter(correlation, parameter_to_check):
                self.add_error(error.ErrorParameterNeed(correlation.line(), parameter_to_check, 'fit'))

    def visitTimeLine(self, time_line):
        # print('check time_line')
        if not self.in_read_graph():
            self.add_error(error.ErrorFitOutside(time_line.line()))
            return
        for parameter_to_check in parameter.parameters_used['time_line']:
            if not self.check_parameter(time_line, parameter_to_check=parameter_to_check):
                self.add_error(
                    error_to_add=error.ErrorParameterNeed(time_line.line(), parameter_to_check, 'time_line'))
        time_line.data_object.set_type(symbol.dataType['s_area'])
        time_line.data_object.accept(self)
        time_line.out_path.accept(self)

    def visitScatter(self, scatter):
        scatter.new_object.set_type(symbol.dataType['s_scatter'])
        scatter.new_object.accept(self)
        for scatter_parameter in scatter.scatter_list:
            scatter_parameter.accept(self)
            scatter.scatter_dictionary[scatter_parameter.key] = scatter_parameter.value.value
        for parameter_to_check in parameter.parameters_used['scatter']:
            if scatter.scatter_dictionary.get(parameter_to_check, None) is None:
                self.add_error(error.ErrorParameterNeed(scatter.line(), parameter_to_check, 'scatter'))

    def visitPolygon(self, polygon):
        polygon.new_object.set_type(symbol.dataType['s_area'])
        polygon.new_object.accept(self)
        for point in polygon.point_list:
            point[0].set_type(float)
            point[0].accept(self)
            point[1].set_type(float)
            point[1].accept(self)

    def visitCircle(self, circle):
        circle.new_object.set_type(symbol.dataType['s_area'])
        circle.new_object.accept(self)
        for number_literal in [circle.center_x, circle.center_y, circle.radius]:
            number_literal.set_type(float)
            number_literal.accept(self)

    def visitMark(self, mark):
        mark.picture_object.set_type(symbol.dataType['s_picture'])
        mark.picture_object.accept(self)
        # mark.data_object.set_type(symbol.dataType['s_data_molecule'])
        # mark.data_object.accept(self)
        # mark.scatter_object.set_type(symbol.dataType['s_scatter'])
        # mark.scatter_object.accept(self)
        mark.out_file.accept(self)
        for literal in [mark.start_frame, mark.end_frame, mark.segment_frame]:
            if literal is not None:
                literal.set_type(int)
                literal.accept(self)
        if mark.start_frame is not None and mark.end_frame is not None:
            if mark.start_frame.value > mark.end_frame.value:
                self.add_error(error.WarnSizeRelationship(
                    line=mark.line(), parameter_small='start_frame', real_value_small=mark.start_frame.value,
                    parameter_large='end_frame', real_value_large=mark.end_frame.value))

    def visitMarkSub(self, mark_sub):
        mark_sub.data_object.set_type(symbol.dataType['s_data_molecule'])
        mark_sub.data_object.accept(self)
        mark_sub.scatter_object.set_type(symbol.dataType['s_scatter'])
        mark_sub.scatter_object.accept(self)

    def visitFilter(self, filter_object):
        # print('visit filter')
        filter_object.data_object.set_type(symbol.dataType['s_data_molecule'])
        filter_object.data_object.set_type(symbol.dataType['s_data_molecule'])
        filter_object.data_object.accept(self)
        filter_object.new_object.set_type(symbol.dataType['s_data_molecule'])
        filter_object.new_object.accept(self)
        if filter_object.graph_object is not None:
            filter_object.graph_object.set_type(symbol.dataType['s_area'])
            filter_object.graph_object.accept(self)
        if filter_object.start_frame is not None:
            for literal in [filter_object.start_frame, filter_object.end_frame]:
                literal.set_type(int)
                literal.accept(self)
            if filter_object.start_frame.value > filter_object.end_frame.value:
                self.add_error(error.WarnSizeRelationship(
                    line=filter_object.line(),
                    parameter_small='start_frame', real_value_small=filter_object.start_frame.value,
                    parameter_large='end_frame', real_value_large=filter_object.end_frame.value,
                ))

    def visitMerge(self, merge):
        merge.new_object.set_type(symbol.dataType['s_data_molecule'])
        if len(merge.data_object_list) == 0:
            self.add_error(error_to_add=error.WarnEmptyMerge(line=merge.line()))
        else:
            for data_to_merge in merge.data_object_list:
                data_to_merge.set_type(symbol.dataType['s_data_molecule'])
                data_to_merge.accept(self)

    def visitWriteMolecule(self, write_molecule):
        write_molecule.data_object.set_type(symbol.dataType['s_data_molecule'])
        write_molecule.data_object.accept(self)
        write_molecule.out_file.accept(self)

    def visitReadMolecule(self, read_molecule):
        read_molecule.new_object.set_type(symbol.dataType['s_data_molecule'])
        read_molecule.new_object.accept(self)
        read_molecule.file_path.accept(self)

    # return False if the define of parameter cannot be found in the script.
    # @staticmethod
    def check_parameter(self, node, parameter_to_check):
        value = node.handle_parameter(parameter=parameter_to_check)
        if value is None:
            return False
        self.check_parameter_dependency(node=node, value=value, parameter_to_check=parameter_to_check)
        return True

    def check_parameter_dependency(self, node, value, parameter_to_check):
        if parameter.parameter_dependency.get(parameter_to_check) is not None and\
                        parameter.parameter_dependency[parameter_to_check].get(value) is not None:
            for parameter_need in parameter.parameter_dependency[parameter_to_check][value]:
                parameter_value = node.handle_parameter(parameter=parameter_need)
                if parameter_value is None:
                    self.add_error(error.ErrorParameterNeed(node.line(), parameter_need, parameter_to_check))
                else:
                    self.check_parameter_dependency(node=node, value=parameter_value, parameter_to_check=parameter_need)
