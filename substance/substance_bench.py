from copy import deepcopy

import pytest

from substance import Substance


@pytest.fixture
def simple_substance():
    """Простое вещество без параметров"""
    return Substance("Water")


@pytest.fixture
def complex_substance():
    """Сложное вещество со всеми параметрами"""
    return Substance(
        "Water",
        composition={"H": 2, "O": 1},
        parameters={"density": 1.0, "viscosity": 0.001},
        functions={
            "heat_capacity": lambda T: 4186 + 0.1 * T,
            "conductivity": lambda P: 0.6 + 0.01 * P,
        },
    )


class TestSubstanceBenchmark:
    """Бенчмарк-тесты для класса Substance"""

    def test_init_simple(self, benchmark, simple_substance):
        """Бенчмарк простой инициализации"""
        benchmark(Substance, "Water")

    def test_init_complex(self, benchmark, complex_substance):
        """Бенчмарк сложной инициализации"""
        benchmark(
            Substance,
            "Water",
            composition={"H": 2, "O": 1},
            parameters={"density": 1.0},
            functions={"Cp": lambda T: 1000 + T},
        )

    def test_deepcopy(self, benchmark, complex_substance):
        """Бенчмарк глубокого копирования"""
        benchmark(deepcopy, complex_substance)

    def test_add_operation(self, benchmark, simple_substance):
        """Бенчмарк операции сложения веществ"""
        other = Substance("Salt", composition={"Na": 1, "Cl": 1})
        benchmark(lambda: simple_substance + other)

    def test_property_access(self, benchmark, complex_substance):
        """Бенчмарк доступа к свойствам"""
        benchmark(lambda: complex_substance.name)
        benchmark(lambda: complex_substance.composition)
        benchmark(lambda: complex_substance.functions["heat_capacity"](300))

    def test_young_modulus(self, benchmark):
        """Бенчмарк статического метода"""
        benchmark(Substance.young_modulus, 0.3, elastic_modulus=200e9)
        benchmark(Substance.young_modulus, 0.3, shear_modulus=80e9)

    def test_excess_oxidizing(self, benchmark, complex_substance):
        """Бенчмарк вычисления свойства"""
        benchmark(lambda: complex_substance.excess_oxidizing)
