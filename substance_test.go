package substance

import (
	"math"
	"testing"

	"github.com/ParkhomenkoDV/units"
)

func TestNewParameter(t *testing.T) {
	tests := []struct {
		name        string
		value       float64
		unit        float64
		description string
		wantSI      float64
	}{
		{
			name:        "Meter test",
			value:       5.0,
			unit:        units.Meter,
			description: "Length",
			wantSI:      5.0,
		},
		{
			name:        "Kilogram test",
			value:       2.5,
			unit:        units.Kilogram,
			description: "Mass",
			wantSI:      2.5,
		},
		{
			name:        "Newton test",
			value:       10.0,
			unit:        units.Newton,
			description: "Force",
			wantSI:      10.0,
		},
		{
			name:        "Minute test",
			value:       2.0,
			unit:        units.Minute,
			description: "Time",
			wantSI:      120.0,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got := NewParameter(test.name, test.value, test.unit, test.description)

			if got.Name != test.name {
				t.Errorf("Name = %v, want %v", got.Name, test.name)
			}
			if got.Value != test.value {
				t.Errorf("Value = %v, want %v", got.Value, test.value)
			}
			if got.Unit != test.unit {
				t.Errorf("Unit = %v, want %v", got.Unit, test.unit)
			}
			if math.Abs(got.SI-test.wantSI) > 1e-10 {
				t.Errorf("SI = %v, want %v", got.SI, test.wantSI)
			}
			if got.Description != test.description {
				t.Errorf("Description = %v, want %v", got.Description, test.description)
			}
		})
	}
}

func TestSubstanceP(t *testing.T) {
	// Create test parameters
	params := map[string]Parameter{
		"length": NewParameter("length", 5.0, units.Meter, "Length"),
		"mass":   NewParameter("mass", 2.0, units.Kilogram, "Mass"),
		"time":   NewParameter("time", 10.0, units.Second, "Time"),
	}

	substance := Substance{
		Name:       "test",
		Parameters: params,
		Functions:  make(map[string]func(map[string]Parameter) float64),
	}

	tests := []struct {
		name      string
		paramName string
		wantNil   bool
		wantValue float64
	}{
		{
			name:      "Existing parameter",
			paramName: "length",
			wantNil:   false,
			wantValue: 5.0,
		},
		{
			name:      "Another existing parameter",
			paramName: "mass",
			wantNil:   false,
			wantValue: 2.0,
		},
		{
			name:      "Non-existent parameter",
			paramName: "velocity",
			wantNil:   true,
		},
		{
			name:      "Empty string",
			paramName: "",
			wantNil:   true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got := substance.P(test.paramName)

			if test.wantNil {
				if got != nil {
					t.Errorf("P() = %v, want nil", got)
				}
			} else {
				if got == nil {
					t.Errorf("P() = nil, want parameter")
				} else if got.Value != test.wantValue {
					t.Errorf("P().Value = %v, want %v", got.Value, test.wantValue)
				}
			}
		})
	}
}

func TestSubstanceF(t *testing.T) {
	// Test functions
	functions := map[string]func(map[string]Parameter) float64{
		"double": func(p map[string]Parameter) float64 {
			if val, ok := p["value"]; ok {
				return val.Value * 2
			}
			return 0
		},
		"square": func(p map[string]Parameter) float64 {
			if val, ok := p["value"]; ok {
				return val.Value * val.Value
			}
			return 0
		},
	}

	substance := Substance{
		Name:       "test",
		Parameters: make(map[string]Parameter),
		Functions:  functions,
	}

	tests := []struct {
		name       string
		funcName   string
		wantNil    bool
		testValue  float64
		wantResult float64
	}{
		{
			name:       "Existing function - double",
			funcName:   "double",
			wantNil:    false,
			testValue:  5.0,
			wantResult: 10.0,
		},
		{
			name:       "Existing function - square",
			funcName:   "square",
			wantNil:    false,
			testValue:  4.0,
			wantResult: 16.0,
		},
		{
			name:     "Non-existent function",
			funcName: "cube",
			wantNil:  true,
		},
		{
			name:     "Empty string",
			funcName: "",
			wantNil:  true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got := substance.F(test.funcName)

			if test.wantNil {
				if got != nil {
					t.Errorf("F() = %v, want nil", test.name)
				}
			} else {
				if got == nil {
					t.Errorf("F() = nil, want function")
				} else {
					// Test the function
					params := map[string]Parameter{
						"value": NewParameter("value", test.testValue, units.Meter, "Test value"),
					}
					result := got(params)
					if math.Abs(result-test.wantResult) > 1e-10 {
						t.Errorf("Function result = %v, want %v", result, test.wantResult)
					}
				}
			}
		})
	}
}

func TestSubstanceWithMultipleParameters(t *testing.T) {
	// Create substance with parameters and functions
	parameters := map[string]Parameter{
		"length": NewParameter("length", 5.0, units.Meter, "Length"),
		"width":  NewParameter("width", 3.0, units.Meter, "Width"),
		"height": NewParameter("height", 2.0, units.Meter, "Height"),
		"mass":   NewParameter("mass", 10.0, units.Kilogram, "Mass"),
		"time":   NewParameter("time", 60.0, units.Second, "Time"),
	}

	functions := map[string]func(map[string]Parameter) float64{
		"volume": func(p map[string]Parameter) float64 {
			return p["length"].Value * p["width"].Value * p["height"].Value
		},
		"density": func(p map[string]Parameter) float64 {
			volume := p["length"].Value * p["width"].Value * p["height"].Value
			if volume == 0 {
				return 0
			}
			return p["mass"].Value / volume
		},
		"speed": func(p map[string]Parameter) float64 {
			return p["length"].Value / p["time"].Value
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
		if length == nil || length.Value != 5.0 {
			t.Errorf("length = %v, want 5.0", length)
		}

		mass := substance.P("mass")
		if mass == nil || mass.Value != 10.0 {
			t.Errorf("mass = %v, want 10.0", mass)
		}
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
		expected := 10.0 / (5.0 * 3.0 * 2.0) // 0.3333...
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
}

func TestSubstanceEmpty(t *testing.T) {
	substance := Substance{
		Name:       "Empty",
		Parameters: make(map[string]Parameter),
		Functions:  make(map[string]func(map[string]Parameter) float64),
	}

	// Test P with empty parameters
	if got := substance.P("anything"); got != nil {
		t.Errorf("P() with empty parameters = %v, want nil", got)
	}

	// Test F with empty functions
	if got := substance.F("anything"); got != nil {
		t.Errorf("F() with empty functions = %v, want nil", "lhjeb")
	}
}
