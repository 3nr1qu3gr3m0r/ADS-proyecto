"""
Tests del EPiC Engine.

  1. Silogismo socrático   (Modus Ponens  — UI+)
  2. Modus Tollens         (UI−)
  3. Negación / polarity-switching
  4. Negación inversa
  5. Conjunción positiva
  6. Disyunción negativa
  7. Ejemplo Section 3.2 con cuantificadores y conjunción

Cada test imprime su traza completa (verbose=True).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor.dominio.modelos import Variable, Connective, EPiCModel
from motor.algoritmos.constantes import N, T, F, VALUE_NAMES
from motor.algoritmos.engine import EPiCEngine


def make_engine():
    return EPiCEngine(max_iterations=500)

def build_model(model_id, variables, connectives):
    return EPiCModel(id=model_id, variables=variables, connectives=connectives)

def val(var):
    return VALUE_NAMES[var.current_value]

def _header(title):
    print("\n" + "█" * 80)
    print(f"  {title}")
    print("█" * 80)


def test_modus_ponens():
    _header("TEST 1: Modus Ponens  (UI+)  —  H(s)=T, H(s)→M(s)=T  ⊢  M(s)=T")

    hs = Variable(id="H_s", name="H(s)", initial_value=T, current_value=T, is_premise=True)
    ms = Variable(id="M_s", name="M(s)", initial_value=N, current_value=N)
    z  = Variable(id="Z",   name="Z",    initial_value=T, current_value=T, is_premise=True)

    conn = Connective(id="imp1", type="implication",
                      input_ids=["H_s", "M_s"], output_id="Z")

    model = build_model("mp", [hs, ms, z], [conn])
    ps = make_engine().run(model, verbose=True)

    assert ps.stable, "Motor no estabilizó"
    assert ms.current_value == T, f"M(s) esperado T, es {val(ms)}"
    print(f"[PASS] Modus Ponens: M(s) = {val(ms)}")


def test_modus_tollens():
    _header("TEST 2: Modus Tollens  (UI−)  —  M(s)=F, H(s)→M(s)=T  ⊢  H(s)=F")

    hs = Variable(id="H_s", name="H(s)", initial_value=N, current_value=N)
    ms = Variable(id="M_s", name="M(s)", initial_value=F, current_value=F, is_premise=True)
    z  = Variable(id="Z",   name="Z",    initial_value=T, current_value=T, is_premise=True)

    conn = Connective(id="imp1", type="implication",
                      input_ids=["H_s", "M_s"], output_id="Z")

    model = build_model("mt", [hs, ms, z], [conn])
    ps = make_engine().run(model, verbose=True)

    assert hs.current_value == F, f"H(s) esperado F, es {val(hs)}"
    print(f"[PASS] Modus Tollens: H(s) = {val(hs)}")


def test_negation():
    _header("TEST 3: Negación directa  —  X=T  ⊢  ¬X=F")

    x = Variable(id="X", name="X", initial_value=T, current_value=T, is_premise=True)
    z = Variable(id="Z", name="¬X", initial_value=N, current_value=N)

    conn = Connective(id="neg1", type="negation", input_ids=["X"], output_id="Z")
    model = build_model("neg", [x, z], [conn])
    ps = make_engine().run(model, verbose=True)

    assert z.current_value == F, f"¬T esperado F, es {val(z)}"
    print(f"[PASS] Negación: ¬T = {val(z)}")


def test_negation_backward():
    _header("TEST 4: Negación inversa  —  ¬X=T  ⊢  X=F")

    x = Variable(id="X", name="X", initial_value=N, current_value=N)
    z = Variable(id="Z", name="¬X", initial_value=T, current_value=T, is_premise=True)

    conn = Connective(id="neg1", type="negation", input_ids=["X"], output_id="Z")
    model = build_model("neg_back", [x, z], [conn])
    ps = make_engine().run(model, verbose=True)

    assert x.current_value == F, f"X esperado F, es {val(x)}"
    print(f"[PASS] Negación inversa: X = {val(x)}")


def test_conjunction_forward():
    _header("TEST 5: Conjunción  (Prop 16)  —  X∧Y=T  ⊢  X=T, Y=T")

    x = Variable(id="X", name="X", initial_value=N, current_value=N)
    y = Variable(id="Y", name="Y", initial_value=N, current_value=N)
    z = Variable(id="Z", name="X∧Y", initial_value=T, current_value=T, is_premise=True)

    conn = Connective(id="and1", type="conjunction", input_ids=["X", "Y"], output_id="Z")
    model = build_model("and_fwd", [x, y, z], [conn])
    ps = make_engine().run(model, verbose=True)

    assert x.current_value == T, f"X esperado T, es {val(x)}"
    assert y.current_value == T, f"Y esperado T, es {val(y)}"
    print(f"[PASS] Conjunción Z=T → X={val(x)}, Y={val(y)}")


def test_disjunction_negative():
    _header("TEST 6: Disyunción  (Prop 19)  —  X∨Y=F  ⊢  X=F, Y=F")

    x = Variable(id="X", name="X", initial_value=N, current_value=N)
    y = Variable(id="Y", name="Y", initial_value=N, current_value=N)
    z = Variable(id="Z", name="X∨Y", initial_value=F, current_value=F, is_premise=True)

    conn = Connective(id="or1", type="disjunction", input_ids=["X", "Y"], output_id="Z")
    model = build_model("or_neg", [x, y, z], [conn])
    ps = make_engine().run(model, verbose=True)

    assert x.current_value == F, f"X esperado F, es {val(x)}"
    assert y.current_value == F, f"Y esperado F, es {val(y)}"
    print(f"[PASS] Disyunción Z=F → X={val(x)}, Y={val(y)}")


def test_section32():
    _header(
        "TEST 7: Section 3.2  —  ∀x(B→A)=T, ∃x(¬C∧¬A)=T  ⊢  ¬C∧¬B=T"
    )

    Ca  = Variable(id="Ca",  name="C(a)",  initial_value=N, current_value=N)
    Aa  = Variable(id="Aa",  name="A(a)",  initial_value=N, current_value=N)
    Ba  = Variable(id="Ba",  name="B(a)",  initial_value=N, current_value=N)
    nCa = Variable(id="nCa", name="¬C(a)", initial_value=N, current_value=N)
    nAa = Variable(id="nAa", name="¬A(a)", initial_value=N, current_value=N)
    nBa = Variable(id="nBa", name="¬B(a)", initial_value=N, current_value=N)
    Y   = Variable(id="Y",   name="¬C∧¬A", initial_value=T, current_value=T, is_premise=True)
    Z1  = Variable(id="Z1",  name="B→A",   initial_value=T, current_value=T, is_premise=True)
    W   = Variable(id="W",   name="¬C∧¬B", initial_value=N, current_value=N)

    connectives = [
        Connective(id="c1", type="conjunction",  input_ids=["nCa", "nAa"], output_id="Y"),
        Connective(id="c2", type="negation",     input_ids=["Ca"],          output_id="nCa"),
        Connective(id="c3", type="negation",     input_ids=["Aa"],          output_id="nAa"),
        Connective(id="c4", type="implication",  input_ids=["Ba", "Aa"],   output_id="Z1"),
        Connective(id="c5", type="negation",     input_ids=["Ba"],          output_id="nBa"),
        Connective(id="c6", type="conjunction",  input_ids=["nCa", "nBa"], output_id="W"),
    ]

    variables = [Ca, Aa, Ba, nCa, nAa, nBa, Y, Z1, W]
    model = build_model("sec32", variables, connectives)
    ps = make_engine().run(model, verbose=True)

    assert ps.stable,              "Motor no estabilizó"
    assert W.current_value  == T,  f"W (conclusión) esperado T, es {val(W)}"
    assert Aa.current_value == F,  f"A(a) esperado F, es {val(Aa)}"
    assert Ba.current_value == F,  f"B(a) esperado F, es {val(Ba)}"
    assert nBa.current_value == T, f"¬B(a) esperado T, es {val(nBa)}"
    print(f"[PASS] Section 3.2: conclusión W = {val(W)} ✓")


if __name__ == "__main__":
    tests = [
        test_modus_ponens,
        test_modus_tollens,
        test_negation,
        test_negation_backward,
        test_conjunction_forward,
        test_disjunction_negative,
        test_section32,
    ]

    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {e}")
            import traceback; traceback.print_exc()
            failed += 1

    print(f"\n{'='*80}")
    print(f"  {passed} pasados  |  {failed} fallidos")
    print(f"{'='*80}")
