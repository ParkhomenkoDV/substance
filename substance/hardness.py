import json
from math import nan
from typing import Dict

import numpy as np
from scipy.interpolate import interp1d

"""
Марочник сталей и сплавов.
2-е изд., исправл. и доп. / Зубченко А.С., Колосков М.М., Каширский Ю.В. и др. Под ред. А.С. Зубченко.
М.: Машиностроение, 2003. 784 с.
"""
with open("substance/hardness.json", "r") as file:
    data = json.load(file)


def interpolate(x_hardness: str, y_hardness: str, strategy="mean", kind: int = 1):
    # Извлекаем данные в numpy массивы
    x_data = np.array([d[x_hardness] for d in data], dtype="float64")
    y_data = np.array([d[y_hardness] for d in data], dtype="float64")

    x_unique, indices = np.unique(x_data, return_inverse=True)

    # Вычисляем y для каждого уникального x
    if strategy == "mean":
        y_unique = np.array([np.mean(y_data[indices == i]) for i in range(len(x_unique))])
    elif strategy == "median":
        y_unique = np.array([np.median(y_data[indices == i]) for i in range(len(x_unique))])

    # Удаляем NaN значения
    valid = ~np.isnan(y_unique)
    if not np.all(valid):
        x_unique, y_unique = x_unique[valid], y_unique[valid]

    return interp1d(x_unique, y_unique, kind=kind, bounds_error=False, fill_value=nan)


class Hardness:
    """Твердость"""

    __slots__ = ("HB", "HRA", "HRC", "HRB", "HV", "HSD")

    HB_HRA = interpolate("HB", "HRA", kind=1)
    HB_HRC = interpolate("HB", "HRC", kind=1)
    HB_HRB = interpolate("HB", "HRB", kind=1)
    HB_HV = interpolate("HB", "HV", kind=1)
    HB_HSD = interpolate("HB", "HSD", kind=1)

    HRA_HB = interpolate("HRA", "HB", kind=1)
    HRA_HRC = interpolate("HRA", "HRC", kind=1)
    HRA_HRB = interpolate("HRA", "HRB", kind=1)
    HRA_HV = interpolate("HRA", "HV", kind=1)
    HRA_HSD = interpolate("HRA", "HSD", kind=1)

    HRC_HB = interpolate("HRC", "HB", kind=1)
    HRC_HRA = interpolate("HRC", "HRA", kind=1)
    HRC_HRB = interpolate("HRC", "HRB", kind=1)
    HRC_HV = interpolate("HRC", "HV", kind=1)
    HRC_HSD = interpolate("HRC", "HSD", kind=1)

    HRB_HB = interpolate("HRB", "HB", kind=1)
    HRB_HRA = interpolate("HRB", "HRA", kind=1)
    HRB_HRC = interpolate("HRB", "HRC", kind=1)
    HRB_HV = interpolate("HRB", "HV", kind=1)
    HRB_HSD = interpolate("HRB", "HSD", kind=1)

    HV_HB = interpolate("HV", "HB", kind=1)
    HV_HRA = interpolate("HV", "HRA", kind=1)
    HV_HRC = interpolate("HV", "HRC", kind=1)
    HV_HRB = interpolate("HV", "HRB", kind=1)
    HV_HSD = interpolate("HV", "HSD", kind=1)

    HSD_HB = interpolate("HSD", "HB", kind=1)
    HSD_HRA = interpolate("HSD", "HRA", kind=1)
    HSD_HRC = interpolate("HSD", "HRC", kind=1)
    HSD_HRB = interpolate("HSD", "HRB", kind=1)
    HSD_HV = interpolate("HSD", "HV", kind=1)

    @classmethod
    def validate(cls, **hardness: Dict[str, float]):
        """Валидирование твердости"""
        if len(hardness) != 1:
            raise ValueError(f"{len(hardness)=} must be 1")
        for k, v in hardness.items():
            if k not in cls.__slots__:
                raise KeyError(f"{hardness=} not in {cls.__slots__}")
            if not isinstance(v, (float, int)):
                raise TypeError(f"{type(v)=} must be float")

    def __init__(self, **hardness: Dict[str, float]):
        Hardness.validate(**hardness)
        converted = Hardness.convert(**hardness)
        for k, v in converted.items():
            setattr(self, k, v)

    @property
    def values(self) -> Dict[str, float]:
        return {k: getattr(self, k, nan) for k in self.__slots__}

    @classmethod
    def convert(cls, **hardness: Dict[str, float]) -> Dict[str, float]:
        cls.validate(**hardness)
        for k, v in hardness.items():
            match k:
                case "HB":
                    return {
                        "HB": v,
                        "HRA": float(cls.HB_HRA(v)),
                        "HRC": float(cls.HB_HRC(v)),
                        "HRB": float(cls.HB_HRB(v)),
                        "HV": float(cls.HB_HV(v)),
                        "HSD": float(cls.HB_HSD(v)),
                    }
                case "HRA":
                    return {
                        "HB": float(cls.HRA_HB(v)),
                        "HRA": v,
                        "HRC": float(cls.HRA_HRC(v)),
                        "HRB": float(cls.HRA_HRB(v)),
                        "HV": float(cls.HRA_HV(v)),
                        "HSD": float(cls.HRA_HSD(v)),
                    }
                case "HRC":
                    return {
                        "HB": float(cls.HRC_HB(v)),
                        "HRA": float(cls.HRC_HRA(v)),
                        "HRC": v,
                        "HRB": float(cls.HRC_HRB(v)),
                        "HV": float(cls.HRC_HV(v)),
                        "HSD": float(cls.HRC_HSD(v)),
                    }
                case "HRB":
                    return {
                        "HB": float(cls.HRB_HB(v)),
                        "HRA": float(cls.HRB_HRA(v)),
                        "HRC": float(cls.HRB_HRC(v)),
                        "HRB": v,
                        "HV": float(cls.HRB_HV(v)),
                        "HSD": float(cls.HRB_HSD(v)),
                    }
                case "HV":
                    return {
                        "HB": float(cls.HV_HB(v)),
                        "HRA": float(cls.HV_HRA(v)),
                        "HRC": float(cls.HV_HRC(v)),
                        "HRB": float(cls.HV_HRB(v)),
                        "HV": v,
                        "HSD": float(cls.HV_HSD(v)),
                    }
                case "HSD":
                    return {
                        "HB": float(cls.HSD_HB(v)),
                        "HRA": float(cls.HSD_HRA(v)),
                        "HRC": float(cls.HSD_HRC(v)),
                        "HRB": float(cls.HSD_HRB(v)),
                        "HV": float(cls.HSD_HV(v)),
                        "HSD": v,
                    }
                case _:
                    raise KeyError(f"{hardness=} not in {cls.__slots__}")


if __name__ == "__main__":
    h = Hardness(HB=229)
    print(h.values)
    print(Hardness.convert(HB=229))
