import requests


class ProductiveClientAPI:
    BASE_URL = "https://api.productive.io/api/v2/"

    def __init__(self, api_token, company_id):
        self.api_token = api_token
        self.include = None
        self.headers = {
            "Content-Type": "application/vnd.api+json",
            "X-Auth-Token": api_token,
            "X-Organization-Id": str(company_id),
            "X-Feature-Flags": "includes-overhaul",
        }

    def request(self, method, endpoint, params=None, json=None):
        url = self.BASE_URL + endpoint
        data = []
        included = []
        if self.include is not None:
            if params is None:
                params = {"include": self.include}
            else:
                params["include"] = self.include
        while True:
            response = requests.request(
                method, url, headers=self.headers, params=params, json=json
            )
            if response.status_code not in range(200, 299):
                raise Exception(f"{response.status_code}: {response.text}")

            result = response.json()
            if "links" not in result:
                data.append(result["data"])
                included.extend(result["included"])
                break
            if "data" in result:
                data.extend(result["data"])
            if "included" in result:
                included.extend(result["included"])
            if "next" in result["links"]:
                url = result["links"]["next"]
            else:
                break
        full_data = data + included
        self.replace_relationship_ids(full_data)
        return data

    def replace_relationship_ids(self, data):
        # Create a lookup dictionary for all objects
        lookup = {item["type"]: {} for item in data}
        for item in data:
            lookup[item["type"]][item["id"]] = item

        # Function to replace IDs with actual objects
        def replace_ids(obj):
            if isinstance(obj, dict):
                if "data" in obj and isinstance(obj["data"], dict):
                    ref_type = obj["data"]["type"]
                    ref_id = obj["data"]["id"]
                    try:
                        return lookup[ref_type].get(ref_id, obj)
                    except Exception:
                        return {}
                elif "data" in obj and isinstance(obj["data"], list):
                    return [
                        lookup[item["type"]].get(item["id"], item)
                        for item in obj["data"]
                    ]
                else:
                    return {k: replace_ids(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_ids(item) for item in obj]
            else:
                return obj

        for item in data:
            if "relationships" in item:
                item["relationships"] = replace_ids(item["relationships"])

        return data

    def include(self, include: str):
        self.include = include

    def get_projects(self, params=None):
        return self.request("GET", "projects", params=params)

    def get_project(self, project_id):
        return self.request("GET", f"projects/{project_id}")
