# ---------------------------------------------
# symbol.py
# the class to define the symbols in the script and the table to search in the symbol table.
# ---------------------------------------------

# following: different type of dataObject
dataType = {
    'wrong_type': -2,
    's_reserved': -1,
    's_data_molecule': 0,
    's_picture': 1,
    's_scatter': 2,
    's_area': 3,
}
# unique_table = None

# @TODO: there may be a better implementation: make a dictionary according to dict dataType while preparing.
symbol_string = {
    -2: 'wrong_type',
    -1: 's_reserved',
    0: 's_data_molecule',
    1: 's_picture',
    2: 's_scatter',
    3: 's_area',
}


# the class of dataObject used in the script.
# @name, string: the name of the
# @type, int: the type of the symbol
class Symbol:
    def __init__(self, sym_name, sym_type):
        self.sym_name = sym_name
        self.sym_type = sym_type

    # static method used to judge the type, overridden in the subclasses.

    @staticmethod
    def is_picture():
        return False

    @staticmethod
    def is_scatter():
        return False

    @staticmethod
    def is_reserved():
        return False

    @staticmethod
    def is_area():
        return False

    @staticmethod
    def is_data_molecule():
        return False

    # return if the symbol is with data.
    @staticmethod
    def data_read():
        return False

    def return_name(self):
        return self.sym_name

    def return_type(self):
        return self.sym_type

    def return_data(self):
        pass

    def link_to_data(self, data):
        pass


# the class of reserved symbols
class SymbolReserved(Symbol):
    def __init__(self, name):
        Symbol.__init__(self, name, dataType['s_reserved'])

    @staticmethod
    def is_reserved():
        return True


# the class of object pointed to data_molecules
# @data, TODO class DataMolecule: the information of the data molecule.
class SymbolDataMolecule(Symbol):
    def __init__(self, name):
        Symbol.__init__(self, name, dataType['s_data_molecule'])
        self.data = None

    @staticmethod
    def is_data_molecule():
        return True

    # return the data of the molecules.
    def return_data(self):
        return self.data

    def link_to_data(self, data):
        self.data = data


# the class of the object pointed to a picture.
# @data, TODO class Picture: the background on which the mark of data molecule is scattered.
class SymbolPicture(Symbol):
    def __init__(self, name):
        Symbol.__init__(self, name, dataType['s_picture'])
        self.data = None

    @staticmethod
    def is_picture():
        return True

    # return the data of the picture.
    def return_data(self):
        return self.data

    def link_to_data(self, data):
        self.data = data


# the class of the object pointed to a scatter.
# @scatter, TODO class Scatter: the scatter.
class SymbolScatter(Symbol):
    def __init__(self, name):
        Symbol.__init__(self, name, dataType['s_scatter'])
        self.data = None

    @staticmethod
    def is_scatter():
        return True

    def return_data(self):
        return self.data

    def link_to_data(self, data):
        self.data = data


class SymbolArea(Symbol):
    def __init__(self, name):
        Symbol.__init__(self, sym_name=name, sym_type=dataType['s_area'])
        self.data = None

    @staticmethod
    def is_area():
        return True

    def return_data(self):
        return self.data

    def link_to_data(self, data):
        self.data = data


class SymbolTable:
    """
    this is the table of the object used in the program.
    @self.table, dict, string -> symbol: the symbol table.
    Attention!
    here use a simple implementation Singleton mode with function Instance(). If more function need, for example:
    concurrency problem, then the implementation need updating
    """
    # remember not to create SymbolTable directly!
    def __init__(self):
        self.table = {}

    # @name, string: the name to search.
    # return None if not found.
    def search_symbol(self, name):
        try:
            return self.table[name]
        except KeyError:
            return None

    # there is no check! the check is done outside.
    # @name, string: the name of the symbol.
    # @sym_type, int: according to the dataType dictionary
    def create_symbol(self, name, sym_type):
        self.table[name] = SymbolFactory.create_symbol(name, sym_type)

    # read the list of reserved string, and set them reserved, in order to make sure
    # that they will not be used in the following program.
    # @name_list, list of string: names to be set.
    def read_reserve(self, name_list):
        for name in name_list:
            self.create_symbol(name, dataType['s_reserved'])


# the class used to create symbols.
class SymbolFactory:
    @classmethod
    def create_symbol(cls, name, sym_type):
        if sym_type == dataType['s_reserved']:
            return SymbolReserved(name)
        elif sym_type == dataType['s_data_molecule']:
            return SymbolDataMolecule(name)
        elif sym_type == dataType['s_scatter']:
            return SymbolScatter(name)
        elif sym_type == dataType['s_picture']:
            return SymbolPicture(name)
        elif sym_type == dataType['s_area']:
            return SymbolArea(name=name)


# the function to return the only example of the SymbolTable.
def table_instance():
    global unique_table
    try:
        unique_table
    except NameError:
        unique_table = SymbolTable()
    return unique_table
