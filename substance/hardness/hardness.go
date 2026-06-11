package hardness

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"math"
	"os"
	"slices"
	"sort"

	"gonum.org/v1/gonum/interp"
	"gonum.org/v1/gonum/stat"
)

// newInterpolator создаёт новый интерполятор из данных
func newInterpolator(xData, yData []float64) (*interp.PiecewiseLinear, error) {
	// Фильтруем NaN значения
	filteredX, filteredY := make([]float64, 0), make([]float64, 0)
	for i := range xData {
		if !math.IsNaN(xData[i]) && !math.IsNaN(yData[i]) {
			filteredX = append(filteredX, xData[i])
			filteredY = append(filteredY, yData[i])
		}
	}

	if len(filteredX) < 2 {
		return nil, fmt.Errorf("недостаточно данных для интерполяции: %d точек", len(filteredX))
	}

	// Группируем по уникальным X и агрегируем Y
	uniqueX, aggregatedY := aggregateByX(filteredX, filteredY)

	// Сортируем по X
	sort.Sort(byX{uniqueX, aggregatedY})

	// Используем PiecewiseLinear из gonum для линейной интерполяции
	var pl interp.PiecewiseLinear
	err := pl.Fit(uniqueX, aggregatedY)
	if err != nil {
		return nil, fmt.Errorf("ошибка fitting интерполятора: %w", err)
	}

	return &pl, nil
}

// aggregateByX группирует данные по уникальным X и агрегирует Y
func aggregateByX(xData, yData []float64) ([]float64, []float64) {
	// Создаём карту для группировки
	groups := make(map[float64][]float64)
	for i := range xData {
		groups[xData[i]] = append(groups[xData[i]], yData[i])
	}

	uniqueX := make([]float64, 0, len(groups))
	aggregatedY := make([]float64, 0, len(groups))

	for x, yValues := range groups {
		uniqueX = append(uniqueX, x)
		agg := stat.Mean(yValues, nil)
		aggregatedY = append(aggregatedY, agg)
	}

	return uniqueX, aggregatedY
}

// byX вспомогательный тип для сортировки по X
type byX struct {
	xs, ys []float64
}

func (b byX) Len() int           { return len(b.xs) }
func (b byX) Less(i, j int) bool { return b.xs[i] < b.xs[j] }
func (b byX) Swap(i, j int) {
	b.xs[i], b.xs[j] = b.xs[j], b.xs[i]
	b.ys[i], b.ys[j] = b.ys[j], b.ys[i]
}

// hardnessConverter конвертирует значения твёрдости
type hardnessConverter struct {
	interpolators map[string]map[string]*interp.PiecewiseLinear
}

// newHardnessConverter создаёт новый конвертер
func newHardnessConverter() (*hardnessConverter, error) {
	hc := &hardnessConverter{
		interpolators: make(map[string]map[string]*interp.PiecewiseLinear),
	}

	// Создаём интерполяторы для всех комбинаций
	for _, from := range scales {
		hc.interpolators[from] = make(map[string]*interp.PiecewiseLinear)
		for _, to := range scales {
			if from != to {
				interp, err := hc.createInterpolator(from, to)
				if err != nil {
					// Пропускаем проблемные комбинации
					continue
				}
				hc.interpolators[from][to] = interp
			}
		}
	}

	return hc, nil
}

func (hc *hardnessConverter) createInterpolator(from, to string) (*interp.PiecewiseLinear, error) {
	xData := make([]float64, len(data))
	yData := make([]float64, len(data))

	for i, d := range data {
		xData[i] = getValue(d, from)
		yData[i] = getValue(d, to)
	}

	return newInterpolator(xData, yData)
}

// getValue возвращает значение поля по имени шкалы
func getValue(d hardness, scale string) float64 {
	switch scale {
	case "HB":
		return d.HB
	case "HRA":
		return d.HRA
	case "HRC":
		return d.HRC
	case "HRB":
		return d.HRB
	case "HV":
		return d.HV
	case "HSD":
		return d.HSD
	default:
		return math.NaN()
	}
}

// Convert конвертирует значение из одной шкалы во все остальные
func (hc *hardnessConverter) Convert(fromScale string, value float64) map[string]float64 {
	result := make(map[string]float64)

	// Проверяем, существует ли шкала
	if _, ok := hc.interpolators[fromScale]; !ok {
		return result
	}

	result[fromScale] = value

	for toScale, interpolator := range hc.interpolators[fromScale] {
		result[toScale] = interpolator.Predict(value)
	}

	return result
}

var scales = []string{"HB", "HRA", "HRC", "HRB", "HV", "HSD"}

// Твердость.
type hardness struct {
	d10 float64
	HB  float64
	HRA float64
	HRC float64
	HRB float64
	HV  float64
	HSD float64
}

func (h hardness) String() string {
	return fmt.Sprintf("HB: %.1f, HRA: %.1f, HRC: %.1f, HRB: %.1f HV: %.1f, HSD: %.1f", h.HB, h.HRA, h.HRC, h.HRB, h.HV, h.HSD)
}

//go:embed hardness.json
var embeddedJSON []byte

var (
	data      []hardness
	converter *hardnessConverter
)

func init() {
	var err error

	embeddedJSON, err = os.ReadFile("substance/hardness/hardness.json")
	if err != nil {
		fmt.Println(err)
		return
	}
	if err = json.Unmarshal(embeddedJSON, &data); err != nil {
		fmt.Println(err)
		return
	}

	converter, err = newHardnessConverter()
	if err != nil {
		fmt.Println(err)
		return
	}
}

func Hardness(scale string, value float64) (hardness, error) {
	if !slices.Contains(scales, scale) {
		return hardness{}, fmt.Errorf("scale: %v not found!", scale)
	}

	converted := converter.Convert(scale, value)
	return hardness{
		HB:  converted["HB"],
		HRA: converted["HRA"],
		HRC: converted["HRC"],
		HRB: converted["HRB"],
		HV:  converted["HV"],
		HSD: converted["HSD"],
	}, nil
}
