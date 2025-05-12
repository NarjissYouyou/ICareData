import pandas as pd
import random
from datetime import timedelta

# Load the Medication Request data
df_request = pd.read_excel("source1-request-encounter.xlsx", sheet_name="narjiss-medication-request-2")

# Sample N rows
sample_size = 10000
df_sample = df_request.sample(n=sample_size).copy()

# Add new dispense fields
df_sample['dispense_id'] = ['D' + str(i).zfill(4) for i in range(1, sample_size+1)]

# Random dispense dates: +1 to +10 days after prescription date
df_sample['dispensedate'] = df_sample['prescriptiondate'] + pd.to_timedelta(
    [random.randint(1, 10) for _ in range(sample_size)], unit='d'
)

df_sample['quantity'] = [random.choice([10, 30, 60]) for _ in range(sample_size)]
df_sample['dosage'] = random.choices(['1 tablet/day', '2 tablets/day', '5ml twice/day'], k=sample_size)

# Rename fields to match your desired structure
df_dispense = df_sample.rename(columns={
    'request_rid': 'request_rid',
    'request_patient_md5': 'subject_id_md5',
    'medication_code': 'medication_code',
    'Request_prescribe_md5': 'request_prescriber_md5'
})

# Select final columns
df_dispense = df_dispense[['dispense_id', 'request_rid', 'subject_id_md5', 'medication_code',
                           'dispensedate', 'quantity', 'dosage', 'request_prescriber_md5']]

# Save to Excel
df_dispense.to_excel("source2-dispense.xlsx", index=False)
