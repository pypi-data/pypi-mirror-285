import json
import os
import requests
import murnitur
from concurrent.futures import ThreadPoolExecutor
from typing import TypedDict, Optional, List, Literal, Union
from murnitur.main import GuardConfig, TracedSpan
from .lib import check_pii, detect_tone, detect_injection, detect_toxicity, detect_bias

Value = Union[str, int, List[str]]

default_config: GuardConfig = {
    "murnitur_key": None,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "group": None,
    "api_key": None,
    "base_url": None,
    "headers": {},
}


class Payload(TypedDict):
    input: Optional[str]
    output: Optional[str]


class Rule(TypedDict):
    metric: Literal[
        "pii", "input_pii", "toxicity", "input_tone", "tone", "bias", "prompt_injection"
    ]
    operator: Literal[
        "equal",
        "not_equal",
        "contains",
        "greater_than",
        "less_than",
        "greater_than_equal",
        "less_than_equal",
        "any",
        "all",
    ]
    value: Value


class Action(TypedDict):
    type: Literal["OVERRIDE", "FLAG"]
    fallback: str


class RuleSet(TypedDict):
    rules: List[Rule]
    action: Action


class Response:
    def __init__(
        self,
        text: str,
        triggered: bool,
        rule: Optional[Rule] = None,
    ) -> None:
        self.text = text
        self.triggered = triggered
        self.rule = rule


class Guard:
    executor = ThreadPoolExecutor(max_workers=5)

    @staticmethod
    def send_interception_to_backend(data, api_key: str):
        if api_key is not None:
            try:
                response = requests.post(
                    "https://api.murnitur.ai/api/interceptions",
                    json=data,
                    headers={"x-murnix-trace-token": api_key},
                )
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to send interception: {e}")

    @staticmethod
    def __preprocess_rules(rulesets: List[RuleSet]) -> list[RuleSet]:
        processed_rules = []

        for ruleset in rulesets:
            processed_rules.append(
                {
                    "rules": [
                        {
                            "metric": rule["metric"],
                            "operator": rule["operator"],
                            "value": (
                                rule["value"]
                                if isinstance(rule["value"], list)
                                else [rule["value"]]
                            ),
                        }
                        for rule in ruleset["rules"]
                    ],
                    "action": ruleset["action"],
                }
            )
        return processed_rules

    @staticmethod
    def shield(
        payload: Payload, rulesets: List[RuleSet], config: GuardConfig
    ) -> Response:
        with murnitur.tracer(name="Shield") as trace:
            trace.set_metadata(
                {
                    "input": json.dumps(payload),
                }
            )
            """
            Shields the payload based on provided rulesets.

            Args:
                payload (dict): The input data to be checked.
                rulesets (list): A list of rules defining how to check the payload.\n
                config:
                    murnitur_key (str): API key for Murnitur services.
                    group (str, optional): Group name for categorization. Default is "untitled".
                    openai_key (str, optional): API key for OpenAI services.
                    model (str, optional): Model for OpenAI services. Default is "gpt-4o-mini"

            Returns:
                Response: Response message after applying the rules.
            """
            try:

                if config is None:
                    config = default_config
                else:
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                preprocessed_rulesets = Guard.__preprocess_rules(rulesets)
                return_value: Response = None
                for ruleset in preprocessed_rulesets:
                    action_type = ruleset["action"]["type"]
                    fallback = ruleset["action"]["fallback"]

                    for rule in ruleset["rules"]:
                        metric = rule["metric"]
                        operator = rule["operator"]
                        rule_value = rule["value"]

                        if metric in ("pii", "input_pii"):
                            pii_value = payload.get(
                                "output" if metric == "pii" else "input", ""
                            )
                            if check_pii(pii_value, operator, rule_value):
                                submit_interception(
                                    payload,
                                    fallback,
                                    action_type,
                                    rule,
                                    ruleset,
                                    metric,
                                    config["group"],
                                    config["murnitur_key"],
                                    trace,
                                    rulesets,
                                )
                                return Response(
                                    (
                                        fallback
                                        if action_type == "OVERRIDE"
                                        else f"Message flagged: {fallback}"
                                    ),
                                    True,
                                    rule,
                                )
                            else:
                                return_value = Response(pii_value, False)
                        elif metric in ("tone", "input_tone"):
                            tone_value = payload.get(
                                "output" if metric == "tone" else "input", ""
                            )
                            if detect_tone(tone_value, operator, rule_value):
                                submit_interception(
                                    payload,
                                    fallback,
                                    action_type,
                                    rule,
                                    ruleset,
                                    metric,
                                    config["group"],
                                    config["murnitur_key"],
                                    trace,
                                    rulesets,
                                )
                                return Response(
                                    (
                                        fallback
                                        if action_type == "OVERRIDE"
                                        else f"Message flagged: {fallback}"
                                    ),
                                    True,
                                    rule,
                                )
                            else:
                                return_value = Response(tone_value, False)
                        elif metric == "prompt_injection":
                            input_value = payload.get("input", "")
                            if detect_injection(
                                input_value,
                                operator,
                                rule_value,
                                config,
                            ):
                                submit_interception(
                                    payload,
                                    fallback,
                                    action_type,
                                    rule,
                                    ruleset,
                                    metric,
                                    config["group"],
                                    config["murnitur_key"],
                                    trace,
                                    rulesets,
                                )
                                return Response(
                                    (
                                        fallback
                                        if action_type == "OVERRIDE"
                                        else f"Message flagged: {fallback}"
                                    ),
                                    True,
                                    rule,
                                )
                            else:
                                return_value = Response(input_value, False)
                        elif metric == "toxicity":
                            output_value = payload.get("output", "")
                            if detect_toxicity(
                                output_value, operator, rule_value[0], config
                            ):
                                submit_interception(
                                    payload,
                                    fallback,
                                    action_type,
                                    rule,
                                    ruleset,
                                    metric,
                                    config["group"],
                                    config["murnitur_key"],
                                    trace,
                                    rulesets,
                                )
                                return Response(
                                    (
                                        fallback
                                        if action_type == "OVERRIDE"
                                        else f"Message flagged: {fallback}"
                                    ),
                                    True,
                                    rule,
                                )
                        elif metric == "bias":
                            output_value = payload.get("output", "")
                            if detect_bias(
                                output_value,
                                operator,
                                rule_value[0],
                                config,
                            ):
                                submit_interception(
                                    payload,
                                    fallback,
                                    action_type,
                                    rule,
                                    ruleset,
                                    metric,
                                    config["group"],
                                    config["murnitur_key"],
                                    trace,
                                    rulesets,
                                )
                                return Response(
                                    (
                                        fallback
                                        if action_type == "OVERRIDE"
                                        else f"Message flagged: {fallback}"
                                    ),
                                    True,
                                    rule,
                                )

                return return_value or Response(
                    payload.get("output", payload.get("input", "")), False
                )

            except Exception as e:
                raise e


