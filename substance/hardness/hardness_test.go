package hardness

import (
	"fmt"
	"testing"
)

func TestHardness(t *testing.T) {
	for _, d := range data[:len(data)-180] {
		for _, scale := range Scales {
			value := getValue(d, scale)
			if value == 0 { // no data
				continue
			}
			testName := fmt.Sprintf("%s%v", scale, value)
			t.Run(testName, func(t *testing.T) {
				got := Hardness(scale, value)
				if !got.Eq(d, 0.02) { // 2%
					t.Errorf("Hardness() = %s, want %s", got.String(), d.String())
				}
			})
		}
	}
}
