package substance

import "fmt"

const (
	errParameterNotFound = "substance '%s': parameter '%s' not found"
	errFunctionNotFound  = "substance '%s': function '%s' not found"
)

// Substance - Вещество.
type Substance struct {
	Name       string                                      `doc:"Имя"`
	Parameters map[string]float64                          `doc:"Параметры"`
	Functions  map[string]func(map[string]float64) float64 `doc:"Функции"`
}

// Получение параметра по имени.
func (s *Substance) P(name string) float64 {
	p, ok := s.Parameters[name]
	if ok {
		return p
	}
	panic(fmt.Sprintf(errParameterNotFound, s.Name, name))
}

// Получение функиции по имени.
func (s *Substance) F(name string) func(map[string]float64) float64 {
	f, ok := s.Functions[name]
	if ok {
		return f
	}
	panic(fmt.Sprintf(errFunctionNotFound, s.Name, name))
}
