"""
Tests avanzados del EPiC Engine.

  TEST 8:  Cadena de implicaciones  (A→B→C→D→E)
  TEST 9:  Silogismo disyuntivo encadenado
  TEST 10: Evidencia contradictoria (valor B)
  TEST 11: Ley de De Morgan verificada bidireccionalmente
  TEST 12: Dilema constructivo
  TEST 13: Razonamiento hipotético con premisas mixtas
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor.dominio.modelos import Variable, Connective, EPiCModel
from motor.algoritmos.constantes import N, T, F, B, VALUE_NAMES
from motor.algoritmos.engine import EPiCEngine

def make_engine():
    return EPiCEngine(max_iterations=1000)

def build_model(model_id, variables, connectives):
    return EPiCModel(id=model_id, variables=variables, connectives=connectives)

def val(var):
    return VALUE_NAMES[var.current_value]

def _header(test_num, title, description):
    print("\n" + "█" * 80)
    print(f"  TEST {test_num}: {title}")
    print(f"  {description}")
    print("█" * 80)


def test_implication_chain():
    _header(8,
        "Cadena de implicaciones  A→B→C→D→E",
        "Premisas: A=T, A→B=T, B→C=T, C→D=T, D→E=T  ⊢  B=T, C=T, D=T, E=T")

    A = Variable(id="A", name="A", initial_value=T, current_value=T, is_premise=True)
    B = Variable(id="B", name="B", initial_value=N, current_value=N)
    C = Variable(id="C", name="C", initial_value=N, current_value=N)
    D = Variable(id="D", name="D", initial_value=N, current_value=N)
    E = Variable(id="E", name="E", initial_value=N, current_value=N)

    Z1 = Variable(id="Z1", name="A→B", initial_value=T, current_value=T, is_premise=True)
    Z2 = Variable(id="Z2", name="B→C", initial_value=T, current_value=T, is_premise=True)
    Z3 = Variable(id="Z3", name="C→D", initial_value=T, current_value=T, is_premise=True)
    Z4 = Variable(id="Z4", name="D→E", initial_value=T, current_value=T, is_premise=True)

    connectives = [
        Connective(id="i1", type="implication", input_ids=["A", "B"],  output_id="Z1"),
        Connective(id="i2", type="implication", input_ids=["B", "C"],  output_id="Z2"),
        Connective(id="i3", type="implication", input_ids=["C", "D"],  output_id="Z3"),
        Connective(id="i4", type="implication", input_ids=["D", "E"],  output_id="Z4"),
    ]

    model = build_model("chain", [A, B, C, D, E, Z1, Z2, Z3, Z4], connectives)
    ps = make_engine().run(model, verbose=True)

    assert ps.stable,          "Motor no estabilizó"
    assert B.current_value == T, f"B esperado T, es {val(B)}"
    assert C.current_value == T, f"C esperado T, es {val(C)}"
    assert D.current_value == T, f"D esperado T, es {val(D)}"
    assert E.current_value == T, f"E esperado T, es {val(E)}"
    print(f"[PASS] Cadena: A={val(A)} → B={val(B)} → C={val(C)} → D={val(D)} → E={val(E)}")


def test_disjunctive_syllogism():
    _header(9,
        "Silogismo disyuntivo",
        "Premisas: P∨Q=T, P=F  ⊢  Q=T  (eliminación del disyunto falso)")

    P  = Variable(id="P",  name="P",   initial_value=F, current_value=F, is_premise=True)
    Q  = Variable(id="Q",  name="Q",   initial_value=N, current_value=N)
    PQ = Variable(id="PQ", name="P∨Q", initial_value=T, current_value=T, is_premise=True)

    connectives = [
        Connective(id="c_or", type="disjunction", input_ids=["P", "Q"], output_id="PQ"),
    ]

    model = build_model("disj_syl", [P, Q, PQ], connectives)
    ps = make_engine().run(model, verbose=True)

    assert ps.stable,            "Motor no estabilizó"
    assert Q.current_value == T, f"Q esperado T, es {val(Q)}"
    print(f"[PASS] Silogismo disyuntivo: P={val(P)}, P∨Q=T  ⊢  Q = {val(Q)}")


def test_contradictory_evidence():
    _header(10,
        "Evidencia contradictoria — valor B (Both/inconsistente)",
        "X=B (premisa) → ¬X=B → Z=X∧¬X=B  (inconsistencia propagada)")

    X  = Variable(id="X",  name="X",    initial_value=B, current_value=B, is_premise=True)
    nX = Variable(id="nX", name="¬X",   initial_value=N, current_value=N)
    Z  = Variable(id="Z",  name="X∧¬X", initial_value=N, current_value=N)

    connectives = [
        Connective(id="neg1", type="negation",    input_ids=["X"],        output_id="nX"),
        Connective(id="and1", type="conjunction", input_ids=["X", "nX"],  output_id="Z"),
    ]

    model = build_model("contra", [X, nX, Z], connectives)
    ps = make_engine().run(model, verbose=True)

    assert ps.stable,             "Motor no estabilizó"
    assert nX.current_value == B, f"¬X esperado B, es {val(nX)}"
    assert Z.current_value  == B, f"Z esperado B, es {val(Z)}"
    print(f"[PASS] Evidencia contradictoria: ¬X={val(nX)}, X∧¬X = {val(Z)}  ✓")


def test_de_morgan():
    _header(11,
        "Ley de De Morgan  ¬(P∧Q) ↔ (¬P∨¬Q)",
        "P=T, Q=F  ⊢  ¬(P∧Q)=T  y  ¬P∨¬Q=T  (deben coincidir)")

    P    = Variable(id="P",    name="P",       initial_value=T, current_value=T, is_premise=True)
    Q    = Variable(id="Q",    name="Q",       initial_value=F, current_value=F, is_premise=True)
    nP   = Variable(id="nP",   name="¬P",      initial_value=N, current_value=N)
    nQ   = Variable(id="nQ",   name="¬Q",      initial_value=N, current_value=N)
    PaQ  = Variable(id="PaQ",  name="P∧Q",     initial_value=N, current_value=N)
    nPaQ = Variable(id="nPaQ", name="¬(P∧Q)",  initial_value=N, current_value=N)
    nPoQ = Variable(id="nPoQ", name="¬P∨¬Q",   initial_value=N, current_value=N)

    connectives = [
        Connective(id="neg_p",  type="negation",    input_ids=["P"],          output_id="nP"),
        Connective(id="neg_q",  type="negation",    input_ids=["Q"],          output_id="nQ"),
        Connective(id="and_pq", type="conjunction", input_ids=["P",  "Q"],    output_id="PaQ"),
        Connective(id="neg_pq", type="negation",    input_ids=["PaQ"],        output_id="nPaQ"),
        Connective(id="or_npq", type="disjunction", input_ids=["nP", "nQ"],   output_id="nPoQ"),
    ]

    variables = [P, Q, nP, nQ, PaQ, nPaQ, nPoQ]
    model = build_model("demorgan", variables, connectives)
    ps = make_engine().run(model, verbose=True)

    assert ps.stable,               "Motor no estabilizó"
    assert PaQ.current_value  == F, f"P∧Q esperado F, es {val(PaQ)}"
    assert nPaQ.current_value == T, f"¬(P∧Q) esperado T, es {val(nPaQ)}"
    assert nP.current_value   == F, f"¬P esperado F, es {val(nP)}"
    assert nQ.current_value   == T, f"¬Q esperado T, es {val(nQ)}"
    assert nPoQ.current_value == T, f"¬P∨¬Q esperado T, es {val(nPoQ)}"
    assert nPaQ.current_value == nPoQ.current_value, \
        f"De Morgan falla: ¬(P∧Q)={val(nPaQ)} ≠ ¬P∨¬Q={val(nPoQ)}"
    print(f"[PASS] De Morgan: ¬(P∧Q)={val(nPaQ)} = ¬P∨¬Q={val(nPoQ)}  ✓")


def test_constructive_dilemma():
    _header(12,
        "Dilema constructivo",
        "Premisas: P=B, (P→Q)=T, (R→S)=T, (P∨R)=T  ⊢  (Q∨S)=T")

    P    = Variable(id="P",    name="P",    initial_value=B, current_value=B, is_premise=True)
    Q    = Variable(id="Q",    name="Q",    initial_value=N, current_value=N)
    R    = Variable(id="R",    name="R",    initial_value=N, current_value=N)
    S    = Variable(id="S",    name="S",    initial_value=N, current_value=N)
    PQ   = Variable(id="PQ",   name="P→Q",  initial_value=T, current_value=T, is_premise=True)
    RS   = Variable(id="RS",   name="R→S",  initial_value=T, current_value=T, is_premise=True)
    PorR = Variable(id="PorR", name="P∨R",  initial_value=T, current_value=T, is_premise=True)
    QorS = Variable(id="QorS", name="Q∨S",  initial_value=N, current_value=N)

    connectives = [
        Connective(id="i_pq",   type="implication", input_ids=["P", "Q"],    output_id="PQ"),
        Connective(id="i_rs",   type="implication", input_ids=["R", "S"],    output_id="RS"),
        Connective(id="o_pr",   type="disjunction", input_ids=["P", "R"],    output_id="PorR"),
        Connective(id="o_qs",   type="disjunction", input_ids=["Q", "S"],    output_id="QorS"),
    ]

    variables = [P, Q, R, S, PQ, RS, PorR, QorS]
    model = build_model("dilemma", variables, connectives)
    ps = make_engine().run(model, verbose=True)

    assert ps.stable,               "Motor no estabilizó"
    assert QorS.current_value == T, f"Q∨S esperado T, es {val(QorS)}"
    print(f"[PASS] Dilema constructivo: Q={val(Q)}, S={val(S)}, Q∨S = {val(QorS)}  ✓")


def test_medical_reasoning():
    _header(13,
        "Razonamiento hipotético encadenado — escenario médico",
        "S1=T, S2=T, S1∧S2→E=T, E→Tx=T, Tx→R=T, ¬E∨Prev=T  ⊢  E=T, Tx=T, R=T, Prev=T")

    S1   = Variable(id="S1",   name="Fiebre",       initial_value=T, current_value=T, is_premise=True)
    S2   = Variable(id="S2",   name="Tos",          initial_value=T, current_value=T, is_premise=True)
    Sc   = Variable(id="Sc",   name="S1∧S2",        initial_value=N, current_value=N)
    E    = Variable(id="E",    name="Enfermedad",   initial_value=N, current_value=N)
    nE   = Variable(id="nE",   name="¬Enfermedad",  initial_value=N, current_value=N)
    Tx   = Variable(id="Tx",   name="Tratamiento",  initial_value=N, current_value=N)
    R    = Variable(id="R",    name="Recuperación", initial_value=N, current_value=N)
    Prev = Variable(id="Prev", name="Preventivo",   initial_value=N, current_value=N)

    Z_sc  = Variable(id="Z_sc",  name="Sc→E",     initial_value=T, current_value=T, is_premise=True)
    Z_etx = Variable(id="Z_etx", name="E→Tx",     initial_value=T, current_value=T, is_premise=True)
    Z_txr = Variable(id="Z_txr", name="Tx→R",     initial_value=T, current_value=T, is_premise=True)
    Z_prt = Variable(id="Z_prt", name="¬E∨Prev",  initial_value=T, current_value=T, is_premise=True)

    connectives = [
        Connective(id="c_and",  type="conjunction", input_ids=["S1", "S2"],   output_id="Sc"),
        Connective(id="c_diag", type="implication", input_ids=["Sc", "E"],    output_id="Z_sc"),
        Connective(id="c_neg",  type="negation",    input_ids=["E"],          output_id="nE"),
        Connective(id="c_tx",   type="implication", input_ids=["E",  "Tx"],   output_id="Z_etx"),
        Connective(id="c_rec",  type="implication", input_ids=["Tx", "R"],    output_id="Z_txr"),
        Connective(id="c_prt",  type="disjunction", input_ids=["nE", "Prev"], output_id="Z_prt"),
    ]

    variables = [S1, S2, Sc, E, nE, Tx, R, Prev, Z_sc, Z_etx, Z_txr, Z_prt]
    model = build_model("medical", variables, connectives)
    ps = make_engine().run(model, verbose=True)

    assert ps.stable,              "Motor no estabilizó"
    assert Sc.current_value  == T, f"S1∧S2 esperado T, es {val(Sc)}"
    assert E.current_value   == T, f"Enfermedad esperado T, es {val(E)}"
    assert Tx.current_value  == T, f"Tratamiento esperado T, es {val(Tx)}"
    assert R.current_value   == T, f"Recuperación esperado T, es {val(R)}"
    assert Prev.current_value== T, f"Preventivo esperado T, es {val(Prev)}"
    print(f"[PASS] Médico: E={val(E)}, Tx={val(Tx)}, R={val(R)}, Prev={val(Prev)}  ✓")


if __name__ == "__main__":
    tests = [
        test_implication_chain,
        test_disjunctive_syllogism,
        test_contradictory_evidence,
        test_de_morgan,
        test_constructive_dilemma,
        test_medical_reasoning,
    ]

    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {t.__name__}: {e}")
            import traceback; traceback.print_exc()
            failed += 1

    print(f"\n{'═'*80}")
    print(f"  {passed} pasados  |  {failed} fallidos")
    print(f"{'═'*80}")
