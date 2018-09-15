# ------------------------------------
# ply-test.py
# See: Ply at GitHub: https://github.com/dabeaz/ply
# using Ply version 3.10, from pip -install pip.
# test the ply and complete the lex and yacc part
# ------------------------------------
import ply.lex as lex
import ply.yacc as yacc
import tree
import printer
import sys
import os
import symbol
import checker
import executor
import debug

# following files generated each time. need to delete.
to_clean = ['parser.out', 'parsetab.py']
for file_to_clean in to_clean:
    if os.path.exists(file_to_clean):
        os.remove(file_to_clean)

# writer = printer.WriteVisitor()
type_checker = checker.Checker()
runner = executor.Executor(table=symbol.table_instance(), print_engine=printer.PrinterFactory().return_printer())

reserved = {
    'set': 'SET',
    'read_graph': 'READ_GRAPH',
    'read_picture': 'READ_PICTURE',
    'end': 'END',
    'fit': 'FIT',
    'scatter': 'SCATTER',
    'read_molecule': 'READ_MOLECULE',
    'write_molecule': 'WRITE_MOLECULE',
    'mark': 'MARK',
    'polygon': 'POLYGON',
    'time_line': 'TIME_LINE',
    'circle': 'CIRCLE',
    'district_analyze': 'DISTRICT_ANALYZE',
    'filter': 'FILTER',
    'correlation': 'CORRELATION',
    'merge': 'MERGE',
    'same_time': 'SAME_TIME',
}

tokens = (
    'NAME', 'NUMBER', 'STRING', 'FLOAT',
) + tuple(reserved.values())

# Tokens


def t_NAME(t):
    r"""[a-zA-Z_][a-zA-Z0-9_]*"""
    t.type = reserved.get(t.value, 'NAME')
    return t


def t_FLOAT(t):
    # r"""\d+\.\d+"""
    r"""(-)?\d+\.\d+"""
    t.value = float(t.value)
    return t


def t_NUMBER(t):
    # r"""\d+"""
    r"""(-)?\d+"""
    t.value = int(t.value)
    # t.line_no = t.lexer.lineno
    return t


def t_STRING(t):
    r"""\'[a-zA-Z0-9_:\\\s\/\-\.\,]*\'"""
    t.value = str(t.value)[1:len(t.value) - 1]
    return t


# Ignored Characters
t_ignore = ' \t'


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += t.value.count('\n')


