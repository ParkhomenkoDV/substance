from copy import deepcopy

import pytest
from thermodynamics import parameters as tdp

from substance import Substance


@pytest.fixture
def water():
    """Сложное вещество со всеми параметрами"""
    return Substance(
        "Water",
        composition={"H": 2 / 3, "O": 1 / 3},
        parameters={"density": 1000, tdp.m: 10},
        functions={
            "heat_capacity": lambda T: 4186 + 0.1 * T,
            "conductivity": lambda P: 0.6 + 0.01 * P,
        },
    )


@pytest.mark.benchmark
class TestSubstanceBenchmark:
    """Бенчмарки для класса Substance"""

    def test_init(self, benchmark):
        """Бенчмарк инициализации"""

        def benchfunc():
            return Substance(
                "bench",
                {"H": 2 / 3, "O": 1 / 3},
                parameters={tdp.m: 1},
                functions={"Cp": lambda T: 1000 + T},
            )

        benchmark(benchfunc)

    @pytest.mark.parametrize("attr", ["name", "composition", "parameters", "functions"])
    def test_getattr(self, benchmark, water, attr):
        """Бенчмарк доступа к атрибутам"""
        benchmark(lambda: getattr(water, attr))

    def test_deepcopy(self, benchmark, water):
        """Бенчмарк глубокого копирования"""
        benchmark(deepcopy, water)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--benchmark-only", "--benchmark-min-rounds=10"])
