package utils

import (
	"fmt"
	"math"
	"sort"

	"gonum.org/v1/gonum/interp"
	"gonum.org/v1/gonum/stat"
)

// Создаёт новый линейный интерполятор из данных
func NewInterpolator(xData, yData []float64) (*interp.PiecewiseLinear, error) {
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

	// Интерполируем
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
