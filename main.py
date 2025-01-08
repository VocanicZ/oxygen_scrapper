import json
import time
import safe_open
import generate
import convert

def initialize():
    database_elements = []
    database = safe_open.r("database.json")["database"]
    for contents in database:
        if contents["name"] == "elements":
            database_elements = contents["contents"]
    return database_elements

def scrap(env, database_elements, uri, delay=5):
    elements = {}
    file_map = {}
    db_map = {}
    driver = generate.getDriver()

    for content in database_elements:
        state = content["name"]
        db_map[state] = {}
        sub_state = ""

        def inner(js, state, sub_state):
            name = convert.get(js, "file_name")
            js_out = generate.scrape(driver, uri, js, state, sub_state, delay)
            if js_out is None:
                with safe_open.w(f"error/{name}.json") as file:
                    file.write(json.dumps(js_out, indent=4))
            elements[name] = js_out
            file_map[name] = js["name"]
            db_map[state][convert.get(js, "db")] = name
            with safe_open.w(f"{env}/elements/{state}/{sub_state}/{name}.json") as file:
                file.write(json.dumps(js_out, indent=4))

        for i in content["contents"]:
            if "contents" not in i:
                inner(i, state, sub_state)
            else:
                sub_state = i["name"]
                for j in i["contents"]:
                    inner(j, state, sub_state)
    generate.closeDriver(driver)

    return elements, file_map, db_map

def state_modify(elements, db_map):
    for key, value in elements.items():
        if value is None:
            continue
        state = value.get("data", {}).get("state", {})
        s = value.get("recipe", {}).get("state_transitions", {})
        if "min_target" in s:
            target = s["min_target"]
            if target in db_map[state]:
                s["min_target"] = db_map[state][target]
        if "max_target" in s:
            target = s["max_target"]
            if target in db_map[state]:
                s["max_target"] = db_map[state][target]

def save(env, elements, file_map, db_map):
    mega = {}
    mega["elements"] = elements
    with safe_open.w(f"{env}/mega.json") as file:
        file.write(json.dumps(mega, indent=4))
    with safe_open.w(f"{env}/elements.json") as file:
        file.write(json.dumps(elements, indent=4))
    with safe_open.w(f"{env}/file_map.json") as file:
        file.write(json.dumps(file_map, indent=4))
    with safe_open.w(f"{env}/db_map.json") as file:
        file.write(json.dumps(db_map, indent=4))

# Main execution
start = time.time()
env = "database"
uri = "https://oni-db.com/details/"

database_elements = initialize()
elements, file_map, db_map = scrap(env, database_elements, uri)
state_modify(elements, db_map)
save(env, elements, file_map, db_map)

print(f"Done in {(time.time() - start) / 60:.2f} minutes")