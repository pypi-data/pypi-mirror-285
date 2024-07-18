"""Hermes templating engine for structured prefix generation."""

# TODO: import ansible core filters.
# TODO: cleanup the metric observations.
# TODO: move top level class declarations elsewhere.

import logging
import os
from logging import LoggerAdapter
from typing import NamedTuple

from chartok import heather
from constants import BOM
from data import build_template_data
from decorators import monitor
from exceptions import (
    InvalidPromptError,
    MessageStartIdxNotFound,
    TokenLimitExceededError,
)
from metrics import Metrics
from prompt_poet import AbstractTokenizer, Prompt, PromptPart
from structured_prefix import DEFAULT_TOKEN_LIMIT, StructuredPrefix

MESSAGE_PART_PREFIX = "message_"
PINNED_MESSAGE_PART_PREFIX = "pinned_message_"
DEFAULT_TEMPLATE_NAME = "production_raw.yml.j2"
DEFAULT_TEMPLATE_DIR = "templates"
USE_TEMPLATE_CACHING = True
TRUNCATION_STEP_FRAC_TOKEN_LIMIT = 0.25

HERE = os.path.abspath(os.path.dirname(__file__))


class TokenizedContext(NamedTuple):
    """Tokenized context."""

    tokens: list[int]
    idx_after_timestamp: int
    context_num_msg: int
    truncated_num_msg: int


class MonitoredPrompt(Prompt):
    """Monitored Prompt."""

    @monitor
    def __init__(self, *args, **kwargs):
        """Initialize the monitored prompt."""
        super().__init__(*args, **kwargs)

    @monitor
    def tokenize(self, *args, **kwargs):
        """Tokenize the prompt."""
        return super().tokenize(*args, **kwargs)

    @monitor
    def truncate(self, *args, **kwargs):
        """Truncate the prompt."""
        return super().truncate(*args, **kwargs)

    @monitor
    def lreplace_at(self, *args, **kwargs):
        """Replace substring of part at a specific index."""
        return super().lreplace_at(*args, **kwargs)

    @monitor
    def _render_parts(self, *args, **kwargs):
        """Render parts of the prompt."""
        return super()._render_parts(*args, **kwargs)


def _build_tokenized_context(prompt: Prompt) -> TokenizedContext:
    """Build tokenized context."""
    prompt_parts: list[PromptPart] = prompt.parts
    pretruncation_prompt_parts: list[PromptPart] = prompt.pretruncation_parts
    first_part = prompt_parts[0]

    num_prompt_messages = sum(
        1 for part in prompt_parts if part.name.startswith(MESSAGE_PART_PREFIX)
    )
    num_pretruncation_prompt_messages = sum(
        1
        for part in pretruncation_prompt_parts
        if part.name.startswith(MESSAGE_PART_PREFIX)
    )
    _observe_prompt_message_metrics(
        prompt=prompt,
        num_prompt_messages=num_prompt_messages,
        num_pretruncation_prompt_messages=num_pretruncation_prompt_messages,
    )

    return TokenizedContext(
        tokens=prompt.tokens,
        idx_after_timestamp=len(first_part.tokens) + 1,
        context_num_msg=num_prompt_messages,
        truncated_num_msg=num_pretruncation_prompt_messages - num_prompt_messages,
    )


def _observe_prompt_message_metrics(
    prompt: Prompt, num_prompt_messages: int, num_pretruncation_prompt_messages: int
):
    """Observe prompt message metrics."""
    Metrics().MESSAGE_METRICS.labels(metric_type="total_rendered_messages").observe(
        num_pretruncation_prompt_messages
    )
    Metrics().MESSAGE_METRICS.labels(metric_type="truncated_messages").observe(
        num_pretruncation_prompt_messages - num_prompt_messages
    )
    Metrics().MESSAGE_METRICS.labels(metric_type="total_active_messages").observe(
        num_prompt_messages
    )
    num_pinned_messages = sum(
        1 for part in prompt.parts if part.name.startswith(PINNED_MESSAGE_PART_PREFIX)
    )

    if num_pinned_messages > 0:
        Metrics().MESSAGE_METRICS.labels(
            metric_type="truncated_messages_with_pinned"
        ).observe(num_pretruncation_prompt_messages - num_prompt_messages)
        Metrics().MESSAGE_METRICS.labels(
            metric_type="total_active_messages_with_pinned"
        ).observe(num_prompt_messages)


def _observe_prompt_token_metrics(prompt: Prompt):
    """Observe prompt metrics."""
    Metrics().TOKEN_METRICS.labels(metric_type="total_tokens").observe(
        len(prompt.pretruncation_tokens)
    )
    Metrics().TOKEN_METRICS.labels(metric_type="truncated_tokens").observe(
        len(prompt.pretruncation_tokens) - len(prompt.tokens)
    )
    Metrics().TOKEN_METRICS.labels(metric_type="active_tokens").observe(
        len(prompt.tokens)
    )

    num_pinned_message_tokens = sum(
        len(part.tokens)
        for part in prompt.parts
        if part.name.startswith(PINNED_MESSAGE_PART_PREFIX)
    )
    if num_pinned_message_tokens > 0:
        Metrics().TOKEN_METRICS.labels(
            metric_type="total_pinned_message_tokens"
        ).observe(num_pinned_message_tokens)


