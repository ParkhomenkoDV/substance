from copy import deepcopy

import pytest
from numpy import isnan

from substance import Substance


class TestSubstance:
    """Тесты для класса Substance"""

    def test_init(self):
        """Тест инициализации вещества"""

        # Простая инициализация
        s = Substance("Water")
        assert s.name == "Water"
        assert s.composition == {}
        assert s.parameters == {}
        assert s.functions == {}

        # С параметрами
        comp = {"H": 2, "O": 1}
        params = {"density": 1.0}
        funcs = {"calc": lambda x: x**2}

        s = Substance("Water", composition=comp, parameters=params, functions=funcs)
        assert s.name == "Water"
        assert s.composition == comp
        assert s.parameters == params
        assert "calc" in s.functions

    def test_name_validation(self):
        """Тест валидации имени"""
        with pytest.raises((AssertionError, TypeError)):
            Substance(123)

        with pytest.raises((AssertionError, TypeError)):
            s = Substance("Water")
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
            s = Substance("Water")
            s.parameters = "density=1"

        # Неправильный тип значения
        with pytest.raises((AssertionError, TypeError)):
            s = Substance("Water", parameters={"density": "high"})

    def test_functions_validation(self):
        """Тест валидации функций"""
        # Не-callable объект
        with pytest.raises((AssertionError, TypeError)):
            Substance("Water", functions={"calc": 123})

    def test_slots_protection(self):
        """Тест защиты __slots__"""
        s = Substance("Water")
        with pytest.raises(AttributeError):
            s.new_attr = "value"

    def test_delete_protection(self):
        """Тест защиты от удаления атрибутов"""
        s = Substance("Water")
        with pytest.raises(Exception):
            del s.name

    def test_deepcopy(self):
        """Тест глубокого копирования"""
        s1 = Substance(
            "Water",
            composition={"H": 2, "O": 1},
            parameters={"density": 1.0},
            functions={"Cp": lambda T: 1000 + T},
        )
        s2 = deepcopy(s1)

        assert s1.name == s2.name
        assert s1.composition == s2.composition
        assert s1.parameters == s2.parameters
        assert s1 is not s2

        # Проверка, что это действительно глубокая копия
        s1.composition["H"] = 3
        assert s2.composition["H"] == 2

        # Проверка, что функции работают корректно
        assert s1.functions["Cp"](T=1) == s2.functions["Cp"](T=1)

    def test_add(self):
        """Тест сложения веществ"""
        s1 = Substance("H2", composition={"H": 2})
        s2 = Substance("O2", composition={"O": 2})
        s3 = s1 + s2

        assert s3.name == "H2+O2"
        assert s3.composition == {"H": 2, "O": 2}

        # Проверка с общими элементами
        s4 = Substance("H2O", composition={"H": 2, "O": 1})
        s5 = s4 + s1
        assert s5.composition["H"] == 4

    def test_young_modulus(self):
        """Тест расчета модуля Юнга"""
        # Тест с elastic_modulus
        result = Substance.young_modulus(0.3, elastic_modulus=2.6)
        assert pytest.approx(result) == 1.0

        # Тест с shear_modulus
        result = Substance.young_modulus(0.3, shear_modulus=1.0)
        assert pytest.approx(result) == 2.6

        # Ошибки валидации
        with pytest.raises(ValueError):
            Substance.young_modulus(-0.1, elastic_modulus=1.0)

        with pytest.raises(ValueError):
            Substance.young_modulus(0.3, elastic_modulus=-1.0)

        with pytest.raises(ValueError):
            Substance.young_modulus(0.3)

    def test_excess_oxidizing(self):
        """Тест расчета коэффициента избытка окислителя"""
        # Вещество с кислородом
        s1 = Substance("O2", composition={"O": 2})
        assert s1.excess_oxidizing == 1.0

        # Вещество без кислорода
        s2 = Substance("H2", composition={"H": 2})
        assert s2.excess_oxidizing == 0.0

        # Пустой состав
        s3 = Substance("Empty")
        assert isnan(s3.excess_oxidizing)

        # Смешанный состав
        s4 = Substance("H2O", composition={"H": 2, "O": 1})
        assert pytest.approx(s4.excess_oxidizing) == 1 / 3