def t_error(t):
    # print("Illegal characters '%d'" % t.value[0])
    print('Illegal characters : %s' % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lex.lex()

# Precedence Rules
precedence = ()


def p_program(p):
    """program : stmtList"""
    # it is not that good to use 0, but up to now the line no of node program is not used.
    p[0] = tree.Program(0, p[1])
    # p[0].accept(printer.WriteVisitor())
    # here it only read the reserved keys in the script, and those in parameters will be added later. in Checker.py.
    symbol.table_instance().read_reserve(list(reserved.keys()))
    p[0].accept(type_checker)
    if type_checker.show_errors():
        print('yes')
        p[0].accept(runner)
        # p[0].accept(writer)
        if len(p[0].stmt_list) != 0:
            # if type_checker.check_parameter(p[0].stmt_list[len(p[0].stmt_list)-1], parameter_to_check='script_path'):
            #     path = p[0].stmt_list[len(p[0].stmt_list)-1].handle_output_path(
            #         path=p[0].stmt_list[len(p[0].stmt_list)-1].handle_parameter('script_path'))
            # else:
            #     path = p[0].stmt_list[len(p[0].stmt_list)-1].handle_output_path(path='script.txt')
            path = p[0].stmt_list[len(p[0].stmt_list)-1].handle_output_path(
                path=p[0].stmt_list[len(p[0].stmt_list)-1].handle_parameter('script_path')
            ) if type_checker.check_parameter(
                p[0].stmt_list[len(p[0].stmt_list)-1], parameter_to_check='script_path'
            ) else p[0].stmt_list[len(p[0].stmt_list)-1].handle_output_path(path='script.txt')
            writer = printer.WriteVisitor(writer=open(path, 'w'))
            p[0].accept(writer)
    else:
        print('no')
    return p[0]


def p_stmtList_add(p):
    """stmtList : statement stmtList"""
    # p[2].append(p[1])
    # p[0] = p[2]
    if len(p[2]) > 0:
        p[2][0].set_handler(p[1])
    p[0] = [p[1]] + p[2]


def p_stmtList_end(p):
    """stmtList : END"""
    p[0] = []


# there is no set_handler function where it will not be used.
def p_statement_set(p):
    """statement : SET setList"""
    p[0] = tree.SetStmt(p.lineno(1), p[2])


def p_setList_setStmt(p):
    """setList : paraStmt setList"""
    # p[2].append(p[1])
    # p[0] = p[2]
    p[0] = [p[1]] + p[2]


def p_setList_empty(p):
    """setList : END"""
    p[0] = []


def p_paraStmt(p):
    """paraStmt : parameter literal"""
    p[0] = tree.ParaStmt(p.lineno(1), p[1], p[2])


def p_parameter(p):
    """parameter : NAME"""
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_literal(p):
    """literal : STRING
               | NUMBER
               | FLOAT"""
    p[0] = tree.Literal(p.lineno(1), p[1])


# p[4] is a list of statements. It will start a branch structure.
def p_statement_read_graph(p):
    # """statement : READ_GRAPH literal filePath stmtList"""
    """statement : READ_GRAPH filePath stmtList"""
    p[0] = tree.ReadGraph(p.lineno(1), p[2], p[3])
    # p[2].set_handler(p[0])
    p[2].set_handler(p[0])
    if len(p[3]) > 0:
        p[3][0].set_handler(p[0])


def p_statement_read_pic(p):
    """statement : READ_PICTURE newObject filePath"""
    p[0] = tree.ReadPicture(p.lineno(1), p[2], p[3])
    p[2].set_handler(p[0])
    p[3].set_handler(p[0])


def p_file_path(p):
    """filePath : literal"""
    p[0] = tree.FilePath(p[1].line(), p[1])
    p[1].set_handler(p[0])


def p_out_path(p):
    """outPath : literal"""
    p[0] = tree.OutFile(p[1].line(), p[1])
    p[1].set_handler(p[0])


def p_dataObject(p):
    """dataObject : NAME"""
    p[0] = tree.DataObject(p.lineno(1), p[1])


def p_newObject(p):
    """newObject : NAME"""
    p[0] = tree.NewObject(p.lineno(1), p[1])


def p_statement_fit(p):
    """statement : FIT newObject"""
    p[0] = tree.Fit(p.lineno(1), p[2])
    p[2].set_handler(p[0])


def p_statement_time_line(p):
    """statement : TIME_LINE dataObject outPath"""
    p[0] = tree.TimeLine(line=p.lineno(1), data_object=p[2], out_path=p[3])
    p[2].set_handler(p[0])
    p[3].set_handler(p[0])


def p_statement_fit_part_location(p):
    """statement : FIT newObject literal literal literal literal"""
    p[0] = tree.Fit(p.lineno(1), p[2], start_x=p[3], start_y=p[4], end_x=p[5], end_y=p[6])
    ps = [p[2], p[3], p[4], p[5], p[6]]
    for p_example in ps:
        p_example.set_handler(p[0])


def p_statement_fit_part_time(p):
    """statement : FIT newObject literal literal"""
    p[0] = tree.Fit(p.lineno(1), p[2], start_frame=p[3], end_frame=p[4])
    for p_example in [p[2], p[3], p[4]]:
        p_example.set_handler(p[0])


def p_statement_fit_part(p):
    """statement : FIT newObject literal literal literal literal literal literal"""
    p[0] = tree.Fit(p.lineno(1), p[2],
                    start_x=p[3], start_y=p[4], end_x=p[5], end_y=p[6], start_frame=p[7], end_frame=p[8])
    for p_example in [p[2], p[3], p[4], p[5], p[6], p[7], p[8]]:
        p_example.set_handler(p[0])


def p_statement_district_analyze(p):
    """statement : DISTRICT_ANALYZE dataObject dataObject outPath literal literal"""
    p[0] = tree.DistrictAnalyze(
        line=p.lineno(1), data_object=p[2], graph_object=p[3], out_file=p[4], start_frame=p[5], end_frame=p[6])
    p_s = [p[2], p[3], p[4], p[5], p[6]]
    for p_ex in p_s:
        p_ex.set_handler(p[0])


def p_statement_filter_all(p):
    """statement : FILTER dataObject newObject dataObject literal literal"""
    p[0] = tree.Filter(
        line=p.lineno(1), data_object=p[2], new_object=p[3], graph_object=p[4], start_frame=p[5], end_frame=p[6])
    p_s = [p[2], p[3], p[4], p[5], p[6]]
    for p_ex in p_s:
        p_ex.set_handler(p[0])


def p_statement_filter_graph(p):
    """statement : FILTER dataObject newObject dataObject"""
    p[0] = tree.Filter(line=p.lineno(1), data_object=p[2], new_object=p[3], graph_object=p[4])
    p[2].set_handler(p[0])
    p[3].set_handler(p[0])
    p[4].set_handler(p[0])


def p_statement_filter_frame(p):
    """statement : FILTER dataObject newObject literal literal"""
    p[0] = tree.Filter(line=p.lineno(1), data_object=p[2], new_object=p[3], start_frame=p[4], end_frame=[5])
    p_s = [p[2], p[3], p[4], p[5]]
    for p_ex in p_s:
        p_ex.set_handler(p[0])


def p_statement_correlation(p):
    """statement : CORRELATION dataObject dataObject outPath """
    p[0] = tree.Correlation(line=p.lineno(1), data_object_a=p[2], data_object_b=p[3], out_file=p[4])
    for p_now in [p[2], p[3], p[4]]:
        p_now.set_handler(p[0])


def p_statement_polygon(p):
    """statement : POLYGON newObject pointList"""
    p[0] = tree.Polygon(line=p.lineno(1), new_object=p[2], point_list=p[3])


def p_statement_circle(p):
    """statement : CIRCLE newObject literal literal literal"""
    p[0] = tree.Circle(line=p.lineno(1), new_object=p[2], center_x=p[3], center_y=p[4], radius=p[5])


def p_point_list_new_point(p):
    """pointList : literal literal pointList"""
    p[0] = [[p[1], p[2]]] + p[3]


def p_point_list_empty(p):
    """pointList : """
    p[0] = []


def p_statement_merge(p):
    """statement : MERGE newObject dataObjectList"""
    p[0] = tree.Merge(line=p.lineno(1), new_object=p[2], data_object_list=p[3], mode='normal')
    p[2].set_handler(p[0])
    for p_ex in p[3]:
        p_ex.set_handler(p[0])


def p_statement_merge_same_time(p):
    """statement : MERGE SAME_TIME newObject dataObjectList"""
    p[0] = tree.Merge(line=p.lineno(1), new_object=p[2], data_object_list=p[3], mode='same_time')
    p[2].set_handler(p[0])
    for p_ex in p[3]:
        p_ex.set_handler(p[0])


def p_data_object_list_new(p):
    """dataObjectList : dataObject dataObjectList"""
    p[0] = [p[1]] + p[2]


def p_data_object_list_empty(p):
    """dataObjectList : """
    p[0] = []


def p_statement_read_molecule(p):
    """statement : READ_MOLECULE newObject filePath"""
    p[0] = tree.ReadMolecule(p.lineno(1), p[2], p[3])
    p[2].set_handler(p[0])
    p[3].set_handler(p[0])


def p_statement_write_molecule(p):
    """statement : WRITE_MOLECULE dataObject outPath"""
    p[0] = tree.WriteMolecule(p.lineno(1), p[2], p[3])
    p[2].set_handler(p[0])
    p[3].set_handler(p[0])


def p_statement_scatter(p):
    """statement : SCATTER newObject scatterList"""
    p[0] = tree.Scatter(p.lineno(1), p[2], p[3])
    p[2].set_handler(p[0])


def p_scatterList_add(p):
    """scatterList : parameter literal scatterList"""
    # p[0] = [tree.ScatterSetStmt(p[1].line(), p[1], p[2])] + p[3]
    p[0] = [tree.ScatterSetStmt(line=p.lineno(1), parameter=p[1], value=p[2])] + p[3]


def p_scatterList_end(p):
    """scatterList : END"""
    p[0] = []


def p_mark_list_new(p):
    """markList : mark_sub markList"""
    p[0] = [p[1]] + p[2]


def p_mark_list_end(p):
    """markList : END"""
    p[0] = []


def p_mark(p):
    """statement : MARK dataObject outPath literal literal literal markList"""
    p[0] = tree.Mark(line=p.lineno(1), picture_object=p[2], out_file=p[3], start_frame=p[4],
                     end_frame=p[5], segment_frame=p[6], mark_list=p[7])
    for p_ex in [p[2], p[3], p[4], p[5], p[6]] + p[7]:
        p_ex.set_handler(p[0])


def p_mark_two_border(p):
    """statement : MARK dataObject outPath literal literal markList"""
    p[0] = tree.Mark(
        line=p.lineno(1), picture_object=p[2], out_file=p[3], start_frame=p[4], end_frame=p[5], mark_list=p[6])
    for p_ex in [p[2], p[3], p[4], p[5]] + p[6]:
        p_ex.set_handler(p[0])


def p_mark_frame(p):
    """statement : MARK dataObject outPath literal markList"""
    p[0] = tree.Mark(line=p.lineno(1), picture_object=p[2], out_file=p[3], start_frame=p[4], mark_list=p[5])
    for p_ex in [p[2], p[3], p[4]] + p[5]:
        p_ex.set_handler(p[0])


def p_mark_all(p):
    """statement : MARK dataObject outPath markList"""
    p[0] = tree.Mark(line=p.lineno(1), picture_object=p[2], out_file=p[3], mark_list=p[4])
    for p_ex in [p[2], p[3]] + p[4]:
        p_ex.set_handler(p[0])


def p_mark_sub(p):
    """mark_sub : dataObject dataObject"""
    p[0] = tree.MarkSub(line=p.lineno(1), data_object=p[1], scatter_object=p[2])
    p[1].set_handler(p[0])
    p[2].set_handler(p[0])


def p_error(p):
    print('Syntax error at : %s' % p.value)


t_start = debug.return_time()
yacc.yacc()

file = open(sys.argv[1], 'r')
s = ''
for line in file:
    s += line
# yacc.parse(s, debug=True)
yacc.parse(s)

t_end = debug.return_time()
t_last = t_end - t_start
print('time cost %s' % t_last)
