from copy import deepcopy

import numpy as np
import pytest

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

        # С параметрами
        s = Substance("Air", {"N": 0.78, "O": 0.21}, {"density": 1.2})
        assert s.composition["N"] == pytest.approx(0.78 / (0.78 + 0.21), rel=0.000_1)
        assert s["density"]() == 1.2

    def test_composition_normalization(self):
        """Тест нормализации состава"""
        rel = 0.000_1
        s = Substance("Test", {"A": 1, "B": 1, "C": 3})
        assert s.composition["A"] == pytest.approx(1 / 5, rel=rel)
        assert s.composition["B"] == pytest.approx(1 / 5, rel=rel)
        assert s.composition["C"] == pytest.approx(3 / 5, rel=rel)

    def test_parameter_handling(self):
        """Тест работы с параметрами"""
        s = Substance("Test", parameters={"const": 10, "func": lambda x: x**2})

        # Проверка числового параметра
        assert s["const"]() == 10

        # Проверка функционального параметра
        assert s["func"](2) == 4

        # Проверка несуществующего параметра
        assert np.isnan(s["nonexistent"]())

    def test_parameter_operations(self):
        """Тест операций с параметрами"""
        s = Substance("Test")

        # Добавление параметра
        s["new_param"] = 42
        assert s["new_param"]() == 42

        # Удаление параметра
        del s["new_param"]
        assert "new_param" not in s.parameters

        # Попытка изменения параметра
        s["param"] = 1
        assert s["param"]() == 1

    def test_validation(self):
        """Тест валидации входных данных"""
        # Некорректное имя
        with pytest.raises((AssertionError, TypeError)):
            Substance(123)

        # Некорректный состав
        with pytest.raises((AssertionError, TypeError)):
            Substance("Test", {"A": "not_a_number"})

        # Некорректные параметры
        with pytest.raises((AssertionError, TypeError)):
            Substance("Test", parameters={"param": [1, 2, 3]})

    def test_deepcopy(self):
        """Тест глубокого копирования"""
        s1 = Substance("Test", {"A": 1}, {"param": 10})
        s2 = deepcopy(s1)

        # Проверка копирования
        assert s1.name == s2.name
        assert s1.composition == s2.composition
        assert s1["param"]() == s2["param"]()

        # Проверка независимости копии
        s1["param"] = 20
        assert s1["param"]() != s2["param"]()

    def test_protected_attributes(self):
        """Тест защиты атрибутов"""
        s = Substance("Test")

        # Запрет удаления имени
        with pytest.raises(Exception):
            del s.name

        # Запрет добавления произвольных атрибутов
        with pytest.raises(AttributeError):
            s.new_attr = 123

    def test_callable_parameters(self):
        """Тест callable-параметров с лишними аргументами"""
        s = Substance(
            "Test", parameters={"temp": lambda t: t + 273.15, "press": 101_325}
        )

        # Callable с лишними аргументами
        assert s["temp"](t=20, extra_arg=123) == pytest.approx(293.15)

        # Числовой параметр с аргументами
        assert s["press"](foo="bar") == 101325

    def test_composition_edge_cases(self):
        """Тест крайних случаев состава"""
        # Пустой состав
        s = Substance("Test", {})
        assert s.composition == {}

        # Один элемент
        s = Substance("Test", {"A": 10})
        assert s.composition["A"] == pytest.approx(1.0)

        # Отрицательные значения (должны вызывать ошибку)
        with pytest.raises((AssertionError, ValueError)):
            Substance("Test", {"A": -1})

    def test_jung_modulus(self):
        """Тест расчета модуля Юнга"""
        # Расчет по модулю упругости
        E = Substance.jung(mu=0.3, E=200e9)
        assert E == pytest.approx(76.923e9, rel=1e-3)

        # Расчет по модулю сдвига
        G = Substance.jung(mu=0.3, G=80e9)
        assert G == pytest.approx(208e9, rel=1e-3)

        # Ошибки при неверных входных данных
        with pytest.raises(AssertionError):
            Substance.jung(mu=-0.1, E=200e9)

        with pytest.raises(Exception):
            Substance.jung(mu=0.3)  # Не указан E или G
