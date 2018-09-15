# ---------------------------------------------
# executor.py
# the class to execute the whole script.
# ---------------------------------------------
import tree
import re
import os
import visual
import parameter
import fit_analyzer
import data_analyzer
import data
import graph
import csv
import printer


class Executor(tree.Visitor):
    def __init__(self, table, print_engine):
        tree.Visitor.__init__(self)
        self.table = table
        self.printer = print_engine

    def visitProgram(self, program):
        for statement in program.stmt_list:
            statement.accept(self)

    def visitReadGraph(self, read_graph):
        for statement in read_graph.stmt_list:
            statement.accept(self)

    def visitReadPicture(self, read_picture):
        read_picture.picture_object.accept(self)
        read_picture.file_path.accept(self)
        symbol_search = self.table.search_symbol(read_picture.picture_object.name)
        symbol_search.link_to_data(
            data=visual.Picture(file_path=read_picture.handle_input_path(path=read_picture.file_path.file_path.value)))

    def visitFilePath(self, file_path):
        pass

    def visitOutFile(self, out_file):
        """
        it the path does not exist, then use mkdir to make the path.
        :param out_file:
        :return:
        """
        # match_result = re.match(
        #     pattern=r'([a-zA-Z0-9_\\\:\.]*)\\([a-zA-Z0-9\.]*)',
        #     string=out_file.handle_output_path(out_file.out_file.value))
        # if match_result is not None and not os.path.exists(path=match_result.group(1)):
        #     os.mkdir(path=match_result.group(1))
        path = out_file.handle_output_path(out_file.out_file.value)
        make_dir(path=path)

    """ 
    I choose to use 'pass' for the statements about parameter. The information has been used while checking.
    """
    def visitParaStmt(self, para_stmt):
        pass

    def visitScatterSetStmt(self, scatter_set_stmt):
        pass

    def visitSetStmt(self, set_stmt):
        pass

    def visitLiteral(self, literal):
        pass

    # @TODO: to judge: it is better to link to data in ReadPicture and so on, or DataObject?
    def visitDataObject(self, data_object):
        pass

    def visitNewObject(self, new_object):
        pass

    def visitFit(self, fit):
        parameters = dict()
        # add the value of parameters needed into the dict().
        parameters['graph_file'] = fit.handle_parameter(parameter='graph_file')
        if fit.start_x is not None:
            parameters['start_x'] = fit.start_x.value
            parameters['start_y'] = fit.start_y.value
            parameters['end_x'] = fit.end_x.value
            parameters['end_y'] = fit.end_y.value
        if fit.start_frame is not None:
            parameters['start_frame'] = fit.start_frame.value
            parameters['end_frame'] = fit.end_frame.value
        # for parameter_name in parameter.parameters_used['fit']:
        #     # parameters[parameter_name] = fit.handle_parameter(parameter=parameter_name)
        #     add_for_parameter(node=fit, parameter_dictionary=parameters, parameter_name=parameter_name)
        prepare_the_parameter_dictionary(node=fit, parameter_dictionary=parameters, node_name='fit')
        # fit_engine = fit_analyzer.FitAnalyzer()
        fit_engine = fit_analyzer.FitAnalyzerFactory().create_analyzer(analyzer_type=parameters['pattern_data_mode'])
        molecule_list = fit_engine.fit(parameters=parameters)
        symbol_search = self.table.search_symbol(name=fit.new_object.name)
        symbol_search.link_to_data(data=molecule_list)

    def visitScatter(self, scatter):
        parameters = dict()
        prepare_the_parameter_dictionary(node=scatter, parameter_dictionary=parameters, node_name='scatter')
        scatter_engine = visual.ScatterGeneratorFactory().create_scatter(parameters=parameters)
        symbol_search = self.table.search_symbol(scatter.new_object.name)
        symbol_search.link_to_data(scatter_engine)

    def visitPolygon(self, polygon):
        symbol_search = self.table.search_symbol(polygon.new_object.name)
        point_list = [graph.Point(x=point[0].value, y=point[1].value) for point in polygon.point_list]
        symbol_search.link_to_data(graph.Polygon(points=point_list))

    def visitCircle(self, circle):
        symbol_search = self.table.search_symbol(circle.new_object.name)
        center_point = graph.Point(x=circle.center_x.value, y=circle.center_y.value)
        radius = abs(circle.radius.value)
        symbol_search.link_to_data(data=graph.Circle(center_point=center_point, radius=radius))

    def visitMark(self, mark):
        picture = self.table.search_symbol(mark.picture_object.name).return_data()
        # scatter = self.table.search_symbol(mark.scatter_object.name).return_data()
        # molecules = self.table.search_symbol(mark.data_object.name).return_data()
        mark.out_file.accept(self)
        out_file_path = mark.handle_output_path(path=mark.out_file.out_file.value)
        begin = mark.start_frame.value if mark.start_frame is not None else None
        end = mark.end_frame.value if mark.end_frame is not None else None
        step = mark.segment_frame.value if mark.segment_frame is not None else None
        data_list, scatter_list = [], []
        for mark_sub in mark.mark_list:
            # data_object, scatter_object = mark_sub.accept(self)
            # print(len(result))
            data_object = self.table.search_symbol(mark_sub.data_object.name).return_data()
            scatter_object = self.table.search_symbol(mark_sub.scatter_object.name).return_data()
            data_list.append(data_object)
            scatter_list.append(scatter_object)
        visual.Marker.mark(
            picture=picture, out_path=out_file_path, scatter_list=scatter_list, data_list=data_list,
            begin=begin, end=end, step=step
        )

    def visitMarkSub(self, mark_sub):
        pass
        # # print('execute mark_sub')
        # data_object = self.table.search_symbol(mark_sub.data_object.name).return_data()
        # scatter_object = self.table.search_symbol(mark_sub.scatter_object.name).return_data()
        # # print('%s %s' % (type(data_object), type(scatter_object)))
        # return data_object, scatter_object

    def visitFilter(self, filter_object):
        data_search = self.table.search_symbol(filter_object.data_object.name)
        data_molecule = data_search.return_data()
        graph_search = self.table.search_symbol(filter_object.graph_object.name)
        graph_object = graph_search.return_data()
        # start_frame, end_frame = filter_object.start_frame.value, filter_object.end_frame.value
        start_frame = filter_object.start_frame.value if filter_object.start_frame is not None else None
        end_frame = filter_object.end_frame.value if filter_object.end_frame is not None else None
        new_data_search = self.table.search_symbol(filter_object.new_object.name)
        new_data_search.link_to_data(data=data_analyzer.filter_molecule(
            old_molecule_list=data_molecule, graph_object=graph_object, start_frame=start_frame, end_frame=end_frame))

    def visitMerge(self, merge):
        new_data_search = self.table.search_symbol(merge.new_object.name)
        old_list = []
        for old_data in merge.data_object_list:
            old_list.append(self.table.search_symbol(old_data.name))
        new_data_search.link_to_data(data=data_analyzer.merge_molecules(old_lists=old_list, merge_mode=merge.mode))

    def visitReadMolecule(self, read_molecule):
        input_file = read_molecule.handle_input_path(path=read_molecule.file_path.file_path.value)
        symbol_search = self.table.search_symbol(read_molecule.new_object.name)
        data_molecule = data.MoleculeList()
        data_molecule.read_data_from_csv(file_name=input_file)
        symbol_search.link_to_data(data=data_molecule)

    def visitWriteMolecule(self, write_molecule):
        write_molecule.out_file.accept(self)
        output_file = write_molecule.handle_output_path(path=write_molecule.out_file.out_file.value)
        symbol_search = self.table.search_symbol(write_molecule.data_object.name)
        data_molecule = symbol_search.return_data()
        data_molecule.write_data_into_csv(file_name=output_file)

    # @TODO: write a csv writer?
    def visitTimeLine(self, time_line):
        time_line.out_path.accept(self)
        symbol_search = self.table.search_symbol(time_line.data_object.name)
        graph_search = symbol_search.return_data()
        graph_file = time_line.handle_parameter('graph_file')
        sum_data = data_analyzer.time_line_summer[time_line.handle_parameter('time_line_mode')](
            graph_file=graph_file, graph_object=graph_search)
        output_file = time_line.handle_output_path(path=time_line.out_path.out_file.value)
        out_file = open(file=output_file, mode='w', newline='')
        fieldnames = ['frame', 'value']
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(0, len(sum_data)):
            writer.writerow({'frame': i, 'value': sum_data[i]})

    def visitDistrictAnalyze(self, district_analyze):
        district_analyze.out_file.accept(self)
        graph_search = self.table.search_symbol(district_analyze.graph_object.name)
        graph_object = graph_search.return_data()
        data_search = self.table.search_symbol(district_analyze.data_object.name)
        data_object = data_search.return_data()
        start_frame, end_frame = district_analyze.start_frame.value, district_analyze.end_frame.value
        result, distribution = data_analyzer.district_analyze(
            data_molecule=data_object, graph_object=graph_object, start_frame=start_frame, end_frame=end_frame)
        output_path = district_analyze.handle_output_path(path=district_analyze.out_file.out_file.value)
        out_file = open(file=output_path, mode='w', newline='')
        writer = csv.writer(out_file)
        writer.writerow(result)
        del writer
        out_file.close()
        out_file = open(file=output_path, mode='a', newline='')
        writer = csv.DictWriter(out_file, fieldnames=['frame', 'number', 'exist'])
        writer.writerows(distribution)
        del writer
        out_file.close()

    def visitCorrelation(self, correlation):
        correlation.out_file.accept(self)
        out_path = correlation.handle_output_path(correlation.out_file.out_file.value)
        symbol_a = self.table.search_symbol(correlation.data_a.name)
        data_a = symbol_a.return_data()
        symbol_b = self.table.search_symbol(correlation.data_b.name)
        data_b = symbol_b.return_data()
        parameters = dict()
        formula_type = correlation.handle_parameter('correlation_formula')
        data_mode = correlation.handle_parameter('correlation_data_mode')
        parameter_list = parameter.parameter_dependency['correlation_formula'][formula_type] + \
            parameter.parameter_dependency['correlation_data_mode'][data_mode]
        for parameter_to_add in parameter_list:
            parameters[parameter_to_add] = correlation.handle_parameter(parameter_to_add)
        info = data_analyzer.CorrelationFactory().return_correlation(
            type_name=data_mode, parameter=parameters).calculate(
            data_a=data_a, data_b=data_b, method=formula_type
        )
        print_engine = printer.PrinterFactory.return_printer(print_to=open(out_path, 'w'))
        print_engine.print(info)
        del print_engine


