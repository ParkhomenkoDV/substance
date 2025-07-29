import os
from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from colorama import Fore
from decorators import ignore_extra_kwargs  # игнорирование лишних именных аргументов
from numpy import arange, array, isnan, linspace, nan, sqrt
from scipy import interpolate
from thermodynamics import T0
from thermodynamics import parameters as tdp  # termodynamic parameters

# Список использованной литературы
REFERENCES = {
    1: """Марочник сталей и сплавов.
    2-е изд., исправл. и доп. / Зубченко А.С., Колосков М.М., Каширский Ю.В. и др. Под ред. А.С. Зубченко.
    М.: Машиностроение, 2003. 784 с.""",
    2: """Справочник по конструкционным материалам:
    Справочник / Б.Н. Арзамасов, Т.В. Соловьева, С.А. Герасимов и др.;
    Под ред. Б.Н. Арзамасова, Т.В. Соловьевой.
    - М.: Изд-во МГТУ им Н.Э. Баумана, 2006. с.: ил.""",
}

M = 10**6  # приставка Мега
HERE = os.path.dirname(__file__)  # путь к текущему файлу

hardness = pd.read_excel(os.path.join(HERE, "hardness.xlsx")).drop(
    ["d10mm"], axis=1
)  # [1, c.784]


class Substance:
    """Вещество"""

    __slots__ = (  # запрет других атрибутов + ускорение
        "name",  # имя
        "composition",  # химический состав
        "parameters",  # параметры
    )

    def __init__(
        self, name: str, composition: dict[str, float] = None, parameters: dict = None
    ) -> None:
        """
        Инициализация вещества.

        Args:
            name: Название вещества
            composition: Химический состав (элемент: доля)
            parameters: Физические параметры (название: значение/функция)
        """
        self.name: str = name
        self.composition: dict = composition or {}
        self.parameters: dict = parameters or {}

    def __validate_attribute(self, attribute: str, value: str | dict) -> str | dict:
        """Валидирование атрибутов"""
        assert isinstance(attribute, str), TypeError(f"{attribute} must be str")
        match attribute:
            case "name":
                assert isinstance(value, str), TypeError(f"{attribute} must be a str")
                return value
            case "composition":
                assert isinstance(value, dict), TypeError(f"{attribute} must be a dict")
                return self.__validate_composition(value)
            case "parameters":
                assert isinstance(value, dict), TypeError(f"{attribute} must be a dict")
                validated = {}
                for parameter, v in value.items():
                    assert isinstance(parameter, str), f"{parameter} must be a str"
                    validated[parameter] = self.__validate_parameter(parameter, v)
                return validated
            case _:
                raise AttributeError(f"{attribute} not in {self.__slots__}")

    def __validate_composition(self, composition: dict) -> dict[str:float]:
        for element, fraction in composition.items():
            assert isinstance(element, str), TypeError(
                "Composition elements must be strings"
            )
            assert isinstance(fraction, (int, float, np.number)), TypeError(
                "Composition fractions must be numeric"
            )
            assert fraction >= 0, ValueError("Composition values must be >= 0")
        total = sum(composition.values())  # общая масса
        return {k: v / total for k, v in composition.items()}

    def __validate_parameter(self, name: str, value) -> callable:
        """Валидация значения параметра"""
        if callable(value):
            return ignore_extra_kwargs(value)
        elif isinstance(value, (int, float, np.number)):
            return ignore_extra_kwargs(lambda *_, **__: float(value))
        else:
            raise TypeError(f"Parameter {name} value must be numeric or callable")

    def __setattr__(self, key: str, value):
        value = self.__validate_attribute(key, value)
        object.__setattr__(self, key, value)

    def __delattr__(self, key) -> None:
        if key == "name":
            raise Exception("Deleting forbidden!")
        elif key in self.parameters:
            del self.parameters[key]

    def __getitem__(self, key):
        return self.parameters.get(key, lambda *args, **kwargs: nan)

    def __setitem__(self, key, value) -> None:
        value = self.__validate_parameter(key, value)
        self.parameters[key] = value

    def __delitem__(self, key) -> None:
        del self.parameters[key]

    def __deepcopy__(self, memo):
        """
        Создает глубокую копию объекта Substance.
        Обрабатывает:
        - Копирование строки name
        - Рекурсивное копирование словарей composition и parameters
        - Корректную обработку callable-объектов в parameters
        """

        new_obj = Substance.__new__(Substance)  # новый экземпляр без вызова __init__

        # Копируем простые атрибуты в memo для предотвращения циклических ссылок
        memo[id(self)] = new_obj

        # Глубокое копирование каждого атрибута
        new_obj.name = deepcopy(self.name, memo)

        # Особое внимание словарям
        new_obj.composition = {
            k: deepcopy(v, memo) for k, v in self.composition.items()
        }

        new_obj.parameters = {}
        for k, v in self.parameters.items():
            if callable(v):
                new_obj.parameters[k] = v
            else:
                new_obj.parameters[k] = deepcopy(v, memo)

        return new_obj

    '''
    def __add__(self, other):
    """Смешение веществ"""
    assert isinstance(other, Substance)
    composition = self.composition.copy()
    for el in other.composition.keys():
        if el not in composition:
            composition[el] = other.composition[el]
        else:
            composition[el] += other.composition[el]

    return Substance(composition)
    '''

    @staticmethod
    def jung(**kwargs) -> float:
        """Модуль Юнга I и II рода"""
        mu = kwargs.pop("mu", None)
        E = kwargs.pop("E", None)
        G = kwargs.pop("G", None)
        assert isinstance(mu, (float, int, np.number)) and 0 < mu
        if isinstance(E, (float, int, np.number)):
            assert 0 < E
            return E / (2 * (mu + 1))
        elif isinstance(G, (float, int, np.number)):
            assert 0 < G
            return 2 * G * (mu + 1)
        else:
            raise Exception(
                "isinstance(E, (float, int, np.number)) or isinstance(G, (float, int, np.number))"
            )

    @property
    def excess_oxidizing(self) -> float:
        """Коэффициент избытка окислителя"""
        oxidizing = self.composition.get("O", 0)
        total = sum(self.composition.values())
        total = nan if total == 0 else total
        return oxidizing / total


