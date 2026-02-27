package substance

import (
	"errors"
	"fmt"
	"math"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

var units = []string{
	// СИ
	"m", "kg", "s", "A", "K", "mol", "cd",
	// Производные СИ
	"Pa", // TODO: add
}

var Prefixes = map[string]float64{
	"q":  1e-30, // квекто
	"r":  1e-27, // ронто
	"y":  1e-24, // иокто
	"z":  1e-21, // зепто
	"a":  1e-18, // атто
	"f":  1e-15, // фемто
	"p":  1e-12, // пико
	"n":  1e-9,  // нано
	"μ":  1e-6,  // микро
	"m":  1e-3,  // милли
	"c":  1e-2,  // санти
	"d":  1e-1,  // деци
	"":   1.0,
	"da": 1e+1,  // дека
	"h":  1e+2,  // гекто
	"k":  1e+3,  // кило
	"M":  1e+6,  // мега
	"G":  1e+9,  // гига
	"T":  1e+12, // тера
	"P":  1e+15, // пета
	"E":  1e+18, // экса
	"Z":  1e+21, // зетта
	"Y":  1e+24, // иотта
	"R":  1e+27, // ронна
	"Q":  1e+30, // кветта
}

var (
	emptyName      = errors.New("empty name")
	invalidUnitErr = errors.New("invalid unit format")
)

// regex для разбора единиц измерения
var (
	// Паттерн для операций: * /
	operationPattern = regexp.MustCompile(`[*/]`)
	// Паттерн для степени
	powerPattern = regexp.MustCompile(`\^(\d+)`)
)

// isNumeric проверяет, является ли строка числом
func isNumeric(s string) bool {
	_, err := strconv.ParseFloat(s, 64)
	return err == nil
}

// calculateMultiplier вычисляет множитель для перевода в СИ на основе строки единицы измерения
func calculateMultiplier(unit string) (float64, error) {
	if unit == "" {
		return 1.0, nil
	}

	// Удаляем пробелы
	unit = strings.ReplaceAll(unit, " ", "")

	// Сначала обрабатываем степени
	unit = processPowers(unit)

	// Разбиваем на токены по операторам * и /
	tokens := splitByOperators(unit)

	multiplier := 1.0
	for i := 0; i < len(tokens); i++ {
		token := tokens[i]

		// Определяем оператор перед токеном
		op := "+"
		if strings.HasPrefix(token, "*") {
			op = "*"
			token = token[1:]
		} else if strings.HasPrefix(token, "/") {
			op = "/"
			token = token[1:]
		}

		// Проверяем, является ли токен числом
		if isNumeric(token) {
			continue
		}

		// Обрабатываем степень (цифры в конце)
		baseToken, power := extractPower(token)

		// Получаем множитель для базовой единицы
		unitMultiplier, err := parseUnitWithPrefix(baseToken)
		if err != nil {
			return 0, fmt.Errorf("%w: %s", invalidUnitErr, token)
		}

		// Применяем степень
		effectiveMultiplier := math.Pow(unitMultiplier, power)

		// Применяем оператор
		switch op {
		case "+", "*":
			multiplier *= effectiveMultiplier
		case "/":
			multiplier /= effectiveMultiplier
		}
	}

	return multiplier, nil
}

// processPowers обрабатывает выражения со степенью (например, km^2 -> km2)
func processPowers(unit string) string {
	// Ищем все вхождения ^число и заменяем на число без ^
	return powerPattern.ReplaceAllStringFunc(unit, func(match string) string {
		// Извлекаем число после ^
		number := match[1:] // убираем ^
		return number
	})
}

// extractPower извлекает степень из токена (например, "m2" -> ("m", 2), "km2" -> ("km", 2))
func extractPower(token string) (string, float64) {
	// Ищем цифры в конце строки
	re := regexp.MustCompile(`^(.+?)(\d+)$`)
	matches := re.FindStringSubmatch(token)
	if len(matches) == 3 {
		base := matches[1]
		power, _ := strconv.ParseFloat(matches[2], 64)
		return base, power
	}

	// Степень не найдена
	return token, 1.0
}

// splitByOperators разбивает строку единицы на токены с сохранением операторов * и /
func splitByOperators(unit string) []string {
	if !operationPattern.MatchString(unit) {
		return []string{unit}
	}

	var tokens []string
	current := ""
	for i, r := range unit {
		ch := string(r)
		if ch == "*" || ch == "/" {
			if current != "" {
				tokens = append(tokens, current)
			}
			current = ch
		} else {
			if i > 0 && (string(unit[i-1]) == "*" || string(unit[i-1]) == "/") {
				current += ch
			} else if current == "" || (current != "*" && current != "/") {
				current += ch
			} else {
				tokens = append(tokens, current)
				current = string(ch)
			}
		}
	}
	if current != "" {
		tokens = append(tokens, current)
	}

	return tokens
}

// parseUnitWithPrefix разбирает единицу измерения с возможной приставкой
func parseUnitWithPrefix(unit string) (float64, error) {
	// Специальная обработка для граммов
	if unit == "g" { // Грамм - это 0.001 кг (базовой единицы СИ для массы)
		return 0.001, nil
	}
	if unit == "h" {
		return 3600, nil
	}

	// Сортируем приставки по длине (от самой длинной к короткой)
	prefixes := make([]string, 0, len(Prefixes))
	for p := range Prefixes {
		if p != "" {
			prefixes = append(prefixes, p)
		}
	}
	sort.Slice(prefixes, func(i, j int) bool {
		return len(prefixes[i]) > len(prefixes[j])
	})

	// Ищем приставку
	for _, p := range prefixes {
		if strings.HasPrefix(unit, p) {
			remaining := unit[len(p):]

			// Проверяем, является ли оставшаяся часть базовой единицей СИ
			for _, u := range units {
				if remaining == u {
					// Нашли соответствие
					if val, ok := Prefixes[p]; ok {
						return val, nil
					}
				}
			}

			// Специальный случай: если остаток - это "g" (граммы)
			if remaining == "g" {
				if val, ok := Prefixes[p]; ok {
					// Для граммов нужно умножить приставку на 0.001
					return val * 0.001, nil
				}
			}
		}
	}

	// Проверяем, является ли сама единица базовой
	for _, u := range units {
		if unit == u {
			return 1.0, nil
		}
	}

	return 0, fmt.Errorf("unknown unit: %s", unit)
}

// Parameter - параметр вещества.
type Parameter struct {
	Name        string  `doc:"Имя"`
	Value       float64 `doc:"Значение"`
	Unit        string  `doc:"CИ"`
	Multiplier  float64 `doc:"Множитель СИ"`
	ValueUnit   float64 `doc:"Значение в СИ"`
	Description string  `doc:"Описание"`
}

// Конструктор Parameter.
func NewParameter(name string, value float64, unit string, description string) (Parameter, error) {
	if name == "" {
		return Parameter{}, emptyName
	}

	multiplier, err := calculateMultiplier(unit)
	if err != nil {
		return Parameter{}, err
	}

	return Parameter{
		Name:        name,
		Value:       value,
		Unit:        unit,
		Multiplier:  multiplier,
		ValueUnit:   value * multiplier,
		Description: description,
	}, nil
}

// Возвращение значения в СИ.
func (p *Parameter) Get() float64 {
	return p.ValueUnit
}

// Substance - Вещество.
type Substance struct {
	Name       string                                        `doc:"Имя"`
	Parameters map[string]Parameter                          `doc:"Параметры"`
	Functions  map[string]func(map[string]Parameter) float64 `doc:"Функции"`
}

// Конструктор Substance.
func NewSubstance(name string, parameters map[string]Parameter, functions map[string]func(map[string]Parameter) float64) (Substance, error) {
	if name == "" {
		return Substance{}, emptyName
	}
	return Substance{Name: name, Parameters: parameters, Functions: functions}, nil
}