def prepare_the_parameter_dictionary(node, parameter_dictionary, node_name):
    for parameter_name in parameter.parameters_used[node_name]:
        add_for_parameter(node=node, parameter_dictionary=parameter_dictionary, parameter_name=parameter_name)


def add_for_parameter(node, parameter_dictionary, parameter_name):
    value = node.handle_parameter(parameter=parameter_name)
    parameter_dictionary[parameter_name] = value
    if parameter.parameter_dependency.get(parameter_name) is not None \
            and parameter.parameter_dependency[parameter_name].get(value) is not None:
        for parameter_need in parameter.parameter_dependency[parameter_name][value]:
            add_for_parameter(node=node, parameter_dictionary=parameter_dictionary, parameter_name=parameter_need)


def make_dir(path):
    match_result = re.match(pattern=r'([a-zA-Z0-9_\\\:\.\s\-]*)\\([a-zA-Z0-9\.\s\-]*)', string=path)
    # if match_result is not None and not os.path.exists(path=match_result.group(1)):
    #     os.mkdir(path=match_result.group(1))
    if match_result is None:
        os.mkdir(path=path)
    elif not os.path.exists(path=match_result.group(1)):
        try:
            os.mkdir(path=match_result.group(1))
        except FileNotFoundError:
            make_dir(path=match_result.group(1))
            os.mkdir(path=match_result.group(1))
