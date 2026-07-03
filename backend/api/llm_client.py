import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional provider imports — imported at module level so tests can mock them.
# Wrapped in try/except so the server starts even if a provider's package is
# missing (the runtime ValueError is raised later, when the provider is used).
# ---------------------------------------------------------------------------
try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:  # pragma: no cover
    genai = None  # type: ignore[assignment]
    genai_types = None  # type: ignore[assignment]

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]

DEFAULT_MODELS = {
    "openai": {
        "chat": "gpt-4.1-mini",
        "embedding": "text-embedding-3-small",
        "embedding_dim": 1536,
    },
    "gemini": {
        "chat": "gemini-2.5-flash",
        "embedding": "gemini-embedding-2",
        "embedding_dim": 1536,
    },
}


def _get_provider():
    return settings.LLM_PROVIDER


def get_chat_model():
    if settings.LLM_CHAT_MODEL:
        return settings.LLM_CHAT_MODEL
    provider = _get_provider()
    return DEFAULT_MODELS[provider]["chat"]


def get_embedding_model():
    provider = _get_provider()
    return DEFAULT_MODELS[provider]["embedding"]


def get_embedding_dimension():
    provider = _get_provider()
    return DEFAULT_MODELS[provider]["embedding_dim"]


def get_chroma_collection_name():
    embedding_model = get_embedding_model()
    safe_name = embedding_model.replace("-", "_").replace(".", "_")
    return f"portfolio_knowledge_{safe_name}"


def record_llm_cost(operation_type, model_name, input_tokens, output_tokens, session=None):
    from decimal import Decimal

    from django.db import transaction

    from .models import LLMCostTracking
    from .pricing import calculate_chat_cost, calculate_embedding_cost

    total_tx_tokens = input_tokens + output_tokens

    if operation_type == "chat":
        total_transaction_cost = calculate_chat_cost(model_name, input_tokens, output_tokens)
    else:
        total_transaction_cost = calculate_embedding_cost(model_name, input_tokens)

    try:
        with transaction.atomic():
            last_record = LLMCostTracking.objects.select_for_update().order_by("-created_at").first()

            new_record = LLMCostTracking(
                session=session,
                operation_type=operation_type,
                model_name=model_name,
                tokens_used=total_tx_tokens,
                cost=total_transaction_cost,
            )

            if last_record:
                new_record.total_chat_cost = last_record.total_chat_cost
                new_record.total_embedding_cost = last_record.total_embedding_cost
                new_record.total_cost = last_record.total_cost
                new_record.total_chat_tokens = last_record.total_chat_tokens
                new_record.total_embedding_tokens = last_record.total_embedding_tokens
                new_record.total_tokens = last_record.total_tokens

            if operation_type == "chat":
                new_record.total_chat_cost = Decimal(str(new_record.total_chat_cost)) + total_transaction_cost
                new_record.total_chat_tokens += total_tx_tokens
            else:
                new_record.total_embedding_cost = Decimal(str(new_record.total_embedding_cost)) + total_transaction_cost
                new_record.total_embedding_tokens += total_tx_tokens

            new_record.total_cost = Decimal(str(new_record.total_cost)) + total_transaction_cost
            new_record.total_tokens += total_tx_tokens

            new_record.save()
    except Exception as e:
        logger.error(f"Failed to record LLM cost: {e}", exc_info=True)


def generate_chat_completion(messages, max_tokens=512, temperature=0.2, session=None):
    provider = _get_provider()

    if provider == "gemini":
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set. Cannot use Gemini provider.")

        client = genai.Client(api_key=api_key)
        prompt = messages[0]["content"] if messages else ""
        model = get_chat_model()

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )

        in_tokens = 0
        out_tokens = 0
        try:
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                in_tokens = int(response.usage_metadata.prompt_token_count)
                out_tokens = int(response.usage_metadata.candidates_token_count)
        except Exception:
            from .pricing import estimate_token_count

            in_tokens = estimate_token_count(prompt)
            out_tokens = estimate_token_count(response.text if response.text else "")

        if session:
            record_llm_cost("chat", model, in_tokens, out_tokens, session)
        return response.text

    else:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set. Cannot use OpenAI provider.")

        client = OpenAI(api_key=api_key)
        model = get_chat_model()
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        in_tokens = 0
        out_tokens = 0
        try:
            in_tokens = int(completion.usage.prompt_tokens)
            out_tokens = int(completion.usage.completion_tokens)
        except Exception:
            from .pricing import estimate_token_count

            prompt_text = " ".join(m["content"] for m in messages if "content" in m)
            in_tokens = estimate_token_count(prompt_text)
            out_tokens = estimate_token_count(completion.choices[0].message.content)
        if session:
            record_llm_cost("chat", model, in_tokens, out_tokens, session)

        return completion.choices[0].message.content


def generate_embedding(text):
    from .pricing import estimate_token_count

    provider = _get_provider()
    model = get_embedding_model()

    if provider == "gemini":
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set. Cannot generate embeddings with Gemini.")

        client = genai.Client(api_key=api_key)
        result = client.models.embed_content(
            model=model,
            contents=[text],
        )

        in_tokens = estimate_token_count(text)
        record_llm_cost("embedding", model, in_tokens, 0)

        return result.embeddings[0].values

    else:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set. Cannot generate embeddings with OpenAI.")

        client = OpenAI(api_key=api_key)
        resp = client.embeddings.create(input=[text], model=model)

        in_tokens = resp.usage.prompt_tokens if hasattr(resp, "usage") else estimate_token_count(text)
        try:
            in_tokens = int(in_tokens)
        except (TypeError, ValueError):
            in_tokens = estimate_token_count(text)
        record_llm_cost("embedding", model, in_tokens, 0)

        return resp.data[0].embedding
