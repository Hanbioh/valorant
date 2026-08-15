import requests
res = requests.get("https://valorant-api.com/v1/weapons?language=ko-KR").json()
weapons = res.get("data", [])
for w in weapons:
    cat = w.get("shopData", {}).get("categoryText", "") if w.get("shopData") else "None"
    print(w["displayName"], cat)
