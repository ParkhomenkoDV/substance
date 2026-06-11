package hardness

import "testing"

func TestHardness(t *testing.T) {
	tests := []struct {
		name    string
		scale   string
		value   float64
		want    hardness
		wantErr bool
	}{
		{
			name:    "HB=229",
			scale:   "HB",
			value:   229,
			wantErr: false,
			want: hardness{
				HB:  229,
				HRA: 61.8,
				HRC: 22.0,
				HRB: 98.2,
				HV:  229.0,
				HSD: 32.5,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, gotErr := Hardness(tt.scale, tt.value)
			if gotErr != nil {
				if !tt.wantErr {
					t.Errorf("Hardness() failed: %v", gotErr)
				}
				return
			}
			if tt.wantErr {
				t.Fatal("Hardness() succeeded unexpectedly")
			}
			if got != tt.want {
				t.Errorf("Hardness() = %+v, want %+v", got, tt.want)
			}
		})
	}
}