class Material:
    __PARAMETERS = {
        "density": {
            "description": "плотность",
            "unit": "[кг/м^3]",
            "type": (int, float, np.number),
            "assert": (lambda density: "" if 0 < density else f"0 < density",),
        },
        "alpha": {
            "description": "коэффициент линейного расширения",
            "unit": "[1/К]",
            "type": (int, float, np.number),
            "assert": (lambda alpha: "" if 0 <= alpha else f"0 <= alpha",),
        },
        "E": {
            "description": "модуль Юнга I рода",
            "unit": "[Па]",
            "type": (int, float, np.number),
            "assert": (lambda E: "" if 0 < E else f"0 < E",),
        },
        "G": {
            "description": "модуль (сдвига) Юнга II рода",
            "unit": "[Па]",
            "type": (int, float, np.number),
            "assert": (lambda G: "" if 0 < G else f"0 < G",),
        },
        "mu": {
            "description": "коэффициент Пуассона",
            "unit": "[]",
            "type": (int, float, np.number),
            "assert": (lambda mu: "" if 0 < mu else f"0 < mu",),
        },
        "sigma_t": {
            "description": "предел текучести",
            "unit": "[Па]",
            "type": (int, float, np.number),
            "assert": (lambda sigma_t: "" if 0 < sigma_t else f"0 < sigma_t",),
        },
        "sigma_s": {
            "description": "предел прочности",
            "unit": "[Па]",
            "type": (int, float, np.number),
            "assert": (lambda sigma_s: "" if 0 < sigma_s else f"0 < sigma_s",),
        },
        "l": {
            "description": "теплопроводность",
            "unit": "[Вт/м/К]",
            "type": (int, float, np.number),
            "assert": (lambda l: "" if 0 < l else f"0 < l",),
        },
        "C": {
            "description": "теплоемкость",
            "unit": "[Дж/К]",
            "type": (int, float, np.number),
            "assert": (lambda C: "" if 0 < C else f"0 < C",),
        },
        "c": {
            "description": "удельная теплоемкость",
            "unit": "[Дж/кг/К]",
            "type": (int, float, np.number),
            "assert": (lambda c: "" if 0 < c else f"0 < c",),
        },
        "KCU": {
            "description": "ударная вязкость",
            "unit": "[Дж/м^2]",
            "type": (int, float, np.number),
            "assert": (lambda KCU: "" if 0 < KCU else f"0 < KCU",),
        },
        "HB": {
            "description": "твердость по Бринеллю",
            "unit": "[Па]",
            "type": (int, float, np.number),
            "assert": (lambda HB: "" if 0 < HB else f"0 < HB",),
        },
        "HRC": {
            "description": "твердость по Роквеллу",
            "unit": "[Па]",
            "type": (int, float, np.number),
            "assert": (lambda HRC: "" if 0 < HRC else f"0 < HRC",),
        },
        "HV": {
            "description": "твердость по Виккерсу",
            "unit": "[Па]",
            "type": (int, float, np.number),
            "assert": (lambda HV: "" if 0 < HV else f"0 < HV",),
        },
        "*": {
            "description": "частный параметр",
            "unit": "[...]",
            "type": (int, float, np.number, str, bool),
            "assert": tuple(),
        },
    }

    @classmethod
    def help(cls):
        print(Fore.CYAN + "Material parameters:" + Fore.RESET)
        print(
            Fore.RED
            + "type value must be int, float, array with shape (-1,2) or callable(int | float)"
            + Fore.RESET
        )
        for parameter, d in Material.__PARAMETERS.items():
            print("\t\t" + Fore.CYAN + f"{parameter}" + Fore.RESET)
            for key, value in d.items():
                print("\t\t\t" + f"{key}: {value}")

    def __init__(
        self,
        name: str,
        parameters: dict,
        composition=None,
        reference: str = "",
        kind: int = 1,
        fill_value=nan,
    ) -> None:
        assert isinstance(name, str)
        self.__name = name

        assert isinstance(kind, int) and 0 <= kind <= 3
        assert isnan(fill_value) or fill_value == "extrapolate"

        assert isinstance(parameters, dict)
        assert all(isinstance(el, str) for el in parameters.keys())  # все ключи - стоки

        for (
            parameter,
            value,
        ) in parameters.items():  # есть возможность создавать свои свойства
            if isinstance(value, (int, float)):  # const
                setattr(
                    self,
                    parameter,
                    interpolate.interp1d(
                        (273.15,),
                        (value,),
                        kind=0,  # для константы надо 0
                        bounds_error=False,
                        fill_value="extrapolate",
                    ),
                )
            elif isinstance(value, (tuple, list, np.ndarray)):  # таблица значений
                value = array(value).T
                assert (
                    len(value.shape) == 2 and value.shape[0] == 2 and value.shape[1] > 3
                )
                setattr(
                    self,
                    parameter,
                    interpolate.interp1d(
                        value[0],
                        value[1],
                        kind=kind,
                        bounds_error=False,
                        fill_value=fill_value,
                    ),
                )
            elif callable(value):  # функция
                try:
                    value(273.15)  # проверка на вызов от численного значения
                    setattr(self, parameter, value)
                except Exception:
                    print(f'parameter "{parameter}" has not callable value!')
            else:
                raise Exception(
                    "type of values parameters is in (int, float) or callable(int, float)"
                )

        if composition is None:
            self.composition = composition
        elif isinstance(composition, dict):
            assert all(isinstance(el, str) for el in composition.keys())
            assert all(isinstance(el, (float, int)) for el in composition.values())
            assert all(0 <= el <= 1 for el in composition.values())
            self.composition = composition
        else:
            raise ValueError("type(composition) must be dict!")

        assert isinstance(reference, str)
        self.reference = reference

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        assert isinstance(name, str)
        self.__name = name

    @staticmethod
    def jung(**kwargs) -> float:
        """Модуль Юнга I и II рода"""
        mu = kwargs.pop("mu", None)
        E = kwargs.pop("E", None)
        G = kwargs.pop("G", None)
        assert isinstance(mu, (float, int, np.number)) and 0 < mu
        if isinstance(E, (float, int, np.number)):
            assert 0 < E
            return E / (2 * (mu + 1))
        elif isinstance(G, (float, int, np.number)):
            assert 0 < G
            return 2 * G * (mu + 1)
        else:
            raise Exception(
                "isinstance(E, (float, int, np.number)) or isinstance(G, (float, int, np.number))"
            )

    @staticmethod
    def hardness(h: str, value: float | int | np.number) -> dict[str:float]:
        """Перевод твердости"""
        assert h in hardness.columns, hardness.columns
        assert isinstance(value, (float, int, np.number)) and 0 <= value
        group = hardness.groupby(h).mean()  # замена дубликатов их средним значением
        result = dict()
        for column in group.columns:
            temp = group.dropna(subset=column)  # удаление nan
            func = interpolate.interp1d(
                temp.index, temp[column], kind=3, fill_value=nan, bounds_error=False
            )
            result[column] = float(func(value))
        return result

    def show(self, temperature: tuple | list | np.ndarray, **kwargs) -> None:
        assert isinstance(temperature, (tuple, list, np.ndarray))
        parameters = [k for k, v in self.__dict__.items() if callable(v)]

        fg = plt.figure(figsize=kwargs.pop("figsize", (4 * len(parameters), 8)))
        fg.suptitle(self.__name, fontsize=16, fontweight="bold")
        gs = fg.add_gridspec(1, len(parameters))  # строки, столбцы

        for i, param in enumerate(parameters):
            if not hasattr(self, param):
                continue
            xy = array(
                [
                    (t, getattr(self, param)(t))
                    for t in linspace(
                        temperature[0], temperature[-1], 1_000, endpoint=True
                    )
                    if not isnan(getattr(self, param)(t))
                ]
            )
            fg.add_subplot(gs[0, i])
            plt.grid(True)
            (plt.xlim(temperature[0], temperature[-1]),)
            plt.xticks(temperature)
            plt.xlabel("temperature", fontsize=12)
            plt.ylabel(param, fontsize=12)
            plt.plot(*xy.T, color="black")

        plt.show()


