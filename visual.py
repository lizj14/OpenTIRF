# ---------------------------------------------
# visual.py
# the classes about the dealing with pictures.
# ---------------------------------------------

# import pylab as py
# import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import module_base
from fit_analyzer import VERY_BIG

color_dictionary = {
    'snow': (255, 250, 250),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'grey': (190, 190, 190),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'red': (255, 0, 0),
    'pink': (255, 192, 203),
    'orange': (255, 165, 0),
    'purple': (160, 32, 240),
}


class Picture:
    def __init__(self, file_path):
        self.img = Image.open(file_path)
        if self.img.mode != 'RGB' or self.img.mode != 'RGBA':
            # the value of the gray scale may exceed 256, which is the max value in 'RGB' mode.
            data_array = np.array(self.img)
            data_array = data_array / data_array.max() * 255
            self.img = Image.fromarray(data_array)
            self.img = self.img.convert('RGB')

    def picture(self):
        """
        Attention: it returns a copy instead of the img itself!
        many operation may change the img.
        :return: class 'PIL.Image.Image'
        """
        return self.img.copy()

    def picture_size(self):
        return self.img.size


class ScatterGenerator:
    def __init__(self):
        pass

    def generate_scatter(self, molecule_list, to_scatter):
        pass


class NormalGenerator(ScatterGenerator):
    def __init__(self, size, shape, binning, color, alpha):
        ScatterGenerator.__init__(self)
        self.binning = binning
        self.painter = PainterFactory().create_painter(
            shape=shape, size=size, color=color_dictionary.get(color, (255, 0, 0)), alpha=alpha)

    def generate_scatter(self, molecule_list, to_scatter):
        """
        :param molecule_list: list of object of class Molecule
        :param to_scatter: Image.new(...)
        :return:
        """
        # scatters = Image.new(mode='RGBA', size=size)
        draw = ImageDraw.Draw(im=to_scatter)
        # locations = [(molecule.x(), molecule.y()) for molecule in molecule_list.molecule_list()]
        locations = [(molecule.x(), molecule.y()) for molecule in molecule_list]
        for point in locations:
            self.painter.paint(draw=draw, x=point[0]*self.binning, y=point[1]*self.binning)
        # why to del draw? because the ImageDraw is very awful... any change will be put on the picture linked to the
        # object. So delete it right after it has been used in order not to make any more changes.
        del draw
        # return to_scatter


class ScatterGeneratorFactory(module_base.Singleton):
    # @classmethod
    # def create_scatter(cls, parameters):
    #     return ScatterGeneratorFactory.scatters[parameters['scatter_mode']](cls, parameters)

    # @classmethod
    # def create_normal_generator(cls, parameters):
    #     return NormalGenerator(
    #         size=parameters['mark_size'], shape=parameters['mark_shape'], alpha=parameters['mark_alpha'],
    #         color=parameters['mark_color'], binning=parameters['scatter_bin'],
    #     )
    def __init__(self):
        ScatterGeneratorFactory.scatters['normal'] = ScatterGeneratorFactory.create_normal_generator

    @staticmethod
    def create_scatter(parameters):
        # print(ScatterGeneratorFactory.scatters[parameters['scatter_mode']])
        return ScatterGeneratorFactory.scatters[parameters['scatter_mode']](parameters)

    @staticmethod
    def create_normal_generator(parameters):
        return NormalGenerator(
            size=parameters['mark_size'], shape=parameters['mark_shape'], alpha=parameters['mark_alpha'],
            color=parameters['mark_color'], binning=parameters['scatter_bin'],
        )

    scatters = {
        # 'normal': create_normal_generator.__get__(obj=object, type=function),
        # 'normal': create_normal_generator.__get__(object),
    }


# Now, I think this class as useless and discarded.
class ScatterInfo:
    def __init__(self, painter, x, y):
        self.x = x
        self.y = y
        self.painter = painter


class Painter:
    def __init__(self, size, color):
        self.size = size
        self.color = color

    def paint(self, draw, x, y):
        self.paint_graph(draw=draw, x=int(x), y=int(y))

    def paint_graph(self, draw, x, y):
        pass


class CirclePainter(Painter):
    def __init__(self, size, color):
        Painter.__init__(self, size=size, color=color)

    def paint_graph(self, draw, x, y):
        # print('%s %s' % (x, self.color))
        # x, y = int(x), int(y)
        draw.ellipse([x-self.size, y-self.size, x+self.size, y+self.size], outline=self.color)


class CrossPainter(Painter):
    def __init__(self, size, color):
        Painter.__init__(self, size=size, color=color)

    def paint_graph(self, draw, x, y):
        draw.line([x, y-self.size, x, y+self.size], fill=self.color)
        draw.line([x-self.size, y, x+self.size, y], fill=self.color)


class PainterFactory(module_base.Singleton):
    def __init__(self):
        self.__painters_ = dict()

    def create_painter(self, shape, size, color, alpha):
        if self.__painters_.get((shape, size, color, alpha), None) is None:
            self.__painters_[(shape, size, color, alpha)] = PainterFactory.painters[shape](
                size=size, color=color+(alpha,))
        return self.__painters_[(shape, size, color, alpha)]

    painters = {
        'circle': CirclePainter,
        'cross': CrossPainter,
    }


# @TODO: I think it better to realize the auto deal with format of the picture later.
class Marker:
    @classmethod
    def mark(cls, picture, out_path, scatter_list, data_list, begin=None, end=None, step=None):
        """

        :param picture: class Visual.Pictur
        :param out_path: string, out put file path
        :param scatter_list: list of class Visual.Scatter
        :param data_list: list of class data.MoleculeList
        :param begin: int
        :param end: int
        :param step: int
        :return:
        """
        # scatters = Image.new(mode='RGBA', size=size)
        pic = picture.picture().convert('RGBA')
        pic_size = picture.picture_size()
        begin = 0 if begin is None else begin
        end = VERY_BIG if end is None else end
        step = end - begin if step is None else step

        picture_dict = dict()
        frame_now = begin
        while frame_now < end:
            picture_dict[frame_now] = Marker.new_marker(pic_size)
            frame_now += step

        for i in range(0, len(scatter_list)):
            Marker.mark_sub(picture_dict=picture_dict, molecule_list=data_list[i], scatter=scatter_list[i],
                            begin=begin, end=end, step=step)

        for (frame, new_pic_now) in picture_dict.items():
            new_picture = Image.alpha_composite(im1=pic, im2=new_pic_now)
            new_picture.save('%s_%d_%d.png' % (out_path, frame, frame + step - 1))

    @classmethod
    def mark_sub(cls, picture_dict, molecule_list, scatter, begin, end, step):
        molecule_lists = dict()
        frame_now = begin
        # this is as the common rule in Python: left included while right not.
        while frame_now < end:
            molecule_lists[frame_now] = []
            frame_now += step
        for molecule in molecule_list.molecule_list():
            frame = molecule.start()
            # the duration of the molecule is not demanded.
            if frame < begin or frame >= end:
                continue
            frame -= (molecule.start() - begin) % step
            while frame <= molecule.end() and frame < end:
                molecule_lists[frame].append(molecule)
                frame += step
        for (frame, frame_molecule_list) in molecule_lists.items():
            scatter.generate_scatter(to_scatter=picture_dict[frame], molecule_list=frame_molecule_list)
            # new_picture = Image.alpha_composite(im1=pic, im2=marks)
            # new_picture.save('%s_%d_%d.png' % (out_path, frame, frame+step-1))

    @classmethod
    def new_marker(cls, size):
        return Image.new(mode='RGBA', size=size)

    def out_path(self):
        pass
