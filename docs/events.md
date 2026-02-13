# Event System

The Math SDK uses a standardized event system to track all game actions and outcomes.

## Overview

Events are the primary way to record game actions:
- Wins and payouts
- Feature triggers (free spins, bonuses)
- Board transformations (tumbles, upgrades)
- Special symbol actions (multipliers, wilds)

All events are stored in the books files and consumed by the frontend to render animations.

## EventConstants

**Always use `EventConstants`** instead of hardcoded strings:

```python
from src.events.event_constants import EventConstants

# ✅ Good
event_type = EventConstants.WIN.value

# ❌ Bad
event_type = "win"
```

### Standard Event Types

**Wins**
- `EventConstants.WIN` - Basic win event
- `EventConstants.SET_FINAL_WIN` - Set final win amount
- `EventConstants.SET_WIN` - Set win for current stage
- `EventConstants.SET_TOTAL_WIN` - Set cumulative win
- `EventConstants.WIN_CAP` - Win cap applied

**Free Spins**
- `EventConstants.TRIGGER_FREE_SPINS` - Trigger free spins
- `EventConstants.RETRIGGER_FREE_SPINS` - Retrigger during free spins
- `EventConstants.END_FREE_SPINS` - Free spins ended

**Tumbles/Cascades**
- `EventConstants.TUMBLE` - Board tumble/cascade
- `EventConstants.SET_TUMBLE_WIN` - Win from tumble
- `EventConstants.UPDATE_TUMBLE_WIN` - Update tumble win

**Special Symbols**
- `EventConstants.UPDATE_GLOBAL_MULTIPLIER` - Global multiplier change
- `EventConstants.UPDATE_BOARD_MULTIPLIER` - Board multiplier information
- `EventConstants.UPGRADE` - Symbol upgrade
- `EventConstants.REVEAL` - Reveal hidden symbols
- `EventConstants.REVEAL_EXPANDING_WILDS` - Reveal new expanding wild symbols
- `EventConstants.UPDATE_EXPANDING_WILDS` - Update existing expanding wilds
- `EventConstants.ADD_STICKY_SYMBOLS` - Add new sticky symbols

## Creating Events

### Basic Event

```python
from src.events.event_constants import EventConstants
from src.events.events import construct_event

event = construct_event(
    event_type=EventConstants.WIN.value,
    amount=10.0
)

self.book.add_event(event)
```

### Event with Details

```python
event = construct_event(
    event_type=EventConstants.WIN.value,
    amount=10.0,
    details={
        "symbols": ["A", "A", "A"],
        "positions": [[0, 0], [0, 1], [0, 2]],
        "multiplier": 2
    }
)

self.book.add_event(event)
```

### Free Spin Trigger

```python
event = construct_event(
    event_type=EventConstants.TRIGGER_FREE_SPINS.value,
    details={
        "count": 10,
        "scatter_positions": [[1, 0], [2, 1], [3, 2]]
    }
)

self.book.add_event(event)
```

### Tumble/Cascade

```python
event = construct_event(
    event_type=EventConstants.TUMBLE.value,
    details={
        "removed_positions": [[0, 0], [0, 1]],
        "new_symbols": [["K", 0, 0], ["Q", 0, 1]]
    }
)

self.book.add_event(event)
```

### Global Multiplier

```python
event = construct_event(
    event_type=EventConstants.UPDATE_GLOBAL_MULTIPLIER.value,
    details={
        "old_multiplier": 1,
        "new_multiplier": 2,
        "increment": 1
    }
)

self.book.add_event(event)
```

## Event Flow in a Spin

Typical event sequence:

```python
def run_spin(self):
    # 1. Draw board
    self.draw_board()

    # 2. Calculate and record wins
    self.calculate_wins()  # Adds WIN events

    # 3. Check for tumbles/cascades
    if self.has_winning_clusters():
        while self.has_wins():
            self.book.add_event(construct_event(
                event_type=EventConstants.TUMBLE.value
            ))
            self.remove_winning_symbols()
            self.drop_symbols()
            self.calculate_wins()

    # 4. Check for feature triggers
    if self.check_free_spin_condition():
        self.book.add_event(construct_event(
            event_type=EventConstants.TRIGGER_FREE_SPINS.value,
            details={"count": 10}
        ))
        self.run_free_spin_from_base()

    # 5. Set final win
    self.book.add_event(construct_event(
        event_type=EventConstants.SET_FINAL_WIN.value,
        amount=self.book.get_total_win()
    ))

    return self.book
```

