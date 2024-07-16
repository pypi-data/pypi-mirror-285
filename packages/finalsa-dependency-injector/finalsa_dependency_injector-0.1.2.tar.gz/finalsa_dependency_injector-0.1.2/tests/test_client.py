from finalsa.dependency.injector import (
    __version__, Container, LifeCycle, DependencyNotFoundException, InvalidInterface
)
import os
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


def test_version():
    assert __version__ is not None


def test_container():
    container = Container()
    assert container is not None


def test_life_cycle():
    assert LifeCycle is not None


def test_dependency_not_found_exception():
    assert DependencyNotFoundException is not None


def test_invalid_interface_exception():
    assert InvalidInterface is not None


def test_add_dependency():
    container = Container()
    container.add_dependency(str, str)
    assert container.dependency_map[str] == str
    assert container.life_cycle_map[str] == LifeCycle.SCOPED


def test_add_builded_dependency():
    container = Container()
    container.add_builded_dependency(str, "test")
    assert container.dependency_map[str] == "test"
    assert container.life_cycle_map[str] == LifeCycle.SINGLETON
    assert container.loaded_dependencies[str] == "test"


def test_get():
    container = Container()
    container.add_dependency(str, str)
    assert container.get(str) == ""


def test_get_singleton_dependency():
    container = Container()
    container.add_builded_dependency(str, "test")
    assert container.get_singleton_dependency(str) == "test"


def test_get_scoped_dependency():
    container = Container(
        get_correlation_id_method=lambda: "test"
    )
    container.add_dependency(str, uuid.uuid4)

    container.set_scope("test")

    first_value = container.get(str)
    second_value = container.get(str)

    assert first_value == second_value

    container.delete_scope("test")

    assert "test" not in container.scoped_loaded_dependencies
