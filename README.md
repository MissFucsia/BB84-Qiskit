# Simulazione e Analisi di Sicurezza del Protocollo BB84 in Qiskit

Progetto per l'insegnamento di **Crittografia**  
Università degli Studi di Milano  
Anno Accademico: *2025/2026*  
Autrice: **Marta Finazzi**

---

## 📌 Panoramica

A differenza della crittografia asimmetrica classica (es. RSA o ECC), vulnerabile all'algoritmo di Shor su computer quantistici su larga scala, il protocollo **BB84** (Bennett & Brassard, 1984) fonda la propria sicurezza sulle leggi fisiche della meccanica quantistica e sul **Teorema di Non-Clonazione**.

In questo progetto vengono analizzati:
1. Lo scambio ideale privo di disturbi tra Alice e Bob (canale noise-free ideale).
2. L'interferenza provocata da un ascoltatore attivo (**Eve**) tramite un attacco *Intercept-Resend*, con conseguente collasso della funzione d'onda.
3. La rilevazione statistica dell'intrusione confrontando il **QBER (Quantum Bit Error Rate)** rispetto alla soglia convenzionale di sicurezza fissata all'**11%**.
4. Lo studio empirico delle fluttuazioni statistiche e dei falsi negativi al variare della taglia del campione ($N = 20, 100, 1000$).

---

## 🔬 Dettagli di Implementazione

L'infrastruttura di simulazione fa uso di **Qiskit** ed **AerSimulator**:

* **Preparazione degli stati (Alice)**:
  * Base Rettilinea ($Z$): $\vert{}0\rangle$ (Bit 0) e porta $X \to \vert{}1\rangle$ (Bit 1).
  * Base Diagonale ($X$): applicazione del gate di Hadamard $H \to \vert{}+\rangle$ (Bit 0) o $X + H \to \vert{}-\rangle$ (Bit 1).
* **Intercettazione (Eve)**:
  * Misura intermedia lungo basi casuali e reinvio del fotone collassato verso Bob.
* **Misurazione (Bob)**:
  * Rotazione tramite gate $H$ qualora la base scelta sia quella diagonale, prima della lettura computazionale in base $Z$.
* **Sifting & Metriche**:
  * Setacciamento classico delle basi scambiate su canale pubblico.
  * Calcolo di **Fidelity** e **QBER** ($Loss = 1 - Fidelity$).

---

## 📊 Risultati e Convergenza Statistica

| Taglia Campione ($N$) | QBER Medio (con Eve) | Deviazione Standard | Comportamento Rilevato |
| :---: | :---: | :---: | :--- |
| **20 bit** | 21.40% | 0.0838 | Forte dispersione; rischio di falsi negativi ($QBER < 11\%$). |
| **100 bit** | 22.08% | 0.0776 | Riduzione progressiva della varianza. |
| **1000 bit** | **25.14%** | **0.0169** | Convergenza quasi perfetta al valore teorico atteso del **25%**. |

L'analisi sperimentale dimostra visivamente (tramite Box Plot) che su larga scala la distinzione tra rumore di fondo e intercettazione attiva è matematicamente garantita, annullando il rischio di falsi negativi dovuti a fluttuazioni stocastiche.
