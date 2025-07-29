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
        assert s.composition["N"] == 0.78
        assert s.composition["O"] == 0.21
        assert s["density"]() == 1.2

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
        assert s.composition["A"] == 10

        # Отрицательные значения (должны вызывать ошибку)
        with pytest.raises((AssertionError, ValueError)):
            Substance("Test", {"A": -1})

    def test_add(self):
        """Тест сложения двух веществ"""
        # Создаем тестовые вещества
        water = Substance("Water", {"H": 2, "O": 1})
        salt = Substance("Salt", {"Na": 1, "Cl": 1})

        mixture = water + salt

        assert mixture.name == "Water+Salt"
        assert set(mixture.composition.keys()) == {"H", "O", "Na", "Cl"}
        assert mixture.composition["H"] == 2
        assert mixture.composition["O"] == 1
        assert mixture.composition["Na"] == 1
        assert mixture.composition["Cl"] == 1

        # Тест смешения с общими элементами
        water1 = Substance("Water1", {"H": 2, "O": 1})
        water2 = Substance("Water2", {"H": 1, "O": 1, "D": 1})  # D - дейтерий

        mixture = water1 + water2

        assert mixture.name == "Water1+Water2"
        assert mixture.composition["H"] == 3  # 2 + 1
        assert mixture.composition["O"] == 2  # 1 + 1
        assert mixture.composition["D"] == 1  # только из water2

        # Тест смешения с веществом без состава
        water = Substance("Water", {"H": 2, "O": 1})
        empty = Substance("")

        mixture = water + empty

        assert mixture.name == "Water+"
        assert mixture.composition == water.composition

        # Тест попытки сложения с не-Substance объектом
        water = Substance("Water")

        with pytest.raises(AssertionError):
            water + 123  # попытка сложить с числом

        # Тест коммутативности сложения веществ
        water = Substance("Water", {"H": 2, "O": 1})
        salt = Substance("Salt", {"Na": 1, "Cl": 1})

        mix1 = water + salt
        mix2 = salt + water

        # Составы должны быть одинаковыми независимо от порядка
        assert mix1.composition == mix2.composition
        # Но имена будут разными
        assert mix1.name == "Water+Salt"
        assert mix2.name == "Salt+Water"

        # Тест сохранения параметров при сложении
        water = Substance("Water", parameters={"temp": 20})
        salt = Substance("Salt", parameters={"mass": 10})

        mixture = water + salt

        # Параметры не должны переноситься при сложении
        assert not mixture.parameters  # должен быть пустой словарь
