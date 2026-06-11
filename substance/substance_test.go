package substance

import (
	"math"
	"testing"
)

func TestInit(t *testing.T) {
	t.Run("Init pretty", func(t *testing.T) {
		s := Substance{
			Name: "test",
			Parameters: Parameters{
				"eo": 3,
				"m":  50,
				"t":  300,
				"p":  101_325,
			},
			Functions: Functions{
				"gc": func(p Parameters) Parameter {
					return 287.3
				},

				"hcp": func(ps Parameters) float64 { return ps["t"] + 3 },
			},
		}
		enthalpy := s.Functions["hcp"](Parameters{"t": 500}) * s.P("m") * s.P("t")
		if enthalpy != 7_545_000 {
			t.Errorf("got: %v, want: %v", enthalpy, 7_545_000)
		}
	})
}

func TestSubstanceC(t *testing.T) {
	// Создаём вещество с химическим составом
	composition := map[string]float64{
		"H2O":    0.80,
		"NaCl":   0.15,
		"C2H5OH": 0.05,
	}

	substance := Substance{
		Name:        "TestSolution",
		Composition: composition,
		Parameters:  make(Parameters),
		Functions:   make(Functions),
	}

	tests := []struct {
		name      string
		component string
		wantPanic bool
		wantValue float64
	}{
		{
			name:      "Existing component H2O",
			component: "H2O",
			wantPanic: false,
			wantValue: 0.80,
		},
		{
			name:      "Existing component NaCl",
			component: "NaCl",
			wantPanic: false,
			wantValue: 0.15,
		},
		{
			name:      "Existing component C2H5OH",
			component: "C2H5OH",
			wantPanic: false,
			wantValue: 0.05,
		},
		{
			name:      "Non-existent component",
			component: "CO2",
			wantPanic: true,
		},
		{
			name:      "Empty string",
			component: "",
			wantPanic: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.wantPanic {
				defer func() {
					if r := recover(); r == nil {
						t.Errorf("C() did not panic for non-existent component")
					}
				}()
				substance.C(tt.component)
			} else {
				got := substance.C(tt.component)
				if math.Abs(got-tt.wantValue) > 1e-10 {
					t.Errorf("C(%q) = %v, want %v", tt.component, got, tt.wantValue)
				}
			}
		})
	}
}

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
		Functions:  make(Functions),
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
	functions := Functions{
		"double": func(ps Parameters) float64 {
			if val, ok := ps["value"]; ok {
				return val * 2
			}
			return 0
		},

		"square": func(ps Parameters) float64 {
			if val, ok := ps["value"]; ok {
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
	composition := map[string]float64{
		"A": 0.3,
		"B": 0.3,
		"C": 0.4,
	}

	parameters := map[string]float64{
		"length": 5.0,
		"width":  3.0,
		"height": 2.0,
		"mass":   10.0,
		"time":   60.0,
	}

	functions := Functions{
		"volume": func(ps Parameters) float64 {
			return ps["length"] * ps["width"] * ps["height"]
		},
		"density": func(ps Parameters) float64 {
			volume := ps["length"] * ps["width"] * ps["height"]
			if volume == 0 {
				return 0
			}
			return ps["mass"] / volume
		},
		"speed": func(ps Parameters) float64 {
			return ps["length"] / ps["time"]
		},
	}

	substance := Substance{
		Name:        "Test Substance",
		Composition: composition,
		Parameters:  parameters,
		Functions:   functions,
	}

	t.Run("", func(t *testing.T) {
		// Проверяем, что все компоненты доступны и их сумма = 1.0
		sum := 0.0
		for name, expected := range composition {
			got := substance.C(name)
			if math.Abs(got-expected) > 1e-10 {
				t.Errorf("C(%q) = %v, want %v", name, got, expected)
			}
			sum += got
		}
		if math.Abs(sum-1.0) > 1e-10 {
			t.Errorf("Sum of composition = %v, want 1.0", sum)
		}

		// Проверяем панику при запросе отсутствующего компонента
		defer func() {
			if r := recover(); r == nil {
				t.Error("C() should panic for missing component in non-empty composition")
			}
		}()
		substance.C("D")
	})

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
		Parameters: make(Parameters),
		Functions:  make(Functions),
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