def submit_interception(
    payload,
    fallback,
    action_type,
    rule,
    ruleset,
    metric,
    group=None,
    murnitur_key=None,
    trace: TracedSpan = None,
    rulesets: list[RuleSet] = [],
):
    """
    Submits an interception to the backend for processing asynchronously.

    Args:
        payload (dict): The input data to be intercepted.
        fallback (str): The fallback message.
        action_type (str): The action type, e.g., "OVERRIDE".
        rule (dict): The rule that triggered the interception.
        ruleset (dict): The ruleset containing the rule.
        group (str, optional): Group name for categorization. Default is None.
        murnitur_key (str, optional): API key for Murnitur services. Default is None.

    Returns:
        Future: A future object representing the execution of the interception.
    """
    group = group or "untitled"

    interception_data = {
        "group": group,
        "interception": {
            "input": payload.get("input"),
            "output": payload.get("output"),
            "metric": metric,
            "response": (
                fallback
                if action_type == "OVERRIDE"
                else f"Message flagged: {fallback}"
            ),
            "rule": rule,
            "action": ruleset["action"],
        },
    }

    if trace:
        trace.__shield__(
            rules=rulesets,
            rule={
                **rule,
                "action": ruleset["action"],
            },
            triggered=True,
            response=interception_data["interception"]["response"],
        )
        trace.set_result(
            json.dumps({"output": interception_data["interception"]["response"]})
        )

    return Guard.executor.submit(
        Guard.send_interception_to_backend,
        data=interception_data,
        api_key=os.getenv("MURNITUR_API_KEY", murnitur_key),
    )
