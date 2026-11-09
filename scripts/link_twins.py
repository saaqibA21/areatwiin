# Cross-link index.html and google_maps_twin.html

with open("c:/Users/SAAQIB/areatwin/google_maps_twin.html", "r", encoding="utf-8") as f:
    text1 = f.read()

target1 = '<div id="time-disp">🕐 08:00 AM</div>'
btn1 = '<div style="display:flex;align-items:center;gap:10px"><a href="index.html" class="btn" style="text-decoration:none;display:inline-block">🏙️ Switch to 3D Three.js Twin</a><div id="time-disp">🕐 08:00 AM</div></div>'

if 'Switch to 3D Three.js Twin' not in text1:
    text1 = text1.replace(target1, btn1, 1)
    with open("c:/Users/SAAQIB/areatwin/google_maps_twin.html", "w", encoding="utf-8") as f:
        f.write(text1)

with open("c:/Users/SAAQIB/areatwin/index.html", "r", encoding="utf-8") as f:
    text2 = f.read()

btn2 = '<div style="display:flex;align-items:center;gap:10px"><a href="google_maps_twin.html" class="btn" style="text-decoration:none;display:inline-block;background:#0284c7;color:#fff">🗺️ Switch to Google Maps Satellite Twin</a><div id="time-disp">🕐 08:00 AM</div></div>'

if 'Switch to Google Maps Satellite Twin' not in text2:
    text2 = text2.replace(target1, btn2, 1)
    with open("c:/Users/SAAQIB/areatwin/index.html", "w", encoding="utf-8") as f:
        f.write(text2)

print("Linked both twins successfully!")
