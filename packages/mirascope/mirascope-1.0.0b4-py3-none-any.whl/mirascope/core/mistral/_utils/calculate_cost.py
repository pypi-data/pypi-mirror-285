"""Calculate the cost of a completion using the Mistral API."""


def calculate_cost(
    input_tokens: int | float | None,
    output_tokens: int | float | None,
    model="open-mistral-7b",
) -> float | None:
    """Calculate the cost of a completion using the Mistral API.

    https://mistral.ai/technology/#pricing

    Model                     Input               Output
    open-mistral-7b	          $0.25/1M tokens	  $0.25/1M tokens
    open-mixtral-8x7b	      $0.7/1M tokens	  $0.7/1M tokens
    open-mixtral-8x22b	      $2/1M tokens	      $6/1M tokens
    mistral-small		      $2/1M tokens	      $6/1M tokens
    mistral-medium		      $2.7/1M tokens	  $8.1/1M tokens
    mistral-large		      $8/1M tokens	      $24/1M tokens
    """
    pricing = {
        "open-mistral-7b": {"prompt": 0.000_000_25, "completion": 0.000_000_25},
        "open-mixtral-8x7b": {"prompt": 0.000_000_7, "completion": 0.000_000_7},
        "open-mixtral-8x22b": {"prompt": 0.000_002, "completion": 0.000_006},
        "mistral-small": {"prompt": 0.000_002, "completion": 0.000_006},
        "mistral-medium": {"prompt": 0.000_002_7, "completion": 0.000_008_1},
        "mistral-large": {"prompt": 0.000_008, "completion": 0.000_024},
    }

    if input_tokens is None or output_tokens is None:
        return None

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    completion_cost = input_tokens * model_pricing["completion"]
    total_cost = output_tokens + completion_cost

    return total_cost
