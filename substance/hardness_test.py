import pytest
from numpy import isnan

try:
    from .hardness import Hardness, data
except ImportError:
    from hardness import Hardness, data


class TestHardness:
    """Тесты для класса Hardness"""

    def test_init(self):
        """Тест инициализации твердости"""
        for d in data:
            del d["d10mm"]  # лишняя инфа
            for key, value in d.items():
                if isnan(value):
                    continue
                obj = Hardness(**{key: value})
                for k, v in obj.values.items():
                    if isnan(v):
                        continue
                    else:
                        assert v == pytest.approx(d[k], rel=0.02), f"{key}={value} -> {k}={v}"

    @pytest.mark.benchmark
    def test_hardness_init(self, benchmark):
        def benchfunc():
            Hardness(HB=229)

        benchmark(benchfunc)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-x"])
