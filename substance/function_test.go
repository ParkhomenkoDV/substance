package substance

import (
	"testing"
)

func TestFunction_Call(t *testing.T) {
	tests := []struct {
		name     string
		function Function
		ps       Parameters
		want     Parameter
	}{
		{
			name: "test",
			function: Function{
				Func: func(ps Parameters) Parameter {
					return ps["t"] + ps["p"]
				},
				Args: map[string]struct{}{
					"t": {}, "p": {},
				},
			},
			ps: Parameters{
				"t": 1, "p": 2, "extra": 3,
			},
			want: 3,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.function.Call(tt.ps)
			if got != tt.want {
				t.Errorf("Call() = %v, want %v", got, tt.want)
			}
		})
	}
}
