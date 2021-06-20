import urllib.request
import json
import os.path
import glob

with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json") as url:
    data = json.loads(url.read().decode())
version = data[0]


def champions():
    if not os.path.isfile("cache/champions" + version + ".json"):
        update()
    with open("cache/champions" + version + ".json") as file:
        data = json.load(file)["data"]
    champions = dict()
    for champion in data:
        champions[data[champion]["name"]] = data[champion]["spells"][3]["cooldown"]
    return champions

def summonerspells():
    if not os.path.isfile("cache/summonerspells" + version + ".json"):
        update()
    with open("cache/summonerspells" + version + ".json") as file:
        data = json.load(file)["data"]
    summonerspells = dict()
    for summonerspell in data:
        summonerspells[data[summonerspell]["name"]] = data[summonerspell]["cooldown"]
    return summonerspells

def update():
    print("Updating data for new patch")
    files = glob.glob('cache/*')
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))
    cache = open("cache/champions" + version + ".json", "x")
    with urllib.request.urlopen("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/championFull.json") as url:
       cache.write(url.read().decode())
    cache.close()
    cache = open("cache/summonerspells" + version + ".json", "x")
    with urllib.request.urlopen("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/summoner.json") as url:
        cache.write(url.read().decode())
    cache.close()
    print("Updated successfully")