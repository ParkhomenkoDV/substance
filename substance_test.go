package substance

import (
	"math"
	"testing"
)

func TestNewParameter(t *testing.T) {
	tests := []struct {
		name          string
		parameterName string
		value         float64
		unit          string
		description   string
		want          Parameter
		wantErr       bool
	}{
		{
			name:          "empty parameterName",
			parameterName: "",
			value:         30,
			unit:          "kg",
			description:   "mass",
			want:          Parameter{},
			wantErr:       true,
		}, {
			name:          "Mass in kg",
			parameterName: "Mass",
			value:         30,
			unit:          "kg",
			description:   "Mass",
			want: Parameter{
				Name:        "Mass",
				Value:       30,
				Unit:        "kg",
				Multiplier:  1,
				ValueUnit:   30,
				Description: "Mass",
			},
			wantErr: false,
		}, {
			name:          "Mass in g",
			parameterName: "Mass",
			value:         1000,
			unit:          "g",
			description:   "Mass in grams",
			want: Parameter{
				Name:        "Mass",
				Value:       1000,
				Unit:        "g",
				Multiplier:  0.001,
				ValueUnit:   1,
				Description: "Mass in grams",
			},
			wantErr: false,
		}, {
			name:          "Length in km",
			parameterName: "Distance",
			value:         5,
			unit:          "km",
			description:   "Distance in kilometers",
			want: Parameter{
				Name:        "Distance",
				Value:       5,
				Unit:        "km",
				Multiplier:  1000,
				ValueUnit:   5000,
				Description: "Distance in kilometers",
			},
			wantErr: false,
		},
		{
			name:          "Time in ms",
			parameterName: "Time",
			value:         100,
			unit:          "ms",
			description:   "Time in milliseconds",
			want: Parameter{
				Name:        "Time",
				Value:       100,
				Unit:        "ms",
				Multiplier:  0.001,
				ValueUnit:   0.1,
				Description: "Time in milliseconds",
			},
			wantErr: false,
		},
		{
			name:          "empty unit",
			parameterName: "Count",
			value:         42,
			unit:          "",
			description:   "Unitless quantity",
			want: Parameter{
				Name:        "Count",
				Value:       42,
				Unit:        "",
				Multiplier:  1,
				ValueUnit:   42,
				Description: "Unitless quantity",
			},
			wantErr: false,
		},
		{
			name:          "invalid unit",
			parameterName: "Invalid",
			value:         10,
			unit:          "xyz",
			description:   "Invalid unit",
			want:          Parameter{},
			wantErr:       true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := NewParameter(tt.parameterName, tt.value, tt.unit, tt.description)

			// Проверка ошибки
			if (err != nil) != tt.wantErr {
				t.Errorf("NewParameter() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if err != nil {
				return
			}

			// Проверка полей
			if got.Name != tt.want.Name {
				t.Errorf("Name = %v, want %v", got.Name, tt.want.Name)
			}
			if got.Value != tt.want.Value {
				t.Errorf("Value = %v, want %v", got.Value, tt.want.Value)
			}
			if got.Unit != tt.want.Unit {
				t.Errorf("Unit = %v, want %v", got.Unit, tt.want.Unit)
			}
			if math.Abs(got.Multiplier-tt.want.Multiplier) > 1e-10 {
				t.Errorf("Multiplier = %v, want %v", got.Multiplier, tt.want.Multiplier)
			}
			if math.Abs(got.ValueUnit-tt.want.ValueUnit) > 1e-10 {
				t.Errorf("ValueUnit = %v, want %v", got.ValueUnit, tt.want.ValueUnit)
			}
			if got.Description != tt.want.Description {
				t.Errorf("Description = %v, want %v", got.Description, tt.want.Description)
			}
		})
	}
}

