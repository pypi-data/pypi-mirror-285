import logging
from typing import Dict, List

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def inject_system_prompt(
    messages: List[Dict[str, str]], system_prompt: str
) -> List[Dict[str, str]]:
    """
    Add a system prompt to an OpenAI-style message list. If a system prompt is already present, replace it.
    """
    new_messages = []
    found = False
    for msg in messages:
        # t7: replace the first system prompt with the new one
        if msg["role"] == "system" and not found:
            new_messages.append({"role": "system", "content": system_prompt})
            found = True
        else:
            new_messages.append(msg)
    if not found:
        new_messages.insert(0, {"role": "system", "content": system_prompt})
    return new_messages
