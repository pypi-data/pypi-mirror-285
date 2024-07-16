import os
from pathlib import PurePosixPath
from .data import extract_global_data


def test_find_single_file(tmp_path):
    fname = "dogs.yaml"
    yaml = """
    a: 3
    b: 5
    """
    tmp_path.joinpath(fname).write_text(yaml)

    data = extract_global_data(tmp_path)
    dogs = data['dogs']
    assert dogs['a'] == 3
    assert dogs['b'] == 5


def test_find_all_single_files(tmp_path):
    fname = "cats.yaml"
    yaml = """
    a: 3
    b: 5
    """
    tmp_path.joinpath(fname).write_text(yaml)

    fname = "birds.yaml"
    yaml = """
    d: 5
    e: hello
    """
    tmp_path.joinpath(fname).write_text(yaml)

    data = extract_global_data(tmp_path)
    assert data['cats']['a'] == 3
    assert data['cats']['b'] == 5
    assert data['birds']['d'] == 5
    assert data['birds']['e'] == "hello"


def test_find_single_nested_files(tmp_path):
    fname = "animals/cats.yaml"
    yaml = """
    a: 3
    b: 5
    """
    path = tmp_path.joinpath(fname)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml)

    fname = "animals/bees.yaml"
    yaml = """
    e: 3
    f: 5
    """
    path = tmp_path.joinpath(fname)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml)

    data = extract_global_data(tmp_path)
    assert data['animals']['cats']['a'] == 3
    assert data['animals']['cats']['b'] == 5
    assert data['animals']['bees']['e'] == 3
    assert data['animals']['bees']['f'] == 5



def test_double_nested_file(tmp_path):
    fname = "animals/dogs/pug.yaml"
    yaml = """
    a: 3
    b: 5
    """
    path = tmp_path.joinpath(fname)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml)

    fname = "animals/dogs/pom.yaml"
    yaml = """
    a: 13
    b: 15
    """
    path = tmp_path.joinpath(fname)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml)

    data = extract_global_data(tmp_path)
    assert data['animals']['dogs']['pug']['a'] == 3
    assert data['animals']['dogs']['pug']['b'] == 5
    assert data['animals']['dogs']['pom']['a'] == 13
    assert data['animals']['dogs']['pom']['b'] == 15



def test_gets_path_of_image_files(tmp_path):
    
    # create a folder with an image in it.
    fname = "animals/dog/dog.jpg"
    path = tmp_path / fname
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    fname = "animals/cat/image.png"
    path = tmp_path / fname
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    data = extract_global_data(tmp_path)
    assert 'animals/dog/dog.jpg' in str(PurePosixPath(data['animals']['dog']['dog']))
    assert 'animals/cat/image.png' in str(PurePosixPath(data['animals']['cat']['image']))


def test_gets_path_of_image_files_with_relative_paths(tmp_path):
    
    # create a folder with an image in it.
    fname = "animals/dog/dog.jpg"
    path = tmp_path / fname
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    os.chdir(tmp_path)
    data = extract_global_data(tmp_path)
    assert 'animals/dog/dog.jpg' in str(PurePosixPath(data['animals']['dog']['dog']))


def test_no_subkey_is_added_if_fielname_is_only_yaml_extension(tmp_path):
    fname = "animals/dogs/.yaml"
    yaml = """
    a: 3
    b: 5
    """
    path = tmp_path.joinpath(fname)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml)

    data = extract_global_data(tmp_path)
    assert '.yaml' not in data['animals']['dogs']
    assert data['animals']['dogs']['a'] == 3


def test_only_yaml_extension_can_provide_default_values_for_images(tmp_path):
    fname = "dogs/.yaml"
    yaml = """
    image: 'https://www.default.com/image.png'
    pic: 'https://www.default.com/image.png'
    b: 5
    """
    path = tmp_path.joinpath(fname)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml)

    fname = "dogs/image.png"
    tmp_path.joinpath(fname).touch()


    data = extract_global_data(tmp_path)
    assert data['dogs']['b'] == 5
    assert data['dogs']['pic'] == 'https://www.default.com/image.png'
    assert 'dogs/image.png' in str(PurePosixPath(data['dogs']['image']))


def test_absolute_paths_result_in_relative_paths(tmp_path):
    fname = 'animals/pigs/.yaml'
    yaml = "f: /myfile.png"
    path = tmp_path.joinpath(fname)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml)

    data = extract_global_data(tmp_path)
    assert data['animals']['pigs']['f'] == str(PurePosixPath(tmp_path.joinpath('myfile.png')))
    # breakpoint()
