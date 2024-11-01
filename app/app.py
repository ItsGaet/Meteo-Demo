import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

# Funzione per ottenere le coordinate della città
def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&addressdetails=1&limit=1"
    headers = {
        'User-Agent': 'YourAppName/1.0 (your_email@example.com)'  # Cambia con il nome della tua app e la tua email
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            st.error("Città non trovata. Controlla il nome e riprova.")
            return None, None
    else:
        st.error(f"Errore nella richiesta: {response.status_code}")
        return None, None

# Funzione per ottenere i dati meteo e qualità dell'aria
def get_weather_data(lat, lon):
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relative_humidity_2m"
    air_quality_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=pm10,pm2_5,carbon_monoxide,ozone"

    weather_response = requests.get(weather_url)
    air_quality_response = requests.get(air_quality_url)

    if weather_response.status_code == 200 and air_quality_response.status_code == 200:
        weather_data = weather_response.json()
        air_quality_data = air_quality_response.json()
        return weather_data, air_quality_data
    else:
        st.error("Impossibile ottenere i dati dal server.")
        return None, None

# Funzione per determinare il colore in base alla qualità dell'aria
def get_air_quality_color(value, pollutant):
    if pollutant == 'pm10':
        if value <= 50:
            return 'green'
        elif value <= 100:
            return 'yellow'
        else:
            return 'red'
    elif pollutant == 'pm2_5':
        if value <= 35:
            return 'green'
        elif value <= 75:
            return 'yellow'
        else:
            return 'red'
    elif pollutant == 'carbon_monoxide':
        if value <= 1000:
            return 'green'
        elif value <= 2000:
            return 'yellow'
        else:
            return 'red'
    elif pollutant == 'ozone':
        if value <= 180:
            return 'green'
        elif value <= 240:
            return 'yellow'
        else:
            return 'red'
    return 'gray'  # valore di default

# Titolo dell'app
st.set_page_config(page_title="Meteo e Qualità dell'Aria", page_icon="🌍", layout="wide")
st.title("Meteo e Qualità dell'Aria 🌍")

# Barra di ricerca per il nome della città
city = st.text_input("Inserisci il nome della città:", "")

if city:
    lat, lon = get_coordinates(city)
    if lat and lon:
        # Creazione della mappa aggiornata
        mappa = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], popup=f"{city}").add_to(mappa)

        # Layout a colonne per mappa e risultati
        col1, col2 = st.columns([3, 2])  # Maggiore larghezza per la mappa

        with col1:
            st_folium(mappa, width=500, height=400)

        with col2:
            weather_data, air_quality_data = get_weather_data(lat, lon)

            if weather_data and air_quality_data:
                st.subheader("Dati Meteo Correnti")
                current_weather = weather_data.get('current_weather', {})
                st.write(f"🌡️ **Temperatura**: {current_weather.get('temperature', 'N/A')}°C")
                st.write(f"💧 **Umidità**: {current_weather.get('relative_humidity', 'N/A')}%")
                st.write(f"🌬️ **Velocità del Vento**: {current_weather.get('windspeed', 'N/A')} km/h")

                st.subheader("Qualità dell'Aria Corrente")
                air_quality = air_quality_data['hourly']
                pm10_value = air_quality['pm10'][0]
                pm2_5_value = air_quality['pm2_5'][0]
                carbon_monoxide_value = air_quality['carbon_monoxide'][0]
                ozone_value = air_quality['ozone'][0]

                # Mostra i valori con colori
                st.write(f"🌫️ **PM10**: {pm10_value} µg/m³", 
                         f"<span style='color:{get_air_quality_color(pm10_value, 'pm10')}'>●</span>", unsafe_allow_html=True)
                st.write(f"🌫️ **PM2.5**: {pm2_5_value} µg/m³", 
                         f"<span style='color:{get_air_quality_color(pm2_5_value, 'pm2_5')}'>●</span>", unsafe_allow_html=True)
                st.write(f"🌫️ **Monossido di Carbonio**: {carbon_monoxide_value} µg/m³", 
                         f"<span style='color:{get_air_quality_color(carbon_monoxide_value, 'carbon_monoxide')}'>●</span>", unsafe_allow_html=True)
                st.write(f"🌫️ **Ozono**: {ozone_value} µg/m³", 
                         f"<span style='color:{get_air_quality_color(ozone_value, 'ozone')}'>●</span>", unsafe_allow_html=True)

                with st.expander("Mostra Grafici Avanzati", expanded=False):
                    # Creazione di un DataFrame per i dati di qualità dell'aria
                    timestamps = air_quality_data['hourly']['time']
                    pm10 = air_quality['pm10']
                    pm2_5 = air_quality['pm2_5']
                    carbon_monoxide = air_quality['carbon_monoxide']
                    ozone = air_quality['ozone']

                    # Crea un DataFrame per i grafici
                    df = pd.DataFrame({
                        'Timestamp': pd.to_datetime(timestamps),
                        'PM10 (µg/m³)': pm10,
                        'PM2.5 (µg/m³)': pm2_5,
                        'CO (µg/m³)': carbon_monoxide,
                        'Ozone (µg/m³)': ozone,
                    })

                    # Imposta il timestamp come indice
                    df.set_index('Timestamp', inplace=True)

                    # Grafico area per PM10 e PM2.5
                    st.subheader("Grafico Area per PM10 e PM2.5")
                    st.area_chart(df[['PM10 (µg/m³)', 'PM2.5 (µg/m³)']], use_container_width=True)

                    # Grafico a barre per CO e Ozono
                    st.subheader("Grafico a Barre per CO e Ozono")
                    st.bar_chart(df[['CO (µg/m³)', 'Ozone (µg/m³)']], use_container_width=True)

                    # Grafico a linee per tutti gli indicatori
                    st.subheader("Grafico a Linee per Qualità dell'Aria")
                    st.line_chart(df[['PM10 (µg/m³)', 'PM2.5 (µg/m³)', 'CO (µg/m³)', 'Ozone (µg/m³)']], use_container_width=True)