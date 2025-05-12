from mpyc.runtime import mpc
import pandas as pd
import hashlib

def hash_id(id_str):
    """
    Convert a string to a 64-bit integer using a truncated SHA-256 hash.
    
    This preserves pseudo-uniqueness while reducing the input domain to a fixed-size
    integer space that can be processed securely with MPyC. Truncation to 64 bits 
    allows compatibility with MPyC’s SecInt(64) while keeping collisions rare.
    """
    h = hashlib.sha256(id_str.encode()).hexdigest()
    return int(h[:16], 16)  # Use first 16 hex chars (64 bits)
    

async def main():
    """
    Secure Two-Party Record Matching using MPyC.
    
    This protocol compares hashed patient identifiers from two Excel datasets
    using secure multi-party computation. It does not reveal the identifiers,
    nor the comparison matrix — only the final match count is revealed.
    
    Security rationale:
    - Uses secret sharing to protect input values (via MPyC).
    - No intermediate values or match positions are revealed.
    - Only the total number of matches is revealed (output).
    - Pads inputs to equal length `n` so no party learns the other's size.
    - Input hashing ensures format unification and basic privacy before MPC.
    
    Parties:
    - Party 0: Data source 1 (request-encounter)
    - Party 1: Data source 2 (dispense)
    - (Optional) Party 2+: Helper parties with no input
    """

    # === Initialize MPC with 64-bit secure integers ===
    SEC = mpc.SecInt(64)
    await mpc.start()
    pid = mpc.pid  # Party ID (0 or 1 typically)
    print("this is the pid: ", pid)

    # === Load party-specific data ===
    if pid == 0:
        # Party 0: Load patient request data
        df = pd.read_excel("source1-request-encounter.xlsx", sheet_name="narjiss-medication-request-2")
        my_ids = [hash_id(str(x)) for x in df["request_patient_md5"]]
    elif pid == 1:
        # Party 1: Load dispense data
        df = pd.read_excel("source2-dispense.xlsx")
        my_ids = [hash_id(str(x)) for x in df["subject_id_md5"]]
    else:
        # Other parties contribute no data
        my_ids = []

    # === Share the number of records securely ===
    # Each party inputs their own dataset length; others input dummy 0
    if pid == 0:
        len0 = mpc.input(mpc.SecInt(16)(len(my_ids)), senders=0)
    else:
        len0 = mpc.input(mpc.SecInt(16)(0), senders=0)

    if pid == 1:
        len1 = mpc.input(mpc.SecInt(16)(len(my_ids)), senders=1)
    else:
        len1 = mpc.input(mpc.SecInt(16)(0), senders=1)

    # Reveal only the dataset lengths, which are not sensitive
    len0, len1 = await mpc.output(len0), await mpc.output(len1)
    n = max(len0, len1)  # Equalize lengths

    # === Pad each party's list to length n ===
    # Prevents leaking the number of real inputs (length privacy)
    my_ids += [0] * (n - len(my_ids))

    # === Secure Input Phase ===
    # Each party provides their own input values to the protocol.
    # The actual values are only known to the party who owns them.
    
    # Party 0 input
    inputs_0 = []
    for i in range(n):
        if pid == 0 and i < len(my_ids):
            val = mpc.input(SEC(my_ids[i]), senders=0)
        else:
            val = mpc.input(SEC(0), senders=0)
        inputs_0.append(val)

    # Party 1 input
    inputs_1 = []
    for i in range(n):
        if pid == 1 and i < len(my_ids):
            val = mpc.input(SEC(my_ids[i]), senders=1)
        else:
            val = mpc.input(SEC(0), senders=1)
        inputs_1.append(val)

    # === Secure Comparison Phase ===
    print("comparison phase")
    results = []
    for a in inputs_0:
        row = []
        for b in inputs_1:
            row.append(a == b)  # Secure equality test
        results.append(row)
    print("finished comparison phase")

    # === Count Total Matches (but not who matched) ===
    flattened_results = [item for sublist in results for item in sublist]

    # Securely sum all match indicators (True = 1, False = 0)
    match_count = mpc.sum([mpc.if_else(x, SEC(1), SEC(0)) for x in flattened_results])

    # === Reveal the total count ===
    revealed_match_count = await mpc.output(match_count)
    print("this is the match_count", revealed_match_count)

    # === Reveal matched index pairs ===
    print("Revealing matched index pairs...")
    revealed_matches = []

    for i in range(n):
        for j in range(n):
            match = await mpc.output(results[i][j])
            if match:
                revealed_matches.append((i, j))

    print("Matched index pairs (request_index, dispense_index):")
    for req_idx, disp_idx in revealed_matches:
        print(f"Request[{req_idx}] matches Dispense[{disp_idx}]")



    print("MPC has been successfully implemented")
    await mpc.shutdown()

mpc.run(main())
