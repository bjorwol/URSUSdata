import pandas as pd

oldAgencies = pd.read_csv(r'C:\Users\nicol\Desktop\URSUSdata\Agency 5.csv')
currentAgencies = pd.read_csv(r'C:\Users\nicol\Desktop\URSUSdata\UseofForce_ORI-Agency_Names_2024.csv')

result = pd.merge(oldAgencies, currentAgencies, how='outer')

result.to_excel('result.xlsx', index=False)
