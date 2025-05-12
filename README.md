# Privacy-Preserving Record Linkage (PPRL) using MPyC

This project implements a **secure two-party record matching protocol** using [MPyC](https://github.com/lschoe/mpyc) (Multiparty Computation in Python). It allows two parties to compare patient records from separate datasets without revealing any sensitive information, such as patient IDs or intermediate match results.

Patients Unique Identifiers have been Anonymized for the purpose of this research project.

Only the **number of matching records** is revealed as an output, no other data is exposed.

## Features

- Secure matching of hashed patient IDs
- Zero-knowledge intermediate results
- Compatible with 2 or more parties (2 main + helper)
- Uses secure equality checks in MPyC
- Data length padding for privacy
- Simple and modular design

---

## Use Case

This prototype is ideal for research in:

- Privacy-preserving data integration
- Health data sharing (e.g. across hospitals)
- GDPR-compliant data linkage
- Secure record deduplication

---

## File Structure

```
ICareData/
│
├── run_match.py                     # Main MPC matching script
├── source1-request-encounter.xlsx  # Excel file for Party 0
├── source2-dispense.xlsx           # Excel file for Party 1
├── requirements.txt                # Python dependencies
└── README.md                       # You're reading this!
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/NarjissYouyou/ICareData.git
cd ICareData
```

### 2. Set up a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```
mpyc
pandas
openpyxl
```

---

# Running the MPC Protocol

This project runs a **2-party protocol** using the `--loopback` mode for local simulation. Both parties are executed in separate terminals or processes.

### Step 1: Start Party 0

```bash
python3 run_match.py -M2 -I0 --loopback
```

### Step 2: Start Party 1 (in another terminal)

```bash
python3 run_match.py -M2 -I1 --loopback
```

> You should see logs like `this is the pid:  0` and eventually the output:  
> `this is the match_count 4`

# Or Run

### Step 1: Start Party 0
```bash
./run.sh 
```


The number of matches computed should be revealed.

---

## 🛡️ Security Overview

| Feature                 | Description                                         |
|------------------------|-----------------------------------------------------|
| Secret Inputs          | Inputs shared using MPyC’s `mpc.input()`            |
| Output Restriction     | Only total match count is revealed                  |
| Dataset Length Privacy | Inputs are padded to hide true lengths              |
| Input Normalization    | SHA-256 hashing used to standardize IDs             |
| Honest-but-Curious     | Secure in the semi-honest adversary model           |

---

## 🔧 Customization

- To **match on other fields**, modify the data loading part of `run_match.py`.
- You can extend the code to include **fuzzy matching** using secure Dice similarity.
- Want to simulate with 3 parties (e.g. a helper)? Run with `-M3` and start a 3rd instance with `-I2`.

---


## Author

**Narjiss [Your Last Name]**  
Research Intern | Data Privacy & Secure Computation  
[University of Antwerp / Narjiss.youyou@student.uantwerpen.be]

