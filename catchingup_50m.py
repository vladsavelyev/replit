"""
Second version. After completing `catchingup_25m.py` with timer, I had 5 minutes remaining out of planned 30m, so I copied the file and started playing more with it. Got carried away for next 25 minutes. This version is slighlty nicer aesthetically, does more checks on the dictionaries, and allows easier adding new operations. 
"""

import json
import inspect


class ValidationError(Exception):
  """Raised to indicate operation validation error"""

  pass


class State:
  """State of repl: just the text and the cursor position"""

  def __init__(self, text: str, cursor: int):
    self.text = text
    self.cursor = cursor
    self._avail_ops = {
      f.__name__: f
      for f in [self.skip, self.delete, self.insert]
    }  # could use inspect.getmembers, but listing explicitly is safer

  def skip(self, count: int):
    if self.cursor + count < 0:
      raise ValidationError(
        f"Cursor cannot be moved below 0, got: {self.cursor + count=}")

    if self.cursor + count > len(self.text):
      raise ValidationError(
        f"Cursor cannot be moved out of bound of text, got: "
        f"{self.cursor + count=}>{len(self.text)}")

    self.cursor = self.cursor + count

  def delete(self, count: int):
    if count < 0:
      raise ValidationError(f"Cannot delete negative count: {count=}")

    if self.cursor + count > len(self.text):
      raise ValidationError(
        f"Trying to delete beyond the boundary of the text: "
        f"{self.cursor + count=}>{len(self.text)}")

    self.text = self.text[:self.cursor] + self.text[self.cursor + count:]

  def insert(self, chars: str):
    self.text = self.text[:self.cursor] + chars + self.text[self.cursor:]
    self.cursor = self.cursor + len(chars)

  def apply_op(self, op: dict[str]):
    """
        Validates an op encoded as a dictionary, and runs the function corresponding
        to this op.
        """
    if (name := op.get("op")) is None:
      raise ValidationError(
        f'"op" key is required for all operations, got: {op}')
    if (op_func := self._avail_ops.get(name)) is None:
      raise ValidationError(f'Unknown op: "{name}", got: {op}')

    op.pop("op")
    provided_args = op
    expected_args = [
      a for a in inspect.getfullargspec(op_func).args if a != "self"
    ]
    if not set(provided_args) == set(expected_args):
      raise ValidationError(
        f"Expected keys: {expected_args} for op: {name}, got: {op}")
    # Finally, running the actual operation.
    return op_func(**op)


def validate(stale: str, latest: str, ot_json: str, cursor: int = 0):
  """
    Validates a set of text modifying operations encoded as a json string (`ot_json`),
    given the `stale` and the `latest` version of text. Raises ValidationError if
    validation failed.
    """
  if not 0 <= cursor < len(stale):
    raise ValidationError(
      f"Initial cursor position must be between 0 and {len(stale)=}, "
      f""
      f"got {cursor=}", )

  state = State(stale, cursor)
  for op in json.loads(ot_json):
    state.apply_op(op)

  # print(f'After applying the operation, {text=}, {cursor=}')
  if state.text != latest:
    raise ValidationError(
      f"Stale text after applying modifications does not match the"
      f" latest text: {state.text=}, {latest=}", )


# Examples from the task plus few more.
examples = [
  (
    "Repl.it uses operational transformations to keep everyone in a multiplayer "
    "repl "
    "in sync.",
    "Repl.it uses operational transformations.",
    '[{"op": "skip", "count": 40}, {"op": "delete", "count": 47}]',
    True,
  ),
  (
    "Repl.it uses operational transformations to keep everyone in a multiplayer "
    "repl "
    "in sync.",
    "Repl.it uses operational transformations.",
    '[{"op": "skip", "chars": 40}]',
    False,
  ),
  (
    "Repl.it uses operational transformations to keep everyone in a multiplayer "
    "repl "
    "in sync.",
    "Repl.it uses operational transformations.",
    '[{"op": "skip", "count": 45}, {"op": "delete", "count": 47}]',
    False,
  ),
  (
    "Repl.it uses operational transformations to keep everyone in a multiplayer "
    "repl "
    "in sync.",
    "Repl.it uses operational transformations.",
    '[{"op": "skip", "count": 40}, {"op": "delete", "count": 47}, {"op": "skip", '
    '"count": 2}]',
    False,
  ),
  (
    "Repl.it uses operational transformations to keep everyone in a multiplayer "
    "repl "
    "in sync.",
    "We use operational transformations to keep everyone in a multiplayer repl in "
    "sync.",
    '[{"op": "delete", "count": 7}, {"op": "insert", "chars": "We"}, '
    '{"op": "skip", '
    '"count": 4}, {"op": "delete", "count": 1}]',
    True,
  ),
  (
    "Repl.it uses operational transformations to keep everyone in a multiplayer "
    "repl "
    "in sync.",
    "We can use operational transformations to keep everyone in a multiplayer "
    "repl in "
    "sync.",
    '[{"op": "delete", "count": 7}, {"op": "insert", "chars": "We"}, '
    '{"op": "skip", '
    '"count": 4}, {"op": "delete", "count": 1}]',
    False,
  ),
  (
    "Repl.it uses operational transformations to keep everyone in a multiplayer "
    "repl "
    "in sync.",
    "Repl.it uses operational transformations to keep everyone in a multiplayer "
    "repl "
    "in sync.",
    "[]",
    True,
  ),
]

# Testing on provided examples plus a few more:
for stale, latest, ot_json, expected in examples:
  try:
    validate(stale, latest, ot_json)
  except ValidationError as e:
    if expected is False:
      print(f"✅ Operations are invalid, as expected, with reason: {e}")
    else:
      print(f"❌ Unexpected validation error: {e}")
  else:
    if expected is True:
      print("✅ Operations are valid, as expected")
    else:
      print("❌ Unexpectedly valid operations")
