package substance

// Substance - Вещество.
type Substance struct {
	Name       string                                      `doc:"Имя вещества"`
	Parameters map[string]float64                          `doc:"Параметры"`
	Functions  map[string]func(map[string]float64) float64 `doc:"Функции"`
}
