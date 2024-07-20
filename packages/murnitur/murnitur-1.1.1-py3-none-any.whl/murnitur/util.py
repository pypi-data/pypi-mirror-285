import os
import requests


class Util:

    api_url = "https://api.murnitur.ai/api"
    endpoint = api_url + "/llm-evaluators/evaluations/save"

    def send_metrics(self, metrics: list, runs: list, headers: any):
        response = requests.post(
            self.endpoint, json={"data": metrics, "metrics": runs}, headers=headers
        )
        return response.status_code == 200 or response.status_code == 201

    def authenticate(self):
        api_key = os.getenv("MURNITUR_API_KEY")
        if not api_key:
            raise ValueError("Please provide a valid API key.")
        try:
            response = requests.get(
                f"https://api.murnitur.ai/api/auth/details",
                headers={"x-murnix-trace-token": api_key},
            )
            response.raise_for_status()

            try:
                return response.json()
            except ValueError as e:
                raise ValueError("Response content is not valid JSON.")

        except requests.RequestException as e:
            raise ConnectionError(f"Request to Murnitur API failed: {e}")

    def get_preset(self, name: str, api_key: str):
        try:
            response = requests.get(
                url=f"{self.api_url}/presets/sdk?name={name}",
                headers={"x-murnix-trace-token": api_key},
            )
            if response.status_code != 200:
                raise Exception(response.json()["message"])
            return response.status_code, response.json()
        except Exception as e:
            print(e)
            return response.status_code, None
