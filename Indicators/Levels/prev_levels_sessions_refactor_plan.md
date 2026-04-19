# Prev Levels + Sessions Refactor Plan

## Goal

Refine `Levels/prev_levels_sessions_refactor.pine` so the chart stays readable by showing only levels that are still untaken.

The script already supports:

- previous timeframe highs/lows
- previous `RTH` highs/lows
- previous `Asia`, `London`, and `New York` session highs/lows
- merged labels and tighter label placement

So the next plan focuses on reducing congestion by hiding levels after price has taken them.

---

## Current Issue

The current indicator looks much better than before, but it can still become crowded because all previous levels remain visible until a newer level replaces them.

That means:

- old highs can stay on screen even after price has already traded through them
- old lows can stay on screen even after price has already traded through them
- the chart keeps historical context, but the active execution view becomes cluttered

---

## Proposed Solution

Hide a level once it has been taken or mitigated.

In practice:

- a previous high should disappear once price confirms it has traded through that high
- a previous low should disappear once price confirms it has traded through that low

This keeps the indicator focused on untouched liquidity or untouched reference levels.

---

## Feasibility

This is fully feasible in Pine Script v6.

The current script already redraws lines and labels from the latest state, so it is straightforward to conditionally stop rendering a level after it is taken.

No major rewrite is required.

---

## Detection Rules

There are 2 practical ways to define when a level is taken.

### Option 1: wick touch

- high taken when `high >= levelPrice`
- low taken when `low <= levelPrice`

Pros:

- reacts immediately
- removes clutter faster

Cons:

- can disappear intrabar and reappear conceptually if the user expects close confirmation
- less stable during live candles

### Option 2: close beyond

- high taken when `close >= levelPrice`
- low taken when `close <= levelPrice`

Pros:

- more stable
- cleaner from a non-repainting perspective
- usually closer to how traders define a confirmed sweep or mitigation

Cons:

- levels stay visible until the candle closes through them

### Recommendation

Use `close beyond` as the default behavior.

This is the cleanest first implementation and avoids noisy intrabar hiding.

---

## Non-Repainting Consideration

The level sources themselves should remain unchanged.

Do not change:

- previous timeframe requests using confirmed prior values
- current `request.security()` lookahead usage
- session start/end detection
- previous completed session storage

Only the visibility of already-calculated levels should change.

Recommended behavior:

- mark a level as taken only using confirmed bar-close logic
- hide the line and label after that confirmation

This preserves the current stable level-calculation logic.

---

## Desired End State

The final behavior should be:

- untouched previous highs remain visible
- untouched previous lows remain visible
- taken highs disappear
- taken lows disappear
- labels disappear together with the level line
- when a new previous period/session level forms, it behaves normally until taken

Example:

- previous day high is visible while price remains below it
- once a candle closes above that previous day high, the `D H` line and label are hidden
- the same logic applies to `W`, `1H`, `RTH`, `Asia`, `London`, and `NY` levels

---

## Rendering Strategy

The best approach is to conditionally hide levels, not permanently delete logic from the script.

In practice:

- compute whether each level is taken
- if taken, do not pass it into the line renderer
- if taken, do not pass it into the label candidate collector

This keeps the code simple and works well with the current render model.

---

## Recommended Helper

Add a helper like:

- `isLevelTaken(levelPrice, isHigh)`

Recommended first implementation:

- for highs: return `close >= levelPrice`
- for lows: return `close <= levelPrice`

Optional later:

- support a user input to switch between `close` and `wick` mode

---

## Code Areas To Change

### Keep unchanged

- `getPrevTfLevel()`
- timeframe enable logic
- session tracking logic
- line update helper structure
- merged label structure

### Add or modify

1. add a small taken-detection helper near the shared rendering helpers
2. compute per-level visibility as `enabled and not taken`
3. pass that filtered visibility into `updateLevelLine(...)`
4. use the same filtered visibility for label collection so taken lines do not still show labels

---

## Recommended Data Flow

Inside `if barstate.islast`:

1. calculate each previous level as today
2. calculate whether that level is taken
3. derive final render visibility from:
   - source enabled
   - category enabled
   - not taken
4. draw only untaken lines
5. collect labels only for untaken levels
6. merge labels as today
7. render merged labels as today

---

## Behavior Choice: Temporary Hide vs Persistent Taken State

There are 2 ways to manage taken levels.

### Simpler option: direct conditional hide

Every bar, determine:

- is this level taken right now?

If yes:

- do not render it

Pros:

- smallest code change
- easy to reason about
- no extra state variables needed

### More advanced option: persistent taken flags

Store booleans so once a level is taken, it stays marked taken until the next previous level replaces it.

Pros:

- more explicit lifecycle

Cons:

- more state management
- more reset logic required when the source level changes

### Recommendation

Start with direct conditional hide.

That is the cleanest version for this script.

---

## Inputs Recommendation

### First version

No extra input required if we use a fixed rule:

- close beyond = taken

### Optional later input

If needed later, add:

- `Hide Taken Levels`
- `Taken Detection Mode` with options:
  - `Close`
  - `Wick`

But for now, keep it simple.

---

## Validation Checklist

After coding, verify these cases:

1. an untouched high remains visible
2. an untouched low remains visible
3. a high disappears after a candle closes through it
4. a low disappears after a candle closes through it
5. the matching label disappears with the line
6. a newly formed previous level appears correctly after the next source period/session completes
7. merged labels still work when multiple untaken levels share the same price
8. level calculations themselves remain unchanged

---

## Final Recommendation

The next change should be a focused untaken-level filter, not another structural rewrite.

The right implementation is:

1. keep the current previous level calculations exactly as they are
2. define a small helper for whether a high or low has been taken
3. use `close beyond` as the default confirmation rule
4. hide both the line and label once taken
5. leave merged-label logic in place for untaken overlapping levels

This will reduce chart congestion significantly while preserving the current indicator behavior and keeping the code change small.
