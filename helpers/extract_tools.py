
from .dirty_json import DirtyJson
import regex, re
from helpers.modules import load_classes_from_file, load_classes_from_folder # keep here for backwards compatibility
from typing import Any
import logging

LOG = logging.getLogger(__name__)

def json_parse_dirty(json: str) -> dict[str, Any] | None:
    if not json or not isinstance(json, str):
        return None

    # Attempt 1: Standard parser
    ext_json = extract_json_object_string(json.strip())
    if ext_json:
        try:
            data = DirtyJson.parse_string(ext_json)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # Attempt 2: Regex fallback - extract tool_name and tool_args from partial output
    try:
        result = _regex_fallback(json)
        if result:
            LOG.debug("json_parse_dirty: recovered via regex fallback")
            return result
    except Exception as e:
        LOG.debug(f"json_parse_dirty: regex fallback failed: {e}")

    return None


def _regex_fallback(text: str) -> dict[str, Any] | None:
    """Try to extract tool_name and tool_args from malformed JSON using regex."""
    # Find tool_name value
    tn_match = re.search(
        r'"tool_name"\s*:\s*"([^"]+)"', text
    )
    if not tn_match:
        return None
    tool_name = tn_match.group(1)

    # Find tool_args object
    ta_match = re.search(
        r'"tool_args"\s*:\s*(\{[^}]*\})', text, re.DOTALL
    )
    if not ta_match:
        # Return with empty args if we at least have a tool_name
        return {"tool_name": tool_name, "tool_args": {}}

    args_str = ta_match.group(1)
    try:
        args = DirtyJson.parse_string(args_str)
        if isinstance(args, dict):
            return {"tool_name": tool_name, "tool_args": args}
    except Exception:
        pass

    # Last resort: return tool_name with raw args string
    return {"tool_name": tool_name, "tool_args": {"_raw": args_str}}


def extract_json_root_string(content: str) -> str | None:
    if not content or not isinstance(content, str):
        return None

    start = content.find("{")
    if start == -1:
        return None
    first_array = content.find("[")
    if first_array != -1 and first_array < start:
        return None

    parser = DirtyJson()
    try:
        parser.parse(content[start:])
    except Exception:
        return None

    if not parser.completed:
        return None

    return content[start : start + parser.index]


def extract_json_object_string(content):
    start = content.find("{")
    if start == -1:
        return ""

    # Find the first '{'
    end = content.rfind("}")
    if end == -1:
        # If there's no closing '}', return from start to the end
        return content[start:]
    else:
        # If there's a closing '}', return the substring from start to end
        return content[start : end + 1]


def extract_json_string(content):
    # Regular expression pattern to match a JSON object
    pattern = r'\{(?:[^{}]|(?R))*\}|\[(?:[^\[\]]|(?R))*\]|"(?:\\.|[^"\\])*"|true|false|null|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?'

    # Search for the pattern in the content
    match = regex.search(pattern, content)

    if match:
        # Return the matched JSON string
        return match.group(0)
    else:
        return ""


def fix_json_string(json_string):
    # Function to replace unescaped line breaks within JSON string values
    def replace_unescaped_newlines(match):
        return match.group(0).replace("\n", "\\n")

    # Use regex to find string values and apply the replacement function
    fixed_string = re.sub(
        r'(?<=: ")(.*?)(?=")', replace_unescaped_newlines, json_string, flags=re.DOTALL
    )
    return fixed_string


