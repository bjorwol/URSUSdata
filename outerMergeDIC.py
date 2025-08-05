import pandas as pd

dic_df = pd.read_excel('/Users/bjorwol/Downloads/URSUSdata-main/DIC_PRA_Rusch_07172025.xlsx', sheet_name='Statewide', engine='openpyxl')
dic_df.to_csv('/Users/bjorwol/Downloads/URSUSdata-main/DIC_clean.csv', index=False)


dic_df = pd.read_csv('/Users/bjorwol/Downloads/URSUSdata-main/DIC_clean.csv')
agency_df = pd.read_csv('/Users/bjorwol/Downloads/URSUSdata-main/Agency 5.csv')

dic_df['agency_number'] = dic_df['agency_number'].astype(str)
agency_df['NCIC'] = agency_df['NCIC'].astype(str)

merged_df = pd.merge(dic_df, agency_df, left_on='agency_number', right_on='NCIC', how='outer')
merged_df['missing_from_agency5'] = merged_df['URSUS Agency Name'].isna()

merged_df.to_csv('/Users/bjorwol/Downloads/URSUSdata-main/dic_merged_with_agency5.csv', index=False)

missing_only = merged_df[merged_df['missing_from_agency5'] == True]
missing_only.to_csv('/Users/bjorwol/Downloads/URSUSdata-main/dic_missing_only.csv', index=False)

print(f"found {len(missing_only)} DIC agencies that aren't in Agency5.")



