from copy import deepcopy

import pytest
from thermodynamics import parameters as tdp

from substance import Substance, young_modulus


class TestSubstance:
    """Тесты для класса Substance"""

    def test_init(self):
        """Тест инициализации вещества"""

        # Простая инициализация
        s = Substance("Water", {"H20": 1}, parameters={tdp.m: 2})
        assert s.name == "Water"
        assert s.composition == {"H20": 1}
        assert s.parameters == {tdp.m: 2}
        assert s.functions == {}

        # С параметрами
        s = Substance(
            "Water",
            composition={"H": 2 / 3, "O": 1 / 3},
            parameters={tdp.m: 2, "density": 1_000},
            functions={"calc": lambda x: x**2},
        )
        assert s.name == "Water"
        assert s.composition == {"H": 2 / 3, "O": 1 / 3}
        assert s.parameters == {tdp.m: 2, "density": 1_000}
        assert "calc" in s.functions

    def test_name_validation(self):
        """Тест валидации имени"""
        with pytest.raises((AssertionError, TypeError)):
            Substance(123, {"H20": 1}, parameters={tdp.m: 2})

        with pytest.raises((AssertionError, TypeError)):
            s = Substance("Water", {"H20": 1}, parameters={tdp.m: 2})
            s.name = 123

    def test_composition_validation(self):
        """Тест валидации состава"""
        # Неправильный тип
        with pytest.raises((AssertionError, TypeError)):
            Substance("Water", composition="H2O")

        # Неправильный тип элемента
        with pytest.raises((AssertionError, TypeError)):
            Substance("Water", composition={1: 2, "O": 1})

        # Неправильный тип доли
        with pytest.raises((AssertionError, TypeError)):
            Substance("Water", composition={"H": "two", "O": 1})

        # Отрицательное значение
        with pytest.raises((AssertionError, ValueError)):
            Substance("Water", composition={"H": -1, "O": 1})

    def test_parameters_validation(self):
        """Тест валидации параметров"""
        # Неправильный тип
        with pytest.raises((AssertionError, TypeError)):
            s = Substance("Water", {"H20": 1}, parameters={tdp.m: 2})
            s.parameters = "density=1"

        # Неправильный тип значения
        with pytest.raises((AssertionError, TypeError)):
            s = Substance("Water", {"H20": 1}, parameters={"density": "high"})

    def test_functions_validation(self):
        """Тест валидации функций"""
        # lambda
        Substance("Water", {"H20": 1}, parameters={tdp.m: 2}, functions={"lambda": lambda x: x**2})
        # Не-callable объект
        with pytest.raises((AssertionError, TypeError)):
            Substance("Water", functions={"calc": 123})

    def test_slots(self):
        """Тест защиты __slots__"""
        s = Substance("Water", {"H2O": 1}, parameters={tdp.m: 2})
        with pytest.raises(AttributeError):
            s.new_attr = "value"

    def test_delattr(self):
        """Тест защиты от удаления атрибутов"""
        s = Substance("Water", {"H2O": 1}, parameters={tdp.m: 2})
        with pytest.raises(Exception):
            del s.name

    def test_deepcopy(self):
        """Тест глубокого копирования"""
        s1 = Substance(
            "Water",
            composition={"H": 2 / 3, "O": 1 / 3},
            parameters={tdp.m: 2, "density": 1.0},
            functions={"Cp": lambda T: 1000 + T},
        )
        s2 = deepcopy(s1)

        assert s1.name == s2.name
        assert s1.composition == {"H": 2 / 3, "O": 1 / 3}
        assert s1.parameters == s2.parameters
        assert s1 is not s2

        # Проверка, что это действительно глубокая копия
        s1.composition["H"] = 3
        assert s2.composition["H"] == 2 / 3

        # Проверка, что функции работают корректно
        assert s1.functions["Cp"](T=1) == s2.functions["Cp"](T=1)


class TestMixing:
    """Тесты для функции mixing"""

    pass


def test_young_modulus():
    """Тест расчета модуля Юнга"""
    # Тест с elastic_modulus
    result = young_modulus(0.3, elastic_modulus=2.6)
    assert pytest.approx(result) == 1.0

    # Тест с shear_modulus
    result = young_modulus(0.3, shear_modulus=1.0)
    assert pytest.approx(result) == 2.6

    # Ошибки валидации
    with pytest.raises(ValueError):
        young_modulus(-0.1, elastic_modulus=1.0)

    with pytest.raises(ValueError):
        young_modulus(0.3, elastic_modulus=-1.0)

    with pytest.raises(ValueError):
        young_modulus(0.3)


if __name__ == "__main__":
    print(__file__)
    pytest.main([__file__, "-v", "-s"])
