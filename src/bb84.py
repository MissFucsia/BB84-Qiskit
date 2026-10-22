import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# 1. SETUP INIZIALE
rng = np.random.default_rng()
bit_num = 20  # Numero di qubit inviati
qc = QuantumCircuit(bit_num, bit_num)

# Alice genera bit e basi casuali
abits = rng.integers(0, 2, size=bit_num) 
abase = rng.integers(0, 2, size=bit_num) 

# NB
# Z (codificata come 0): |0> bit 0, |1> bit 1
# X (codificata come 1): |+> bit 0, |-> bit 1

# il gate x cambia lo stato da |0> a |1>co
# il gate h trasforma lo stato da |0> in |+> e da |1> a |->

# 2. PREPARAZIONE DEGLI STATI (ALICE)
# in qiskit i qubit sono |0>
for n in range(bit_num):
    if abits[n] == 1:
        qc.x(n)      # Se il bit è 1, porta il qubit da |0> a |1>
    if abase[n] == 1:
        qc.h(n)      # Se la base è X (1), applica Hadamard. Quindi se il bit era |0> diventa |+> e se era |1> diventa |->

# Barriera per separare Alice da Bob
# Alice manda i qubit sul canale
qc.barrier()

# 3. RICEZIONE E MISURA (BOB)
# Bob sceglie le sue basi casualmente
bbase = rng.integers(0, 2, size=bit_num) 

for m in range(bit_num):
    if bbase[m] == 1:
        qc.h(m)      # Se Bob sceglie base X, ruota prima di misurare perche il computer quantisco legge solo la base Z
    # qc.measure(qubit_da_misurare, bit_classico_di_destinazione)
    # L'operazione distrugge la sovrapposizione e fissa il valore del qubit a 0 o 1
    qc.measure(m, m)

# 4. ESECUZIONE SUL SIMULATORE
backend = AerSimulator()
job = backend.run(qc, shots=1, memory=True)
result = job.result()

# Estrazione dei dati (invertiamo l'ordine dei bit per il little-endian di Qiskit)
bob_measurements = [int(b) for b in result.get_memory()[0][::-1]]

# 5. SETACCIAMENTO (SIFTING) E CALCOLO FEDELTÀ
chiave_alice = []
chiave_bob = []
match_count = 0

for i in range(bit_num):
    if abase[i] == bbase[i]: # Se le basi coincidono
        valore_alice = int(abits[i])
        valore_bob = bob_measurements[i]
        
        chiave_alice.append(valore_alice)
        chiave_bob.append(valore_bob)
        
        # Se anche i bit coincidono, incrementiamo il contatore per la Fidelity
        # Tecnicamente dato che non c'è Eve e sto usando un simulatore perfetto,
        # se le basi coincidono, coincidono anche i bit. Nella realtà potrebbero 
        # esserci errori dovuti a intercettazioni o a rumorederivante dai dispositivi hardware
        if valore_alice == valore_bob:
            match_count += 1

# 6. CALCOLO METRICHE
n_chiave = len(chiave_alice)
if n_chiave > 0:
    # Fidelity: percentuale di bit che coincidono tra Alice e Bob
    fidelity = match_count / n_chiave
    # Tasso di errore
    loss = 1 - fidelity
else:
    fidelity, loss = 0, 0

# 7. OUTPUT RISULTATI
print("--- DATI TRASMISSIONE ---")
print(f"Bit Alice:  {abits}")
print(f"Basi Alice: {abase}")
print(f"Basi Bob:   {bbase}")
print(f"Bit Bob:    {np.array(bob_measurements)}")

print("\n--- RISULTATO SIFTING ---")
print(f"Basi uguali trovate: {n_chiave} su {bit_num}")
print(f"Chiave Alice: {chiave_alice}")
print(f"Chiave Bob:   {chiave_bob}")

print("\n--- ANALISI SICUREZZA ---")
print(f"Fidelity: {fidelity:.2%} (Percentuale di bit corretti tra Alice e Bob)")
print(f"Loss (QBER): {loss:.2%} (Tasso di errore rilevato)")

if fidelity == 1.0:
    print("\nESITO: Successo! La chiave è sicura e pronta per l'uso.")
    print(f"Chiave finale: {chiave_alice}")
elif loss > 0.11:
    print("\nATTENZIONE: Tasso di errore troppo alto (>11%). Possibile intercettazione!")
else:
    print("\nESITO: Chiave generata con errori trascurabili (rumore di sistema).")

# Visualizzazione del circuito
print("\nGenerazione del grafico del circuito...")
fig = qc.draw("mpl")
fig.savefig("circuito_bb84.png", dpi=300)