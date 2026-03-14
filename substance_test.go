package substance

import (
	"math"
	"testing"
)

func TestSubstanceP(t *testing.T) {
	// Create test parameters
	params := map[string]float64{
		"length": 5.0,
		"mass":   2.0,
		"time":   10.0,
	}

	substance := Substance{
		Name:       "test",
		Parameters: params,
		Functions:  make(map[string]func(map[string]float64) float64),
	}

	tests := []struct {
		name      string
		paramName string
		wantPanic bool
		wantValue float64
	}{
		{
			name:      "Existing parameter",
			paramName: "length",
			wantPanic: false,
			wantValue: 5.0,
		}, {
			name:      "Another existing parameter",
			paramName: "mass",
			wantPanic: false,
			wantValue: 2.0,
		}, {
			name:      "Non-existent parameter",
			paramName: "velocity",
			wantPanic: true,
		}, {
			name:      "Empty string",
			paramName: "",
			wantPanic: true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if test.wantPanic {
				defer func() {
					if r := recover(); r == nil {
						t.Errorf("P() did not panic for non-existent parameter")
					}
				}()
				substance.P(test.paramName)
			} else {
				got := substance.P(test.paramName)
				if got != test.wantValue {
					t.Errorf("P() = %v, want %v", got, test.wantValue)
				}
			}
		})
	}
}

func TestSubstanceF(t *testing.T) {
	// Test functions
	functions := map[string]func(map[string]float64) float64{
		"double": func(p map[string]float64) float64 {
			if val, ok := p["value"]; ok {
				return val * 2
			}
			return 0
		},
		"square": func(p map[string]float64) float64 {
			if val, ok := p["value"]; ok {
				return val * val
			}
			return 0
		},
	}

	substance := Substance{
		Name:       "test",
		Parameters: make(map[string]float64),
		Functions:  functions,
	}

	tests := []struct {
		name       string
		funcName   string
		wantPanic  bool
		testValue  float64
		wantResult float64
	}{
		{
			name:       "Existing function - double",
			funcName:   "double",
			wantPanic:  false,
			testValue:  5.0,
			wantResult: 10.0,
		}, {
			name:       "Existing function - square",
			funcName:   "square",
			wantPanic:  false,
			testValue:  4.0,
			wantResult: 16.0,
		}, {
			name:      "Non-existent function",
			funcName:  "cube",
			wantPanic: true,
		}, {
			name:      "Empty string",
			funcName:  "",
			wantPanic: true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if test.wantPanic {
				defer func() {
					if r := recover(); r == nil {
						t.Errorf("F() did not panic for non-existent function")
					}
				}()
				substance.F(test.funcName)
			} else {
				got := substance.F(test.funcName)
				if got == nil {
					t.Fatal("F() returned nil for existing function")
				}

				// Test the function
				params := map[string]float64{
					"value": test.testValue,
				}
				result := got(params)
				if math.Abs(result-test.wantResult) > 1e-10 {
					t.Errorf("Function result = %v, want %v", result, test.wantResult)
				}
			}
		})
	}
}

