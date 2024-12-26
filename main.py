
import time
import generate
import convert
import json
import safe_open

mega = {}
elements = {}
file_map = {}

start = time.time()
database = safe_open.r("database.json")["database"]
database_elements = []
for contents in database:
    if contents["name"] == "elements":
        database_elements = contents["contents"]
uri = "https://oni-db.com/details/" 

for content in database_elements:
    state = content["name"]
    sub_state=""
    js = {}
    def inner(js=js,state=state,sub_state=sub_state, uri=uri):
        name=convert.get(js, "file_name")
        print("database/elements/"+state+"/"+sub_state+"/"+name+".json")
        js_out = generate.scrape(uri, js, state, sub_state, 2)
        if js_out == None:
            with safe_open.w("error/"+name+".json") as file:
                file.write(json.dumps(js_out, indent=4))
        elements[name] = js_out
        file_map[name] = js["name"]
        with safe_open.w("database/elements/"+state+"/"+sub_state+"/"+name+".json") as file:
            file.write(json.dumps(js_out, indent=4))
    for i in content["contents"]:
        if "contents" not in i:
                inner(i,state,sub_state,uri)
        else:
            sub_state = i["name"]
            for j in i["contents"]:
                inner(j,state,sub_state,uri)
mega["elements"] = elements
with safe_open.w("database/elements.json",) as file:
    file.write(json.dumps(elements, indent=4))
with safe_open.w("database/"+"mega.json") as file:
    file.write(json.dumps(mega, indent=4))
with safe_open.w("database/"+"file_map.json") as file:
    file.write(json.dumps(file_map, indent=4))

print(f"done {(time.time() - start)/60}minutes")