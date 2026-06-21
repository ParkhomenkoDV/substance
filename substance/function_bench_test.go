package substance

import "testing"

func BenchmarkNewFunction(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		f := Function{
			Name: "bench",
			Func: func(ps Parameters) Parameter {
				return ps["t"] + ps["p"]
			},
		}
		_ = f
	}
}

func BenchmarkFunctionCall(b *testing.B) {
	f := Function{
		Name: "bench",
		Func: func(ps Parameters) Parameter {
			return ps["t"] + ps["p"]
		},
		Args: map[string]struct{}{
			"t": {}, "p": {},
		},
	}

	ps := Parameters{
		"t": 1, "p": 2, "extra": 3,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		result := f.Call(ps)
		_ = result
	}
}
