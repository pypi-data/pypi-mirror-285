from acres import Loader
from . import data


def test_loader_from_module():
    my_loader = Loader(data)

    text_resource = my_loader.readable('text_file')
    assert text_resource.read_text() == 'A file with some text.\n'


def test_loader_from_name():
    my_loader = Loader('acres')

    assert my_loader.readable('py.typed').exists()
