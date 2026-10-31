# 🏙️ Royapuram Digital Twin (Chennai, India)

An authentic GIS-based digital twin and urban mobility simulation of **Royapuram, Chennai, Tamil Nadu**.

Built with authentic surveyed OpenStreetMap street geometry, Google Maps Satellite imagery, Three.js 3D architectural rendering, an intelligent car-following anti-collision model, and a predictive traffic congestion engine.

---

## 🌟 Key Features

1. **Authentic 848-Street Road Network (142.8 km of Roads)**
   - Extracted directly from OpenStreetMap surveyed centerlines.
   - Node-by-node topological connectivity with 99.2% network connectivity.
   - Physical street constraints:
     - **71 One-Way Corridors** (directional enforcement)
     - **748 Narrow Streets & Alleys** (<3.5m width restrictions)
     - **147 Dead-End Cul-de-Sacs** (180° turn-around handling)

2. **Multi-Modal Vehicle Fleet & Dynamic Speed Telemetry**
   - **Cars / Sedans** (up to 52 km/h)
   - **Bikes / Two-Wheelers** (agile, up to 48 km/h)
   - **Auto-Rickshaws** (up to 38 km/h)
   - **Chennai MTC City Buses** (up to 32 km/h on designated bus routes)
   - Real-time speedometer and telemetry popup on every vehicle marker.

3. **Intelligent Anti-Collision & Car-Following System**
   - Safe headway buffer calculation along each street segment.
   - Follower vehicles automatically decelerate and maintain safe stopping distances.
   - Zero overlapping/clipping: vehicles queue realistically behind barricades, red lights, and waterlogged roads.

4. **Traffic Congestion Prediction Engine**
   - Simulates and forecasts network traffic displacement when any road corridor is blocked.
   - Visual heatmap overlay with V/C (Volume-to-Capacity) ratio grading:
     - 🔴 Severe Gridlock ($V/C \ge 1.10$)
     - 🟠 Heavy Congestion ($V/C \ge 0.85$)
     - 🟡 Moderate Influx ($V/C \ge 0.65$)
   - Displays estimated queue lengths, onset window, and traffic police mitigation guidance.

5. **29 Points of Interest (POIs)**
   - **7 Kovils (Temples)**: Arulmigu Angalaparameshwari Amman Temple, Subramania Swamy Temple, Salai Vinayagar Koil, Kaligambal Temple, etc.
   - **7 Hotels & Restaurants**: Buhari Hotel, Hotel Sea Shell, Sangeetha Veg, Hotel Saravana Bhavan, etc.
   - **4 Metro Stations**: Mannadi, Washermanpet, High Court, Sir Theagaraya College.
   - **3 Railway Stations**: Royapuram Heritage Station (1856), Washermanpet, Chennai Beach Junction.
   - **8 Key Landmarks**: Kasimedu Fishing Harbour, Stanley Medical College & Hospital, St. Peter's Church, Parsi Fire Temple, etc.

6. **Origin-Destination (OD) Visitor Influx Controller**
   - Dispatch target footfall from 5 major entry gateways:
     - *South*: Parrys / Central / High Court
     - *North*: Tondiarpet / Ennore
     - *West*: Mint / Basin Bridge
     - *Coast*: Kasimedu Port Wharf Gate
     - *Distributed*: Local neighborhood wards

7. **Hydrological Rain & Water Stagnation Simulation**
   - Models Royapuram's natural terrain depression basins:
     - *Stanley Subway Underpass* (-3.8m dip, up to 75 cm stagnation depth)
     - *Royapuram ROB Bridge Foot Slope* (-2.2m dip)
     - *S. Madha Church Street Basin* (-2.5m dip)
     - *Kasimedu Wharf Gate Slipway* (-2.8m dip)
     - *Kalmandapam Market Basin* (-2.0m dip)
     - *Wall Tax / Basin Bridge Low Line* (-3.0m dip)
   - Dynamic monsoon rainfall with real-time water accumulation and automated reroute diversions.

---

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/saaqibA21/areatwiin.git
   cd areatwiin
   ```

2. Start a local HTTP server:
   ```bash
   python -m http.server 8000
   ```

3. Open in your browser:
   - **Google Maps Satellite Twin**: [http://localhost:8000/google_maps_twin.html](http://localhost:8000/google_maps_twin.html)
   - **3D Three.js Architectural Twin**: [http://localhost:8000/index.html](http://localhost:8000/index.html)

---

## 📄 License
MIT License.
