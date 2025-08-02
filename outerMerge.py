import pandas as pd

oldAgencies = pd.read_csv(r'C:\Users\nicol\Desktop\URSUSdata\Agency 5.csv')
currentAgencies = pd.read_csv(r'C:\Users\nicol\Desktop\URSUSdata\UseofForce_ORI-Agency_Names_2024.csv')

missingAgencies = pd.merge(oldAgencies, currentAgencies, on='ORI', how='outer')

missingAgencies['missing_from_agency5'] = missingAgencies['URSUS Agency Name'].isna()

missingAgencies.to_csv('missingAgencies.csv', index=False)
