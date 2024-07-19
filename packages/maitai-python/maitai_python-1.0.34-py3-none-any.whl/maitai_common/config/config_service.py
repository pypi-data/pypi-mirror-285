from betterproto import Casing

from maitai_gen.config import Config, InferenceLocations


def get_default_config() -> Config:
    return Config(
        inference_location=InferenceLocations.SERVER,
        evaluation_enabled=True,
        apply_corrections=True,
        model='gpt-4o',
        temperature=1,
        streaming=False,
        response_format="text",
        stop=None,
        logprobs=False,
        max_tokens=None,
        n=1,
        frequency_penalty=0,
        presence_penalty=0,
        timeout=-1,
        context_retrieval_enabled=False,
        fallback_model=None,
    )


def reconcile_config_with_default(config_dict: dict) -> Config:
    default_config_json = get_default_config().to_pydict(casing=Casing.SNAKE)
    for key, value in default_config_json.items():
        if key not in config_dict:
            config_dict[key] = value
    return Config().from_pydict(config_dict)
