# Prev Levels + Sessions Refactor Plan

## Goal

Refine `Levels/prev_levels_sessions_refactor.pine` so label rendering matches the level lines more cleanly and overlapping equal-price levels are merged into a single readable label.

The current script already supports:

- previous timeframe highs/lows
- previous `RTH` highs/lows
- previous `Asia`, `London`, and `New York` session highs/lows

So this plan focuses only on the remaining rendering issue, not on adding new level families.

---

## Current Issue

The indicator logic is mostly working, but the label layer still has 2 problems:

1. labels sit too far away from the lines
   - labels are vertically offset by a percentage of recent range
   - on volatile charts this pushes them noticeably above high lines and below low lines

2. same-price labels do not merge
   - if two enabled levels share the same exact price, the script currently creates separate labels
   - collision avoidance then pushes them apart instead of combining them into one label like `D L | 1H L`

---

## Root Cause In The Current Script

### Vertical offset

The current label position is built from:

- `labelOffsetPct`
- `recentRange`
- `labelOffset`

Then each label uses:

- `levelPrice + labelOffset` for highs
- `levelPrice - labelOffset` for lows

This means labels are intentionally detached from the level line before collision handling even starts.

### Collision handling

The current collision helper tracks already used y-values and keeps shifting new labels:

- highs move upward
- lows move downward

That works for nearby-but-different prices, but it does not understand that two labels at the same level should be merged rather than separated.

### One-level-one-label structure

Right now the render pass creates one persistent label per source:

- `lbDHigh`
- `lb1HHigh`
- `lbDLow`
- `lb1HLow`
- etc.

That architecture makes it hard to support dynamic merged labels because the number of visible labels should depend on grouped price levels, not on the raw number of sources.

---

## Desired End State

The script should keep all lines at their exact prices and improve only the label display.

### Label placement

- labels should sit on the level price or as close to it as Pine allows visually
- highs should still be eligible to stack upward when needed
- lows should still be eligible to stack downward when needed
- collision shifting should happen only when separate price groups are too close to each other

### Label merging

If multiple enabled levels share the same side and same normalized price, they should be merged into one label.

Examples:

- `D H | 1H H`
- `D L | 1H L`
- `W H | D H | 4H H`

### Important rule

- lines never move
- only labels are aggregated or shifted

---

## Non-Repainting Constraint

The refactor must preserve the current level source logic exactly.

Do not change:

- previous timeframe requests using confirmed prior values
- current `request.security()` lookahead usage
- session start/end detection
- previous completed session storage

This is a label-rendering refactor only.

---

## Pine-Specific Constraints

### Single label color

A Pine `label` can only use one `textcolor`.

So if a merged label contains multiple sources, we must choose one color owner.

Recommended rule:

- use the first merged source color based on fixed priority order

Recommended priority order:

- `1M`
- `W`
- `D`
- `4H`
- `90m`
- `1H`
- `15m`
- `5m`
- `RTH`
- `Asia`
- `London`
- `NY`

This makes higher timeframe labels visually dominant when merged.

### Float equality

Equal prices should not rely on raw float equality.

Recommended grouping rule:

- normalize prices to `syminfo.mintick`
- merge levels when normalized prices match and both are on the same side (`high` with `high`, `low` with `low`)

### Label anchoring limitation

With `yloc.price` and `label.style_none`, Pine anchors text to a price level, but text height is still pixel-based.

So "exactly on the line" is approximate in practice.

Recommended behavior:

- anchor labels at `levelPrice`
- only apply a tiny mintick-based nudge if visual testing proves necessary

---

## Implementation Strategy

### Phase 1: keep all line logic unchanged

Leave line creation and updating exactly as it is now.

This preserves:

- current level visibility
- current styling inputs
- current non-repainting behavior

### Phase 2: split label rendering into an aggregation pass

Instead of calling `updateLevelLabel()` immediately for each source, collect enabled label candidates first.