## Custom Events

### Defining Custom Events

For game-specific events, extend `EventConstants`:

```python
# games/<game_name>/game_events.py

from enum import Enum

class CustomEvents(Enum):
    COLLECT_SYMBOL = "collect_symbol"
    FILL_METER = "fill_meter"
    TRANSFORM_REEL = "transform_reel"
```

Usage:
```python
from games.my_game.game_events import CustomEvents

event = construct_event(
    event_type=CustomEvents.COLLECT_SYMBOL.value,
    details={"symbol": "M", "position": [2, 1]}
)
```

### Custom Event Details

Structure event details for frontend consumption:

```python
# Symbol collection mechanic
event = construct_event(
    event_type=CustomEvents.COLLECT_SYMBOL.value,
    details={
        "symbol": "coin",
        "position": [2, 1],
        "value": 5,
        "total_collected": 25,
        "meter_progress": 0.5  # 50% full
    }
)

# Reel transformation
event = construct_event(
    event_type=CustomEvents.TRANSFORM_REEL.value,
    details={
        "reel": 2,
        "from_symbols": ["A", "K", "Q"],
        "to_symbols": ["W", "W", "W"],  # All wilds
        "trigger": "scatter_on_reel_5"
    }
)
```

## Event Best Practices

### 1. Use Constants
```python
# ✅ Good
EventConstants.WIN.value

# ❌ Bad
"win"
```

### 2. Include Relevant Details
```python
# ✅ Good - frontend knows what to animate
event = construct_event(
    event_type=EventConstants.WIN.value,
    amount=10.0,
    details={
        "symbols": ["A", "A", "A"],
        "positions": [[0,0], [0,1], [0,2]],
        "payline": "L1"
    }
)

# ❌ Bad - frontend doesn't know what won
event = construct_event(
    event_type=EventConstants.WIN.value,
    amount=10.0
)
```

### 3. Event Order Matters
```python
# ✅ Good - logical sequence
self.book.add_event(win_event)
self.book.add_event(multiplier_event)
self.book.add_event(final_win_event)

# ❌ Bad - confusing order
self.book.add_event(final_win_event)
self.book.add_event(win_event)
```

### 4. One Event Per Action
```python
# ✅ Good - separate events
self.book.add_event(tumble_event)
self.book.add_event(new_win_event)

# ❌ Bad - combining unrelated actions
self.book.add_event({
    "tumble": True,
    "win": 10.0
})
```

## Events in Books Files

Events appear in books as:

```json
{
  "board": [["A", "K", "Q"], ...],
  "events": [
    {
      "type": "win",
      "amount": 5.0,
      "details": {
        "symbols": ["A", "A", "A"],
        "positions": [[0, 0], [0, 1], [0, 2]]
      }
    },
    {
      "type": "triggerFreeSpins",
      "details": {
        "count": 10,
        "scatter_positions": [[1, 0], [2, 1], [3, 2]]
      }
    },
    {
      "type": "setFinalWin",
      "amount": 5.0
    }
  ],
  "final_win": 5.0
}
```

## Frontend Consumption

The frontend processes events sequentially:

1. **Parse event type**: Determine animation to play
2. **Extract details**: Get positions, symbols, values
3. **Animate**: Play corresponding animation
4. **Update UI**: Show wins, meters, counters

Example frontend logic:
```javascript
// Pseudo-code
events.forEach(event => {
  switch(event.type) {
    case 'win':
      highlightSymbols(event.details.positions);
      showWinAmount(event.amount);
      break;

    case 'trigger_free_spins':
      playTriggerAnimation();
      show_free_spin_count(event.details.count);
      break;

    case 'tumble_board':
      animateTumble(event.details.removed_positions);
      dropNewSymbols(event.details.new_symbols);
      break;
  }
});
```

## Debugging Events

### Print Events

```python
# In game_state.py
def run_spin(self):
    # ... game logic ...

    # Debug: print all events
    for event in self.book.events:
        print(f"Event: {event['type']}, Amount: {event.get('amount', 'N/A')}")
```

### Validate Events

```python
# Check event structure
def validate_event(event):
    assert "type" in event, "Event missing type"
    assert event["type"] in [e.value for e in EventConstants], f"Unknown event type: {event['type']}"

    if "amount" in event:
        assert isinstance(event["amount"], (int, float)), "Amount must be numeric"
```

## See Also

- [Game Structure](game-structure.md) - Where events fit in game architecture
- [Running Games](running-games.md) - Viewing events in books files
