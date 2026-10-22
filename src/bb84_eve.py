import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister
from qiskit_aer import AerSimulator

# 1. SETUP INIZIALE
rng = np.random.default_rng()
bit_num = 20 # Numero di qubit inviati

# Creiamo due registri classici separati per poter analizzare i dati di entrambi
# cr_bob conterrà le misure finali di Bob, cr_eve quelle intercettate da Eve
cr_bob = ClassicalRegister(bit_num, name="bob")
cr_eve = ClassicalRegister(bit_num, name="eve")
qc = QuantumCircuit(bit_num)
qc.add_register(cr_bob)
qc.add_register(cr_eve)

# Alice genera bit e basi casuali
# rng.integers(0, 2) genera 0 o 1 (il 2 è escluso)
abits = rng.integers(0, 2, size=bit_num) 
abase = rng.integers(0, 2, size=bit_num) 

# NB Codifica:
# Base Z (0): |0> bit 0, |1> bit 1
# Base X (1): |+> bit 0, |-> bit 1

# 2. PREPARAZIONE DI ALICE
for n in range(bit_num):
    if abits[n] == 1:
        qc.x(n)      # Se il bit è 1, porta il qubit da |0> a |1> (Porta Pauli-X)
    if abase[n] == 1:
        qc.h(n)      # Se la base è X, applica Hadamard per creare la sovrapposizione:
                     # |0> diventa |+> e |1> diventa |->

# Barriera per separare Alice dal canale di comunicazione
qc.barrier()

# 3. INTERCETTAZIONE (EVE)
# Eve non sa quali basi ha usato Alice, quindi sceglie casualmente
ebase = rng.integers(0, 2, size=bit_num) 

for e in range(bit_num):
    if ebase[e] == 1:
        qc.h(e) # Se sceglie base X, applica Hadamard prima di misurare
    
    # Eve misura il qubit e salva nel suo registro dedicato 'cr_eve'
    # Questa operazione distrugge lo stato quantistico originale (collasso)
    qc.measure(e, cr_eve[e]) 
    
    # Dopo la misura, Eve deve "preparare" di nuovo il qubit per Bob.
    # Se aveva usato la base X, deve riportarlo in quella base prima di mandarlo.
    if ebase[e] == 1:
        qc.h(e) 

qc.barrier() # I qubit (ormai disturbati da Eve) proseguono verso Bob

# 4. RICEZIONE DI BOB
# Bob sceglie le sue basi casualmente
bbase = rng.integers(0, 2, size=bit_num) 

for m in range(bit_num):
    if bbase[m] == 1:
        # Se Bob sceglie base X, ruota il qubit con H per poterlo misurare lungo l'asse Z
        qc.h(m)
    
    # Misura finale: il qubit collassa e il valore (0 o 1) viene scritto nel registro di Bob
    qc.measure(m, cr_bob[m])

# 5. ESECUZIONE E ESTRAZIONE DATI
backend = AerSimulator()
job = backend.run(qc, shots=1, memory=True)
result_str = job.result().get_memory()[0]

# Estraiamo i bit dai registri (Qiskit li separa con uno spazio nella stringa memory)
# Invertiamo le stringhe [::-1] perché Qiskit numera i bit da destra a sinistra
raw_bits = result_str.split()
bob_measurements = [int(b) for b in raw_bits[1][::-1]]
eve_measurements = [int(b) for b in raw_bits[0][::-1]]

# 6. SETACCIAMENTO (SIFTING)
chiave_alice = []
chiave_bob = []
chiave_eve = []
match_count = 0

for i in range(bit_num):
    if abase[i] == bbase[i]: # Se le basi di Alice e Bob coincidono
        valore_alice = int(abits[i])
        valore_bob = bob_measurements[i]
        
        chiave_alice.append(valore_alice)
        chiave_bob.append(valore_bob)
        # Salviamo anche cosa ha intercettato Eve in queste posizioni
        chiave_eve.append(eve_measurements[i])
        
        # Se anche i bit coincidono, incrementiamo per la Fidelity
        # Con Eve, qui troveremo errori anche se le basi coincidono!
        if valore_alice == valore_bob:
            match_count += 1

# 7. ANALISI DEI RISULTATI
n_chiave = len(chiave_alice)
if n_chiave > 0:
    fidelity = match_count / n_chiave
    loss = 1 - fidelity # QBER (Quantum Bit Error Rate)
else:
    fidelity, loss = 0, 0

# 8. OUTPUT A VIDEO
print("--- DATI TRASMISSIONE ---")
print(f"Bit trasmessi da Alice:  {abits}")
print(f"Basi scelte da Alice: {abase}")
print(f"Basi scelte Bob:   {bbase}")
print(f"Bit letti da Bob:    {np.array(bob_measurements)}")

print("\n--- ANALISI INTERCETTAZIONE ---")
print(f"Basi scelte da Eve:   {ebase}")
print(f"Bit letti da Eve: {np.array(eve_measurements)}")
print(f"Chiave di Eve:    {chiave_eve}")

print("\n--- RISULTATO SIFTING ---")
print(f"Basi uguali trovate: {n_chiave} su {bit_num}")
print(f"Chiave di Alice: {chiave_alice}")
print(f"Chiave di Bob:   {chiave_bob}")

print("\n--- ANALISI SICUREZZA ---")
print(f"Fidelity: {fidelity:.2%} (Percentuale di bit corretti tra Alice e Bob)")
print(f"Loss (QBER): {loss:.2%} (Tasso di errore rilevato)")

if loss > 0.11:
    print("\nATTENZIONE: Possibile presenza di Eve! Il tasso di errore supera l'11%.")
else:
    print("\nESITO: Canale sicuro (rumore trascurabile).")
    print(f"Chiave finale: {chiave_alice}")
    chiave_bob = chiave_alice
    
# Visualizzazione del circuito
print("\nGenerazione del grafico del circuito...")
fig = qc.draw("mpl")
fig.savefig("circuito_eve_bb84.png", dpi=300)