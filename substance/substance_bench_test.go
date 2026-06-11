package substance

import "testing"

// Бенчмарк создания вещества
func BenchmarkNewSubstance(b *testing.B) {
	// Подготавливаем данные ДО цикла бенчмарка
	params := make(map[string]float64, 100)
	for j := 0; j < 100; j++ {
		name := string(rune('A' + j%26))
		params[name] = float64(j)
	}

	funcs := make(Functions, 20)
	for j := 0; j < 20; j++ {
		funcName := string(rune('A' + j%26))
		// Внимание: захват переменной j в замыкании!
		funcs[funcName] = func(ps Parameters) float64 {
			var sum float64
			for _, v := range ps {
				sum += v
			}
			return sum
		}

	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		substance := Substance{
			Name:       "Complex",
			Parameters: params,
			Functions:  funcs,
		}
		_ = substance
	}
}

// Бенчмарк для метода C
func BenchmarkSubstanceC(b *testing.B) {
	composition := make(map[string]float64)
	for i := 0; i < 100; i++ {
		compName := string(rune('A'+i%26)) + string(rune('0'+i/26))
		composition[compName] = 1.0 / 100.0
	}

	substance := Substance{
		Name:        "Bench",
		Composition: composition,
		Parameters:  make(Parameters),
		Functions:   make(Functions),
	}

	// Запоминаем ключ для поиска
	var key string
	for k := range composition {
		key = k
		break
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = substance.C(key)
	}
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
		Functions:  make(Functions),
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = substance.P("A")
	}
}

// Бенчмарк получения и вызова функций
func BenchmarkSubstanceF(b *testing.B) {
	params := map[string]float64{
		"a": 1.0,
		"b": 2.0,
		"c": 3.0,
	}

	functions := make(Functions)
	for i := 0; i < 20; i++ {
		funcName := string(rune('A' + i%26))
		functions[funcName] = func(ps Parameters) float64 {
			sum := 0.0
			for _, v := range ps {
				sum += v
			}
			return sum
		}
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
