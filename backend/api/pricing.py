from decimal import Decimal

import tiktoken

CHAT_PRICING = {
    "gemini-3.6-flash": {"input": 1.50, "output": 7.50},
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "gemini-2.0-flash": {"input": 0.15, "output": 0.60},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

EMBEDDING_PRICING = {
    "gemini-embedding-2": 0.20,
    "gemini-embedding-001": 0.15,
    "text-embedding-004": 0.10,
    "text-embedding-3-small": 0.02,
    "text-embedding-3-large": 0.13,
    "text-embedding-ada-002": 0.10,
}

DEFAULT_CHAT_INPUT_PRICE = 0.50
DEFAULT_CHAT_OUTPUT_PRICE = 2.00
DEFAULT_EMBEDDING_PRICE = 0.15

_tokenizer = None


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = tiktoken.get_encoding("cl100k_base")
    return _tokenizer


def estimate_token_count(text):
    if not text:
        return 0
    return len(_get_tokenizer().encode(text))


def calculate_chat_cost(model, input_tokens, output_tokens):
    prices = CHAT_PRICING.get(model, {})
    input_price = Decimal(str(prices.get("input", DEFAULT_CHAT_INPUT_PRICE)))
    output_price = Decimal(str(prices.get("output", DEFAULT_CHAT_OUTPUT_PRICE)))
    ratio = Decimal(input_tokens) / Decimal(1_000_000)
    input_cost = ratio * input_price
    output_cost = ratio * output_price
    return input_cost + output_cost


def calculate_embedding_cost(model, input_tokens):
    price = Decimal(str(EMBEDDING_PRICING.get(model, DEFAULT_EMBEDDING_PRICE)))
    ratio = Decimal(input_tokens) / Decimal(1_000_000)
    return ratio * price
