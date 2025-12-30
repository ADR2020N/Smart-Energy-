# Smart Energy Dashboard

An **interactive Smart Energy Dashboard** built with **Python, Streamlit, PostgreSQL, and Plotly** for real-time monitoring, visualization, and analysis of energy consumption data from smart meters. The dashboard is designed for smart grid monitoring, energy management, and IoT-based energy analytics.

---

## Features

- Real-time energy monitoring for individual smart meters  
- Dynamic selection of meter ID and time range (Last 1 Hour, Last 24 Hours, Last 7 Days)  
- Key metrics display: average/peak power, voltage, current, and frequency  
- Interactive charts for power, voltage, current, and frequency trends  
- Dark mode for clear visibility and professional look  
- Historical energy data table at the bottom of the dashboard  
- Auto-refresh every 5 seconds for real-time updates  

---

## Tech Stack

- **Python** – Data processing and backend logic  
- **Streamlit** – Interactive dashboard interface  
- **PostgreSQL / TimescaleDB** – Energy data storage and hypertables  
- **Plotly** – Interactive charts and visualizations  
- **paho-mqtt** – MQTT subscription for collecting real-time meter data  

---

## Screenshots

*Add your screenshots in the `images` folder and reference them here:*  

![Dashboard Screenshot](./images/dashboard_screenshot.png)

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/Smart-Energy-Dashboard.git
cd Smart-Energy-Dashboard