materials = list()

materials.append(
    Material(
        "ХН70МВТЮБ",
        {
            "sigma_s": array(
                (
                    array((20, 600, 700, 800, 850, 900)) + T0,
                    array((1060, 980, 930, 720, 600, 380)) * 10**6,
                )
            ).T,
            "sigma_t": array(
                (
                    array((20, 600, 700, 800, 850, 900)) + T0,
                    array((560, 550, 530, 450, 400, 220)) * 10**6,
                )
            ).T,
            "KCU": array(
                (
                    array((700, 750, 800, 850)) + 273.15,
                    array((0.8, 0.7, 0.6, 0.7)) * 10**6,
                )
            ).T,
            "sigma_100": array(
                (array((650, 700, 800, 850)) + T0, array((620, 480, 250, 180)) * 10**6)
            ).T,
            "sigma_200": array(
                (array((650, 700, 800, 850)) + T0, array((600, 420, 230, 230)) * 10**6)
            ).T,
        },
        reference=REFERENCES[2] + ", c. 412-413",
    )
)
materials.append(
    Material(
        "ХН80ТБЮ",
        {
            "sigma_s": array(
                (
                    array((29, 500, 600, 630, 650, 700)) + T0,
                    array((960, 1000, 830, 790, 700, 680)) * M,
                )
            ).T,
            "sigma_t": array(
                (
                    array((29, 500, 600, 630, 650, 700)) + T0,
                    array((650, 610, 600, 600, 550, 500)),
                )
            ).T,
            "KCU": interpolate.interp1d(
                array((29, 650, 700)) + T0,
                array((0.7, 1.0, 1.2)) * M,
                kind=2,
                bounds_error=False,
                fill_value="extrapolate",
            ),
            "sigma_1000": interpolate.interp1d(
                array((650, 700)) + T0,
                array((450, 280)) * M,
                kind=1,
                bounds_error=False,
                fill_value=nan,
            ),
            "sigma_5000": interpolate.interp1d(
                array((650, 700)) + T0,
                array((320, 220)) * M,
                kind=1,
                bounds_error=False,
                fill_value=nan,
            ),
            "sigma_10000": interpolate.interp1d(
                array((650, 700)) + T0,
                array((280, 170)) * M,
                kind=1,
                bounds_error=False,
                fill_value=nan,
            ),
        },
        reference=REFERENCES[2] + ", c. 413",
    )
)
materials.append(
    Material(
        "ХН70ВМТЮ",
        {
            "sigma_s": array(
                (
                    array((20, 500, 600, 650, 700, 750, 800, 900, 950, 1000)) + T0,
                    array((1030, 1020, 970, 990, 890, 710, 570, 300, 140, 80)) * M,
                )
            ).T,
            "sigma_t": array(
                (
                    array((20, 500, 600, 650, 700, 750, 800, 900, 950, 1000)) + T0,
                    array((670, 640, 600, 600, 580, 580, 500, 280, 120, 70)) * M,
                )
            ).T,
            "KCU": array(
                (
                    array((20, 500, 600, 650, 700, 750, 800)) + T0,
                    array((0.8, 0.9, 0.9, 0.8, 0.9, 0.85, 1.05)) * M,
                )
            ).T,
            "sigma_100": interpolate.interp1d(
                array((750, 800)) + T0,
                array((360, 240)) * M,
                kind=1,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_1000": interpolate.interp1d(
                array((600, 650, 700, 750, 800)) + T0,
                array((650, 550, 310, 250, 175)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_2000": interpolate.interp1d(
                array((600, 650, 700, 750)) + T0,
                array((600, 400, 270, 200)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_3000": interpolate.interp1d(
                array((650, 750, 800)) + T0,
                array((470, 215, 145)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_5000": interpolate.interp1d(
                array((600, 650, 750, 800)) + T0,
                array((560, 440, 185, 130)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_10000": interpolate.interp1d(
                array((600, 650, 750, 800)) + T0,
                array((530, 385, 170, 125)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_20000": interpolate.interp1d(
                array((600, 650, 750)) + T0,
                array((500, 340, 190)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 414-415",
    )
)
materials.append(
    Material(
        "ХН55ВМКЮ",
        {
            "sigma_s": array(
                (
                    array((20, 700, 750, 800, 850, 900, 950, 1000)) + T0,
                    array((1100, 1080, 1080, 1000, 750, 650, 550, 350)) * M,
                )
            ).T,
            "sigma_t": array(
                (
                    array((20, 700, 750, 800, 850, 900, 950, 1000)) + T0,
                    array((750, 750, 750, 700, 650, 500, 400, 250)) * M,
                )
            ).T,
            "KCU": array(
                (
                    array((20, 700, 750, 800, 850, 900, 950, 1000)) + T0,
                    array((0.2, 0.3, 0.3, 0.3, 0.3, 0.4, 0.4, 0.4)) * M,
                )
            ).T,
            "sigma_100": interpolate.interp1d(
                array((800, 900, 950)) + T0,
                array((440, 240, 140)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_1000": interpolate.interp1d(
                array((800, 900, 950)) + T0,
                array((310, 130, 65)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_2000": interpolate.interp1d(
                array((800, 900, 950)) + T0,
                array((290, 100, 55)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 415",
    )
)
materials.append(
    Material(
        "10Х18Н9Т",
        {
            "sigma_s": array(
                (
                    array((20, 650, 800, 900, 1000, 1100)) + T0,
                    array((554, 320, 185, 91, 55, 38)) * M,
                )
            ).T,
            "KCU": array(
                (
                    array((20, 650, 800, 900, 1000, 1100)) + T0,
                    array((1.25, 1.96, 2.59, 2.36, 2.06, 1.51)) * M,
                )
            ).T,
            "sigma_100000": interpolate.interp1d(
                array((600, 650, 700)) + T0,
                array((110, 70, 45)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 402",
    )
)
materials.append(
    Material(
        "08Х18Н12М3Т",
        {
            "sigma_1": interpolate.interp1d(
                array((650, 700, 760, 815, 870, 980)) + T0,
                array((350, 270, 210, 145, 120, 58)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_10": interpolate.interp1d(
                array((650, 700, 760, 815, 870, 980)) + T0,
                array((270, 210, 145, 105, 77, 35)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_100": interpolate.interp1d(
                array((650, 700, 760, 815, 870, 980)) + T0,
                array((220, 164, 110, 77, 52, 19)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_300": interpolate.interp1d(
                array((650, 700, 760, 815, 870, 980)) + T0,
                array((196, 155, 83, 66, 42, 13)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_500": interpolate.interp1d(
                array((650, 700, 760, 815, 870, 980)) + T0,
                array((189, 140, 84, 61, 39, 10)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_1000": interpolate.interp1d(
                array((650, 700, 760, 815, 870, 980)) + T0,
                array((182, 126, 73, 49, 30, 8.4)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_10000": interpolate.interp1d(
                array((650, 700, 760, 815)) + T0,
                array((140, 84, 49, 23)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_100000": interpolate.interp1d(
                array((650, 700, 760, 815)) + T0,
                array((112, 62, 30, 11)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 402",
    )
)
materials.append(
    Material(
        "40Х15Н7ГФ2МС",
        {
            "sigma_s": interpolate.interp1d(
                array((20, 300, 400, 500, 600, 700, 800, 900, 1000)) + T0,
                array((1000, 810, 780, 700, 640, 520, 380, 250, 160)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_t": interpolate.interp1d(
                array((20, 300, 400, 500, 600, 700, 800)) + T0,
                array((600, 550, 540, 490, 500, 430, 280)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_100": interpolate.interp1d(
                array((600, 700, 800, 900)) + T0,
                array((430, 250, 130, 75)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_1000": interpolate.interp1d(
                array((600, 700, 800)) + T0,
                array((320, 180, 84)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_10000": interpolate.interp1d(
                array((600, 700, 800)) + T0,
                array((250, 110, 50)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 406-407",
    )
)
materials.append(
    Material(
        "37Х12Н8Г8МФБ",
        {
            "sigma_s": interpolate.interp1d(
                array((20, 200, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750)) + T0,
                array((1000, 770, 740, 730, 730, 720, 680, 660, 600, 560, 500, 420))
                * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_t": interpolate.interp1d(
                array((20, 200, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750)) + T0,
                array((600, 600, 540, 520, 500, 500, 500, 490, 490, 450, 430, 380)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_100": interpolate.interp1d(
                array((600, 650, 700)) + T0,
                array((450, 370, 310)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_1000": interpolate.interp1d(
                array((600, 650, 700)) + T0,
                array((340, 250, 230)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_5000": interpolate.interp1d(
                array((600, 650, 700)) + T0,
                array((310, 220, 190)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_10000": interpolate.interp1d(
                array((600, 650, 700)) + T0,
                array((300, 210, 180)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 407",
    )
)
materials.append(
    Material(
        "08Х16Н13М2Б",
        {
            "sigma_s": interpolate.interp1d(
                array((20, 500, 600, 650)) + T0,
                array((620, 490, 470, 440)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_t": interpolate.interp1d(
                array((20, 500, 600, 650)) + T0,
                array((230, 175, 175, 175)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_10000": interpolate.interp1d(
                array((550, 600, 650, 700)) + T0,
                array((260, 200, 130, 60)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_100000": interpolate.interp1d(
                array((550, 600, 650, 700)) + T0,
                array((210, 150, 95, 35)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "alpha": interpolate.interp1d(
                array((400, 600, 800)) + T0,
                array((17.1, 17.8, 18.6)) / M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "E": interpolate.interp1d(
                array((20, 200, 400, 600, 650)) + T0,
                array((206, 191, 174, 167, 158)) * 10**9,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "l": interpolate.interp1d(
                array((200, 400, 600, 650, 700)) + T0,
                array((17.1, 20.1, 21.7, 23.0, 24.7)),
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 408",
    )
)
materials.append(
    Material(
        "09Х14Н16Б",
        {
            "sigma_s": interpolate.interp1d(
                array((20, 600, 650, 700)) + T0,
                array((570, 400, 360, 330)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_t": interpolate.interp1d(
                array((20, 600, 650, 700)) + T0,
                array((250, 188, 160, 160)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "KCU": interpolate.interp1d(
                array((20, 600, 700)) + T0,
                array((2.1, 3.3, 3.3)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_10000": interpolate.interp1d(
                array((600, 650, 700)) + T0,
                array((170, 110, 65)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_100000": interpolate.interp1d(
                array((600, 650, 700)) + T0,
                array((120, 77, 40)) * M,
                kind=2,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 409",
    )
)
materials.append(
    Material(
        "10Х11Н20Т3Р",
        {
            "sigma_s": interpolate.interp1d(
                array((20, 400, 600, 700, 750, 800)) + T0,
                array((1000, 950, 800, 680, 560, 360)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_t": interpolate.interp1d(
                array((20, 400, 600, 700, 750, 800)) + T0,
                array((600, 600, 530, 470, 450, 250)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_100": interpolate.interp1d(
                array((500, 550, 600, 650, 700, 750)) + T0,
                array((730, 650, 590, 480, 400, 280)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 409-410",
    )
)
materials.append(
    Material(
        "09Х14Н19В2БР",
        {
            "sigma_s": interpolate.interp1d(
                array((20, 600, 650, 700)) + T0,
                array((570, 440, 430, 410)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_t": interpolate.interp1d(
                array((20, 600, 650, 700)) + T0,
                array((230, 140, 140, 140)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "KCU": interpolate.interp1d(
                array((20, 600, 650, 700)) + T0,
                array((1.8, 2.2, 2.1, 2.2)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_10000": interpolate.interp1d(
                array((600, 650, 700, 750)) + T0,
                array((270, 168, 125, 70)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_100000": interpolate.interp1d(
                array((600, 650, 700, 750)) + T0,
                array((200, 130, 95, 55)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "E": interpolate.interp1d(
                array((20, 100, 200, 300, 400, 500, 600, 700)) + T0,
                array((202, 199, 193, 186, 178, 168, 160, 152)) * 10**9,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "l": interpolate.interp1d(
                array((20, 100, 200, 300, 400, 500, 600, 700, 800)) + T0,
                array((15.4, 16.3, 16.3, 18.0, 19.2, 21.3, 23.4, 25.1, 27.6)),
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "alpha": interpolate.interp1d(
                array((100, 200, 300, 400, 500, 600, 700, 800)) + T0,
                array((15.2, 16.3, 16.9, 17.5, 17.8, 18.1, 18.6, 18.6)) / M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 410",
    )
)
materials.append(
    Material(
        "08Х15Н24В4ТР",
        {
            "sigma_s": interpolate.interp1d(
                array((20, 650, 700, 750)) + T0,
                array((750, 650, 600, 500)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_t": interpolate.interp1d(
                array((20, 650, 700, 750)) + T0,
                array((500, 450, 400, 350)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "KCU": interpolate.interp1d(
                array((20, 650, 700, 750)) + T0,
                array((1.2, 1.01, 1.0, 0.1)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_1000": interpolate.interp1d(
                array((600, 650, 700, 750)) + T0,
                array((500, 400, 250, 180)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_10000": interpolate.interp1d(
                array((600, 650, 700, 750)) + T0,
                array((400, 200, 180, 120)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
            "sigma_100000": interpolate.interp1d(
                array((600, 650, 700, 750)) + T0,
                array((300, 230, 140, 80)) * M,
                kind=3,
                fill_value=nan,
                bounds_error=False,
            ),
        },
        reference=REFERENCES[2] + ", c. 410",
    )
)


def main():
    """Тестирование"""
    Material.help()

    material = Material(
        "test",  # тестируемый материал
        {
            "density": 8400,  # int
            "alpha": interpolate.interp1d(
                (400, 600, 800),
                array((18, 18, 18)) * 10**-6,
                kind=1,
                bounds_error=False,
                fill_value="extrapolate",
            ),
            "E": interpolate.interp1d(
                arange(400, 800 + 1, 100),
                array([1.74, 1.66, 1.57, 1.47, 1.32]) * 10**11,
                kind=3,
                bounds_error=False,
                fill_value=nan,
            ),
            "mu": interpolate.interp1d(
                arange(400, 800 + 1, 100),
                (0.384, 0.379, 0.371, 0.361, 0.347),
                kind=3,
                bounds_error=False,
                fill_value="extrapolate",
            ),
            "c": lambda t: 4200,  # lambda
            "l": ((0, 16), (100, 18), (200, 19), (400, 19.5)),  # tuple
            "HV": array(((0, 16), (100, 18), (200, 19), (400, 19.5))),  # array
            "smth": 3.1415,  # float
        },
    )
    materials.insert(0, material)

    temperature, t = arange(200, 1_200 + 1, 50), 700
    for material in materials:
        print(Fore.MAGENTA + material.name + Fore.RESET)
        for k, v in material.__dict__.items():
            if callable(v):
                print("\t" + f"{k}({t}): {v(t)}")
        material.show(temperature)

    for column in hardness.columns:
        for h in range(0, 1_000 + 1, 10):
            print(f'"{column}": {h}, {Material.hardness(column, h)}')
