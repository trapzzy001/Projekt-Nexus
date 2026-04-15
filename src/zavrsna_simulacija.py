import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
import requests

df_lokacije = pd.read_csv('mars_lokacije.csv', sep=';')
df_uzorci = pd.read_csv('mars_uzorci.csv', sep=';')

df = pd.merge(df_lokacije, df_uzorci, on='ID_Uzorka')

df['Temp_Tla_C'] = pd.to_numeric(df['Temp_Tla_C'], errors='coerce')
df['H2O_Postotak'] = pd.to_numeric(df['H2O_Postotak'], errors='coerce')


anomalije = df[(df['Temp_Tla_C'] < -273) | (df['H2O_Postotak'] < 0) | (df['H2O_Postotak'] > 100)]
df_cisto = df.drop(anomalije.index).reset_index(drop=True)

df_anomalije = anomalije[['ID_Uzorka', 'GPS_LONG', 'GPS_LAT', 'Temp_Tla_C', 'H2O_Postotak']]
df_anomalije.to_csv('anomalije_izvjestaj.csv', index=False)

df_cisto['Dubina_Busenja_cm'] = df_cisto['Dubina_Busenja_cm'].astype(str).str.replace(',', '.').astype(float)

df_cisto['GPS_LONG'] = df_cisto['GPS_LONG'].astype(str).str.replace(',', '.').astype(float)
df_cisto['GPS_LAT'] = df_cisto['GPS_LAT'].astype(str).str.replace(',', '.').astype(float)


plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_cisto, x='Temp_Tla_C', y='H2O_Postotak', hue='Metan_Senzor')
plt.savefig('graph1_temp_h2o.png')

plt.figure(figsize=(10, 6))
plt.scatter(df_cisto['GPS_LONG'], df_cisto['GPS_LAT'], c=df_cisto['Dubina_Busenja_cm'], cmap='viridis')
plt.colorbar(label='Dubina')
plt.savefig('graph2_heatmap_depth.png')

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_cisto, x='GPS_LONG', y='GPS_LAT', hue='Metan_Senzor', palette={True: 'red', False: 'blue'})
plt.savefig('graph3_methane_scatter.png')

kandidati = df_cisto[(df_cisto['metan'] == True) & (df_cisto['organske_molekule'] == True)]

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_cisto, x='GPS_LONG', y='GPS_LAT', hue='H2O_Postotak', alpha=0.5)
plt.scatter(kandidati['GPS_LONG'], kandidati['GPS_LAT'], marker='*', s=250, color='red')
plt.savefig('scatter_plot.png')

plt.figure(figsize=(12, 8))
extent_koordinate = [df_cisto['GPS_LONG'].min(), df_cisto['GPS_LONG'].max(), df_cisto['GPS_LAT'].min(), df_cisto['GPS_LAT'].max()]

try:
    slika_kratera = plt.imread('jezero_crater_satellite_map.jpg')
    plt.imshow(slika_kratera, extent=extent_koordinate, aspect='auto', alpha=0.7)
    sns.scatterplot(data=df_cisto, x='GPS_LONG', y='GPS_LAT', alpha=0.4, color='white')
    plt.scatter(kandidati['GPS_LONG'], kandidati['GPS_LAT'], marker='X', color='lime', s=100)
    plt.savefig('jezero_mission_map.jpg')
except:
    pass

lista_naloga = []
for index, redak in kandidati.iterrows():
    lista_naloga.append({
        "ID_Uzorka": int(redak['ID_Uzorka']),
        "koordinate": {"lat": redak['GPS_LAT'], "long": redak['GPS_LONG']},
        "operacije": ["NAVIGACIJA", "SONDIRANJE", "SLANJE_PODATAKA"]
    })

finalni_payload = {"misija": "Nexus", "nalozi": lista_naloga}

with open('nalog_za_robot.json', 'w') as f:
    json.dump(finalni_payload, f, indent=4)

try:
    requests.post("", json=finalni_payload)
except:
    print("JSON spremljen lokalno.")