def _validate_prompt(prompt: Prompt):
    """Raises if the prompt is invalid by certain heuristics."""
    # Cache prompt tokens and prompt string as it can be expensive to compute.
    prompt_tokens: list[int] = prompt.tokens
    prompt_parts: list[PromptPart] = prompt.parts
    pretruncation_prompt_parts: list[PromptPart] = prompt.pretruncation_parts
    num_pretruncation_prompt_messages = sum(
        1
        for part in pretruncation_prompt_parts
        if part.name.startswith(MESSAGE_PART_PREFIX)
    )

    if len(prompt_parts) < 2:
        raise InvalidPromptError(
            f"Prompt should have at least 2 parts: {len(prompt_parts)=}"
        )

    if prompt_parts[1].raw_string.startswith(BOM):
        raise InvalidPromptError(
            f"First message should NOT contain {BOM=}: {prompt_parts[1]=}"
        )

    if prompt.token_limit > 0 and len(prompt_tokens) > prompt.token_limit:
        raise TokenLimitExceededError(
            f"Token limit exceeded: {len(prompt_tokens)=} {prompt.token_limit=}"
        )

    if num_pretruncation_prompt_messages < 1:
        raise MessageStartIdxNotFound(
            f"Message start index not found: {num_pretruncation_prompt_messages=}"
        )


@monitor
def build_structured_prefix(
    logger: LoggerAdapter,
    structured_prefix: StructuredPrefix,
    close_last_message: bool = False,
    truncation_step: int = None,
    stream_params: dict = None,
    tokenizer: AbstractTokenizer = None,
) -> dict:
    """Build structured prefix using Prompt Poet (PP)."""
    del close_last_message  # TODO: support long streaming.
    # TODO: remove this and use package_name.
    template_name = structured_prefix.hermes_generation_template_name
    if template_name and "/" not in template_name:
        structured_prefix.hermes_generation_template_name = os.path.join(
            HERE, DEFAULT_TEMPLATE_DIR, template_name
        )

    prompt = build_prompt(
        logger=logger,
        structured_prefix=structured_prefix,
        truncation_step=truncation_step,
        stream_params=stream_params,
        tokenizer=tokenizer,
    )

    tokenized_context: TokenizedContext = _build_tokenized_context(prompt)
    first_part: PromptPart = prompt.parts[0]
    last_part: PromptPart = prompt.parts[-1]

    return {
        "character_definitions": structured_prefix.character_definitions,
        "chat_history": (
            []
            if not tokenized_context.context_num_msg
            else structured_prefix.chat_history[-tokenized_context.context_num_msg :]
        ),
        "chat_hist_global_index": 0,
        "reply_prompt": last_part.raw_string,
        "space_added": True,
        "token_limit": structured_prefix.token_limit,
        "tokenized_context": tokenized_context,
        "timestamp": first_part.raw_string,
        "prompt": prompt,
    }


@monitor
def build_prompt(
    logger: LoggerAdapter,
    structured_prefix: StructuredPrefix,
    truncation_step: int = None,
    stream_params: dict = None,
    tokenizer: AbstractTokenizer = None,
) -> Prompt:
    """Build prompt using Prompt Poet (PP)."""
    if tokenizer is None:
        tokenizer = heather()
    if logger is None:
        logger = logging.getLogger(__name__)
    # Note: The current truncation step defaults to 1k. If this is changed en mass it
    # will be severly detrimental to the overall model server cache performance for
    # some short period of time.
    if truncation_step is None and structured_prefix.token_limit > DEFAULT_TOKEN_LIMIT:
        truncation_step = int(
            structured_prefix.token_limit * TRUNCATION_STEP_FRAC_TOKEN_LIMIT
        )

    template_data = build_template_data(
        structured_prefix=structured_prefix,
        logger=logger,
        stream_params=stream_params,
    )

    template_path = structured_prefix.hermes_generation_template_name
    if not template_path:
        template_path = os.path.join(HERE, DEFAULT_TEMPLATE_DIR, DEFAULT_TEMPLATE_NAME)

    prompt = MonitoredPrompt(
        template_data=template_data,
        logger=logger,
        template_path=template_path,
        raw_template=structured_prefix.hermes_generation_template,
        tokenizer=tokenizer,
        truncation_step=truncation_step,
        token_limit=structured_prefix.token_limit,
        from_cache=USE_TEMPLATE_CACHING,
    )
    prompt.tokenize()
    prompt.truncate()
    prompt.lreplace_at(old=BOM, new=" ", index=1)
    _validate_prompt(prompt)
    _observe_prompt_token_metrics(prompt)
    Metrics().HERMES_TEMPLATE_NAME.labels(
        template_name=prompt.template_name,
        template_dir=prompt.template_dir,
        source="cache" if USE_TEMPLATE_CACHING else "disk",
    ).inc()

    return prompt