Each candidate should store:

- price
- side (`high` or `low`)
- text
- color
- priority

Example candidate rows:

- `{price: prevDLow, side: low, text: "D L", color: colDLow, priority: 3}`
- `{price: prev1HLow, side: low, text: "1H L", color: col1HLow, priority: 6}`

### Phase 3: merge equal-price candidates

Group candidates by:

- normalized price
- side

Then build one merged display row per group.

Each merged row should produce:

- merged text joined with ` | `
- one chosen text color based on priority
- one final anchor price

### Phase 4: run collision avoidance on merged groups only

After merge, apply collision handling only across distinct merged rows.

Recommended behavior:

- start with `desiredY = levelPrice`
- if another merged row on the same side is too close, shift by collision step
- highs shift upward
- lows shift downward

This keeps true duplicates merged while still deconflicting genuinely crowded nearby levels.

### Phase 5: replace fixed label variables with a reusable label pool

The current fixed label variables do not fit dynamic merge counts.

Recommended refactor:

- keep line variables as they are
- replace the many dedicated label variables with pooled label arrays
- update labels by index during the last-bar render pass
- delete extra pooled labels when fewer merged groups are visible

This gives flexible support for merged labels without breaking object reuse.

---

## Recommended Data Flow

Inside `if barstate.islast`:

1. clear collision-tracking arrays
2. update all level lines exactly as today
3. collect enabled label candidates into temporary arrays
4. merge same-price candidates by side
5. compute final y-position per merged row
6. update pooled labels
7. delete any unused pooled labels

---

## Recommended Helper Responsibilities

### Keep

- `updateLevelLine()`
- `getPrevTfLevel()`
- session high/low tracking logic

### Modify or replace

- replace direct per-source `updateLevelLabel()` usage with aggregated rendering
- either simplify `updateLevelLabel()` to operate on merged rows, or replace it with a pooled label updater

### Add

- price normalization helper
- label candidate collector helper
- merge helper for same-price rows
- pooled label update helper

---

## Collision Rules

### Merge first

If two sources belong to the same side and same normalized price:

- do not stack them
- do not create separate labels
- merge them into one label

### Shift only after merge

If two merged rows are still too close:

- highs shift upward
- lows shift downward

### Spacing basis

Keep the current recent-range-based collision step for now because it already adapts across markets.

But reduce or remove the default base label offset so labels no longer start far from the line.

---

## Recommended Defaults After Refactor

- merged labels enabled by default
- label anchor at the level price
- collision avoidance enabled
- highs stack upward only when needed
- lows stack downward only when needed
- higher timeframe color wins merged label ownership

---

## Build Order

### Step 1

Preserve all existing level calculations and line updates.

### Step 2

Refactor the last-bar label render pass into candidate collection.

### Step 3

Add mintick-normalized grouping and merged text generation.

### Step 4

Apply collision handling only to merged rows.

### Step 5

Replace fixed source label storage with pooled reusable labels.

### Step 6

Lint and visually verify in TradingView.

---

## Validation Checklist

After coding, verify these cases:

1. a single level label sits on or very near its line
2. `D L` and `1H L` at the same price become `D L | 1H L`
3. `D H` and `1H H` at the same price become `D H | 1H H`
4. nearby but different prices still stack cleanly
5. disabling a source removes its contribution from merged labels
6. no extra stale labels remain after visibility changes
7. previous timeframe and session values remain unchanged versus current behavior

---

## Final Recommendation

The correct next step is not another broad refactor of the level engines.

The proper change is a focused label-rendering refactor that:

1. keeps the existing non-repainting price logic intact
2. removes the large default label displacement from the line
3. merges equal-price labels into a single string like `D | 1H`
4. preserves collision avoidance only for distinct nearby price groups
5. uses pooled labels so the dynamic merged output stays maintainable

That gives the cleanest fix for the current indicator without disturbing the working level calculations.