func TestSubstanceWithMultipleParameters(t *testing.T) {
	// Create substance with parameters and functions
	parameters := map[string]float64{
		"length": 5.0,
		"width":  3.0,
		"height": 2.0,
		"mass":   10.0,
		"time":   60.0,
	}

	functions := map[string]func(map[string]float64) float64{
		"volume": func(p map[string]float64) float64 {
			return p["length"] * p["width"] * p["height"]
		},
		"density": func(p map[string]float64) float64 {
			volume := p["length"] * p["width"] * p["height"]
			if volume == 0 {
				return 0
			}
			return p["mass"] / volume
		},
		"speed": func(p map[string]float64) float64 {
			return p["length"] / p["time"]
		},
	}

	substance := Substance{
		Name:       "Test Substance",
		Parameters: parameters,
		Functions:  functions,
	}

	// Test getting parameters
	t.Run("Get parameters", func(t *testing.T) {
		length := substance.P("length")
		if length != 5.0 {
			t.Errorf("length = %v, want 5.0", length)
		}

		mass := substance.P("mass")
		if mass != 10.0 {
			t.Errorf("mass = %v, want 10.0", mass)
		}

		// Test panic for non-existent parameter
		defer func() {
			if r := recover(); r == nil {
				t.Errorf("P() should panic for non-existent parameter")
			}
		}()
		substance.P("non_existent")
	})

	// Test functions
	t.Run("Volume function", func(t *testing.T) {
		volume := substance.F("volume")
		if volume == nil {
			t.Fatal("volume function not found")
		}
		result := volume(substance.Parameters)
		expected := 5.0 * 3.0 * 2.0 // 30.0
		if math.Abs(result-expected) > 1e-10 {
			t.Errorf("volume = %v, want %v", result, expected)
		}
	})

	t.Run("Density function", func(t *testing.T) {
		density := substance.F("density")
		if density == nil {
			t.Fatal("density function not found")
		}
		result := density(substance.Parameters)
		expected := 10.0 / (5.0 * 3.0 * 2.0) // 0.33333...
		if math.Abs(result-expected) > 1e-10 {
			t.Errorf("density = %v, want %v", result, expected)
		}
	})

	t.Run("Speed function", func(t *testing.T) {
		speed := substance.F("speed")
		if speed == nil {
			t.Fatal("speed function not found")
		}
		result := speed(substance.Parameters)
		expected := 5.0 / 60.0 // 0.08333...
		if math.Abs(result-expected) > 1e-10 {
			t.Errorf("speed = %v, want %v", result, expected)
		}
	})

	// Test panic for non-existent function
	t.Run("Non-existent function", func(t *testing.T) {
		defer func() {
			if r := recover(); r == nil {
				t.Errorf("F() should panic for non-existent function")
			}
		}()
		substance.F("non_existent")
	})
}

func TestSubstanceEmpty(t *testing.T) {
	substance := Substance{
		Name:       "Empty",
		Parameters: make(map[string]float64),
		Functions:  make(map[string]func(map[string]float64) float64),
	}

	// Test P with empty parameters - should panic
	t.Run("P with empty parameters", func(t *testing.T) {
		defer func() {
			if r := recover(); r == nil {
				t.Errorf("P() should panic when parameter not found")
			}
		}()
		substance.P("anything")
	})

	// Test F with empty functions - should panic
	t.Run("F with empty functions", func(t *testing.T) {
		defer func() {
			if r := recover(); r == nil {
				t.Errorf("F() should panic when function not found")
			}
		}()
		substance.F("anything")
	})
}

// Бенчмарк получения параметров
func BenchmarkSubstanceP(b *testing.B) {
	params := make(map[string]float64)
	for i := 0; i < 100; i++ {
		name := string(rune('A' + i%26))
		params[name] = float64(i)
	}

	substance := Substance{
		Name:       "Benchmark",
		Parameters: params,
		Functions:  make(map[string]func(map[string]float64) float64),
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = substance.P("A")
	}
}

// Бенчмарк получения и вызова функций
func BenchmarkSubstanceF(b *testing.B) {
	functions := make(map[string]func(map[string]float64) float64)
	for i := 0; i < 20; i++ {
		funcName := string(rune('A' + i%26))
		functions[funcName] = func(p map[string]float64) float64 {
			sum := 0.0
			for _, v := range p {
				sum += v
			}
			return sum
		}
	}

	params := map[string]float64{
		"a": 1.0,
		"b": 2.0,
		"c": 3.0,
	}

	substance := Substance{
		Name:       "Benchmark",
		Parameters: params,
		Functions:  functions,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		fn := substance.F("A")
		_ = fn(params)
	}
}

// Бенчмарк создания вещества
func BenchmarkNewSubstance(b *testing.B) {
	// Подготавливаем данные ДО цикла бенчмарка
	params := make(map[string]float64, 100)
	for j := 0; j < 100; j++ {
		name := string(rune('A' + j%26))
		params[name] = float64(j)
	}

	funcs := make(map[string]func(map[string]float64) float64, 20)
	for j := 0; j < 20; j++ {
		funcName := string(rune('A' + j%26))
		// Внимание: захват переменной j в замыкании!
		funcs[funcName] = func(p map[string]float64) float64 {
			var sum float64
			for _, v := range p {
				sum += v
			}
			return sum
		}
	}

	// Сбрасываем таймер перед началом замера
	b.ResetTimer()

	// Теперь замеряем только создание Substance
	for i := 0; i < b.N; i++ {
		substance := Substance{
			Name:       "Complex",
			Parameters: params,
			Functions:  funcs,
		}
		_ = substance
	}
}