func TestParameter_Get(t *testing.T) {
	tests := []struct {
		name      string
		parameter Parameter
		want      float64
	}{
		{
			name: "simple value",
			parameter: Parameter{
				ValueUnit: 42.5,
			},
			want: 42.5,
		},
		{
			name: "zero value",
			parameter: Parameter{
				ValueUnit: 0,
			},
			want: 0,
		},
		{
			name: "negative value",
			parameter: Parameter{
				ValueUnit: -10.5,
			},
			want: -10.5,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.parameter.Get(); got != tt.want {
				t.Errorf("Parameter.Get() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestNewSubstance(t *testing.T) {
	tests := []struct {
		name       string
		substName  string
		parameters map[string]Parameter
		functions  map[string]func(map[string]Parameter) float64
		want       Substance
		wantErr    bool
	}{
		{
			name:      "empty name",
			substName: "",
			want:      Substance{},
			wantErr:   true,
		},
		{
			name:       "valid substance with no parameters",
			substName:  "Water",
			parameters: map[string]Parameter{},
			functions:  map[string]func(map[string]Parameter) float64{},
			want: Substance{
				Name:       "Water",
				Parameters: map[string]Parameter{},
				Functions:  map[string]func(map[string]Parameter) float64{},
			},
			wantErr: false,
		},
		{
			name:      "valid substance with parameters",
			substName: "Air",
			parameters: map[string]Parameter{
				"density": {
					Name:      "density",
					Value:     1.225,
					Unit:      "kg/m3",
					ValueUnit: 1.225,
				},
			},
			functions: map[string]func(map[string]Parameter) float64{
				"calculate": func(params map[string]Parameter) float64 {
					return params["density"].Value
				},
			},
			want: Substance{
				Name: "Air",
				Parameters: map[string]Parameter{
					"density": {
						Name:      "density",
						Value:     1.225,
						Unit:      "kg/m3",
						ValueUnit: 1.225,
					},
				},
				Functions: map[string]func(map[string]Parameter) float64{
					"calculate": func(params map[string]Parameter) float64 {
						return params["density"].Value
					},
				},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := NewSubstance(tt.substName, tt.parameters, tt.functions)

			if (err != nil) != tt.wantErr {
				t.Errorf("NewSubstance() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if err != nil {
				return
			}

			if got.Name != tt.want.Name {
				t.Errorf("Name = %v, want %v", got.Name, tt.want.Name)
			}

			if len(got.Parameters) != len(tt.want.Parameters) {
				t.Errorf("Parameters length = %v, want %v", len(got.Parameters), len(tt.want.Parameters))
			}

			if len(got.Functions) != len(tt.want.Functions) {
				t.Errorf("Functions length = %v, want %v", len(got.Functions), len(tt.want.Functions))
			}
		})
	}
}

func TestCalculateMultiplier(t *testing.T) {
	tests := []struct {
		name    string
		unit    string
		want    float64
		wantErr bool
	}{
		{
			name:    "empty unit",
			unit:    "",
			want:    1.0,
			wantErr: false,
		},
		{
			name:    "simple kg",
			unit:    "kg",
			want:    1.0,
			wantErr: false,
		},
		{
			name:    "gram",
			unit:    "g",
			want:    0.001,
			wantErr: false,
		},
		{
			name:    "kilometer",
			unit:    "km",
			want:    1000,
			wantErr: false,
		},
		{
			name:    "millisecond",
			unit:    "ms",
			want:    0.001,
			wantErr: false,
		},
		{
			name:    "square meter",
			unit:    "m2",
			want:    1.0,
			wantErr: false,
		},
		{
			name:    "square kilometer",
			unit:    "km2",
			want:    1e6,
			wantErr: false,
		},
		{
			name:    "cubic meter",
			unit:    "m^3",
			want:    1.0,
			wantErr: false,
		},
		{
			name:    "cubic kilometer",
			unit:    "km^3",
			want:    1e9,
			wantErr: false,
		},
		{
			name:    "velocity km/h",
			unit:    "km/h",
			want:    1000.0 / 3600.0, // 0.277777...
			wantErr: false,
		},
		{
			name:    "acceleration m/s2",
			unit:    "m/s2",
			want:    1.0,
			wantErr: false,
		},
		{
			name:    "density kg/m3",
			unit:    "kg/m3",
			want:    1.0,
			wantErr: false,
		},
		{
			name:    "density g/cm3",
			unit:    "g/cm3",
			want:    1000.0, // 0.001 / (0.01^3) = 1000
			wantErr: false,
		},
		{
			name:    "force kg*m/s2",
			unit:    "kg*m/s2",
			want:    1.0,
			wantErr: false,
		},
		{
			name:    "complex with km and h2",
			unit:    "km/h2",
			want:    1000.0 / (3600.0 * 3600.0), // 7.716e-5
			wantErr: false,
		},
		{
			name:    "area in square km with ^ notation",
			unit:    "km^2",
			want:    1e6,
			wantErr: false,
		},
		{
			name:    "volume in cubic cm",
			unit:    "cm3",
			want:    1e-6,
			wantErr: false,
		},
		{
			name:    "pressure in kPa",
			unit:    "kPa",
			want:    1000,
			wantErr: false,
		},
		{
			name:    "pressure in MPa",
			unit:    "MPa",
			want:    1e6,
			wantErr: false,
		},
		{
			name:    "micrometer",
			unit:    "μm",
			want:    1e-6,
			wantErr: false,
		},
		{
			name:    "nanometer",
			unit:    "nm",
			want:    1e-9,
			wantErr: false,
		},
		{
			name:    "invalid unit",
			unit:    "xyz",
			want:    0,
			wantErr: true,
		},
		{
			name:    "unit with space",
			unit:    "km / h",
			want:    1000.0 / 3600.0,
			wantErr: false,
		},
		{
			name:    "multiple operations",
			unit:    "kg*m/s2",
			want:    1.0,
			wantErr: false,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got, err := calculateMultiplier(test.unit)

			if (err != nil) != test.wantErr {
				t.Errorf("calculateMultiplier() error = %v, wantErr %v", err, test.wantErr)
				return
			}

			if err != nil {
				return
			}

			if math.Abs(got-test.want) > 1e-10 {
				t.Errorf("calculateMultiplier() = %v, want %v", got, test.want)
			}
		})
	}
}

func TestExtractPower(t *testing.T) {
	tests := []struct {
		name      string
		token     string
		wantBase  string
		wantPower float64
	}{
		{
			name:      "no power",
			token:     "kg",
			wantBase:  "kg",
			wantPower: 1.0,
		},
		{
			name:      "power with number suffix",
			token:     "m2",
			wantBase:  "m",
			wantPower: 2.0,
		},
		{
			name:      "power with ^",
			token:     "m^3",
			wantBase:  "m^",
			wantPower: 3.0,
		},
		{
			name:      "complex unit with power",
			token:     "km2",
			wantBase:  "km",
			wantPower: 2.0,
		},
		{
			name:      "multiple digits power",
			token:     "m10",
			wantBase:  "m",
			wantPower: 10.0,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			gotBase, gotPower := extractPower(test.token)

			if gotBase != test.wantBase {
				t.Errorf("extractPower() base = %v, want %v", gotBase, test.wantBase)
			}

			if math.Abs(gotPower-test.wantPower) > 1e-10 {
				t.Errorf("extractPower() power = %v, want %v", gotPower, test.wantPower)
			}
		})
	}
}

func TestSplitByOperators(t *testing.T) {
	tests := []struct {
		name string
		unit string
		want []string
	}{
		{
			name: "simple unit",
			unit: "kg",
			want: []string{"kg"},
		},
		{
			name: "multiplication",
			unit: "kg*m",
			want: []string{"kg", "*m"},
		},
		{
			name: "division",
			unit: "m/s",
			want: []string{"m", "/s"},
		},
		{
			name: "power",
			unit: "m^2",
			want: []string{"m", "^2"},
		},
		{
			name: "complex expression",
			unit: "kg*m/s2",
			want: []string{"kg", "*m", "/s2"},
		},
		{
			name: "multiple operators",
			unit: "km/h^2",
			want: []string{"km", "/h", "^2"},
		},
		{
			name: "no operators",
			unit: "kilogram",
			want: []string{"kilogram"},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got := splitByOperators(test.unit)

			if len(got) != len(test.want) {
				t.Errorf("splitByOperators() length = %v, want %v", len(got), len(test.want))
				return
			}

			for i := range got {
				if got[i] != test.want[i] {
					t.Errorf("splitByOperators()[%d] = %v, want %v", i, got[i], test.want[i])
				}
			}
		})
	}
}

func TestIsNumeric(t *testing.T) {
	tests := []struct {
		name string
		s    string
		want bool
	}{
		{
			name: "integer",
			s:    "123",
			want: true,
		},
		{
			name: "float",
			s:    "123.45",
			want: true,
		},
		{
			name: "negative number",
			s:    "-123",
			want: true,
		},
		{
			name: "scientific notation",
			s:    "1.23e-4",
			want: true,
		},
		{
			name: "not a number",
			s:    "abc",
			want: false,
		},
		{
			name: "empty string",
			s:    "",
			want: false,
		},
		{
			name: "number with letters",
			s:    "123abc",
			want: false,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := isNumeric(test.s); got != test.want {
				t.Errorf("isNumeric() = %v, want %v", got, test.want)
			}
		})
	}
}

func TestPrefixes(t *testing.T) {
	// Проверка, что все приставки имеют уникальные значения
	seen := make(map[float64]bool)
	for prefix, value := range Prefixes {
		if seen[value] {
			t.Errorf("Duplicate multiplier value %v for prefix %s", value, prefix)
		}
		seen[value] = true
	}

	// Проверка порядка величин
	expected := []float64{1e-30, 1e-27, 1e-24, 1e-21, 1e-18, 1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3, 1e6, 1e9, 1e12, 1e15, 1e18, 1e21, 1e24, 1e27, 1e30}

	values := make([]float64, 0, len(Prefixes))
	for _, v := range Prefixes {
		values = append(values, v)
	}

	for _, exp := range expected {
		found := false
		for _, v := range values {
			if math.Abs(v-exp) < 1e-10 {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("Expected multiplier %v not found in Prefixes", exp)
		}
	}
}
