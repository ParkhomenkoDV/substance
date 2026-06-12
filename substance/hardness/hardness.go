package hardness

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"math"
	"os"

	"github.com/ParkhomenkoDV/substance/substance/utils"
	"gonum.org/v1/gonum/interp"
)

type Scale string

const (
	HB  Scale = "HB"
	HRA Scale = "HRA"
	HRC Scale = "HRC"
	HRB Scale = "HRB"
	HV  Scale = "HV"
	HSD Scale = "HSD"
)

var Scales = []Scale{HB, HRA, HRC, HRB, HV, HSD}

// Твердость.
type hardness struct {
	d10 float64 `doc:"Диаметр отпечатка, мм"`
	HB  float64 `doc:"Бринелль"`
	HRA float64 `doc:""`
	HRC float64 `doc:"Роквклл"`
	HRB float64 `doc:""`
	HV  float64 `doc:"Виккерс"`
	HSD float64 `doc:""`
}

func (h *hardness) String() (str string) {
	return fmt.Sprintf("HB: %.1f, HRA: %.1f, HRC: %.1f, HRB: %.1f HV: %.1f, HSD: %.1f", h.HB, h.HRA, h.HRC, h.HRB, h.HV, h.HSD)
}

// Eq сравнивает две Hardness с учётом погрешности
func (h *hardness) Eq(other hardness, eps float64) bool {
	return math.Abs(h.HB-other.HB) <= eps*h.HB &&
		math.Abs(h.HRA-other.HRA) <= eps*h.HRA &&
		math.Abs(h.HRC-other.HRC) <= eps*h.HRC &&
		math.Abs(h.HRB-other.HRB) <= eps*h.HRB &&
		math.Abs(h.HV-other.HV) <= eps*h.HV &&
		math.Abs(h.HSD-other.HSD) <= eps*h.HSD
}

// hardnessConverter конвертирует значения твёрдости
type hardnessConverter struct {
	interpolators map[Scale]map[Scale]*interp.PiecewiseLinear
}

// newHardnessConverter создаёт новый конвертер
func newHardnessConverter() (*hardnessConverter, error) {
	hc := &hardnessConverter{
		interpolators: make(map[Scale]map[Scale]*interp.PiecewiseLinear),
	}

	// Создаём интерполяторы для всех комбинаций
	for _, from := range Scales {
		hc.interpolators[from] = make(map[Scale]*interp.PiecewiseLinear)
		for _, to := range Scales {
			if from != to {
				interp, err := hc.createInterpolator(from, to)
				if err != nil {
					panic(err)
				}
				hc.interpolators[from][to] = interp
			}
		}
	}

	return hc, nil
}

func (hc *hardnessConverter) createInterpolator(from, to Scale) (*interp.PiecewiseLinear, error) {
	xData := make([]float64, len(data))
	yData := make([]float64, len(data))

	for i, d := range data {
		xData[i] = getValue(d, from)
		yData[i] = getValue(d, to)
	}

	return utils.NewInterpolator(xData, yData)
}

// getValue возвращает значение поля по имени шкалы
func getValue(d hardness, scale Scale) float64 {
	switch scale {
	case HB:
		return d.HB
	case HRA:
		return d.HRA
	case HRC:
		return d.HRC
	case HRB:
		return d.HRB
	case HV:
		return d.HV
	case HSD:
		return d.HSD
	default:
		return math.NaN()
	}
}

// Convert конвертирует значение из одной шкалы во все остальные
func (hc *hardnessConverter) Convert(fromScale Scale, value float64) map[Scale]float64 {
	result := make(map[Scale]float64)

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

//go:embed hardness.json
var embeddedHardnessJSON []byte

var (
	data      []hardness
	converter *hardnessConverter
)

func init() {
	var err error

	embeddedHardnessJSON, err = os.ReadFile("hardness.json")
	if err != nil {
		panic(err)
	}
	if err = json.Unmarshal(embeddedHardnessJSON, &data); err != nil {
		panic(err)
	}

	converter, err = newHardnessConverter()
	if err != nil {
		panic(err)
	}
}

// Перевод твердости в другую шкалу
func Hardness(scale Scale, value float64) hardness {
	converted := converter.Convert(scale, value)
	return hardness{
		HB:  converted["HB"],
		HRA: converted["HRA"],
		HRC: converted["HRC"],
		HRB: converted["HRB"],
		HV:  converted["HV"],
		HSD: converted["HSD"],
	}
}
