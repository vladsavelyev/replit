"""
First version, which took 25 minutes on timer, including reading the task. After that, I copied the file and continued playing with the code for ~25 minutes more (catchingup_50m.py file).
"""

import json


def is_valid(stale: str,
             latest: str,
             ot_json: str,
             cursor: int = 0) -> tuple[bool, str]:
  """Validates a set of text modifying operations encoded as a 
  json string, given the stale and the latest version of text."""
  # print(ot_json)
  if not 0 <= cursor < len(stale):
    return False, f'cursor position must be between 0 and {len(stale)=}, got {cursor=}'

  text = str(stale)
  for op in json.loads(ot_json):
    if op['op'] == 'skip':
      if 'count' not in op:
        return False, '"count" value is required for the "skip" op'
      count = op['count']
      if not 0 <= (cursor + count) < len(text):
        return False, f"Cursor moved out of bound for current text with skip op, {count=}, got {cursor + count=}"
      cursor = cursor + count

    if op['op'] == 'delete':
      if 'count' not in op:
        return False, '"count" value is required for the "delete" op'
      count = op['count']
      if not 0 <= (cursor + count) < len(text):
        return False, f"Cursor moved out of bound for current text with skip op, {count=}"
      # print(f'Deleting chunk: {text=} ->')
      text = text[:cursor] + text[cursor + count:]

    if op['op'] == 'insert':
      if 'chars' not in op:
        return False, '"chars" value is required for the "insert" op'
      chars = op['chars']
      text = text[:cursor] + chars + text[cursor:]
      cursor = cursor + len(chars)

  # print(f'After applying the operation, {text=}, {cursor=}')
  if text != latest:
    return False, f"Stale text after applying modifications does not match the latest text: {text=}, {latest=}"
  return True, ''


# Testing on provided examples plus a few more:
for stale, latest, ot_json, expected in [
  (
    'Repl.it uses operational transformations to keep everyone in a multiplayer repl in sync.',
    'Repl.it uses operational transformations.',
    '[{"op": "skip", "count": 40}, {"op": "delete", "count": 47}]',
    True,
  ),
  (
    'Repl.it uses operational transformations to keep everyone in a multiplayer repl in sync.',
    'Repl.it uses operational transformations.',
    '[{"op": "skip", "count": 45}, {"op": "delete", "count": 47}]',
    False,
  ),
  (
    'Repl.it uses operational transformations to keep everyone in a multiplayer repl in sync.',
    'Repl.it uses operational transformations.',
    '[{"op": "skip", "count": 40}, {"op": "delete", "count": 47}, {"op": "skip", "count": 2}]',
    False,
  ),
  (
    'Repl.it uses operational transformations to keep everyone in a multiplayer repl in sync.',
    'We use operational transformations to keep everyone in a multiplayer repl in sync.',
    '[{"op": "delete", "count": 7}, {"op": "insert", "chars": "We"}, {"op": "skip", "count": 4}, {"op": "delete", "count": 1}]',
    True,
  ),
  (
    'Repl.it uses operational transformations to keep everyone in a multiplayer repl in sync.',
    'We can use operational transformations to keep everyone in a multiplayer repl in sync.',
    '[{"op": "delete", "count": 7}, {"op": "insert", "chars": "We"}, {"op": "skip", "count": 4}, {"op": "delete", "count": 1}]',
    False,
  ),
  (
    'Repl.it uses operational transformations to keep everyone in a multiplayer repl in sync.',
    'Repl.it uses operational transformations to keep everyone in a multiplayer repl in sync.',
    '[]',
    True,
  )
]:
  res, reason = is_valid(stale, latest, ot_json)
  if res == expected:
    print(f'Result is {res} as expected {reason=}')
  else:
    print(f'Expected {expected}, got {res} with {reason=}')
  print()
