# Quarterly Theory SSMT Indicator Plan

## Goal

Extend `quarterly_theory_ssmt.pine` into a practical auto-mapped SSMT indicator that:

- keeps the current NY-anchored quarterly cycle engine
- supports both manual and automatic comparison-symbol selection
- auto-switches comparison pairs when the chart symbol changes
- supports both positive-correlation SMT and inverse SMT where required
- stays minimal and does not turn into a table-heavy or analytics-heavy script

The target use case is to remove the need to manually swap comparison symbols every time the chart changes.

---

## Current Script Status

The current script already has:

- NY-anchored cycle selection
- quarter-to-quarter high/low tracking
- multiple simultaneous comparison slots
- bullish and bearish SSMT drawing
- historical retention mode

The current script does not yet have:

- auto symbol mapping
- comparison relationship types
- inverse-pair support
- feed-aware defaults for forex, metals, and DXY

The comparison layer is still built around fixed manual slots such as ES and YM.

---

## Core Direction

Do not redesign the SSMT engine.

Keep the current engine and replace only the comparison-selection layer so that:

- the cycle engine remains unchanged
- the quarter tracking model remains unchanged
- the drawing model remains unchanged
- only symbol resolution and signal-condition branching are extended

This is the smallest correct change.

---

## Final v1.5 Scope

### Include

- current cycle choices:
  - `Auto`
  - `22.5m`
  - `90m`
  - `6H`
  - `1D`
  - `1W`
  - `1M`
- NY-anchored cycle logic
- quarter-to-next-quarter SSMT detection
- multiple comparison symbols at the same time
- `Comparison Mode` with `Auto` and `Manual`
- positive-correlation SMT logic
- inverse SMT logic for `DXY` on `EURUSD` and `GBPUSD`
- feed-configurable auto symbols
- historical SSMT retention
- labels showing symbol and inverse relationship where applicable

### Do not include

- copper in the default metals map
- DXY for `AUDUSD` or `NZDUSD`
- inverse-pair expansion beyond `EURUSD` and `GBPUSD`
- scoring/grading system
- analytics tables
- alerts
- multi-quarter pattern chaining
- session-specific forex overrides

---

## Approved Auto Mapping

### Index Futures

- `NQ -> ES, YM`
- `ES -> NQ, YM`
- `YM -> NQ, ES`

### Micro Index Futures

- `MNQ -> MES, MYM`
- `MES -> MNQ, MYM`
- `MYM -> MNQ, MES`

### Forex

- `EURUSD -> GBPUSD (positive), DXY (inverse)`
- `GBPUSD -> EURUSD (positive), DXY (inverse)`
- `AUDUSD -> NZDUSD (positive)`
- `NZDUSD -> AUDUSD (positive)`
- `USDCHF -> USDJPY (positive), USDCAD (positive)`
- `USDJPY -> USDCHF (positive), USDCAD (positive)`
- `USDCAD -> USDCHF (positive), USDJPY (positive)`

### Metals

- `XAUUSD -> XAGUSD (positive)`
- `XAGUSD -> XAUUSD (positive)`

---

## Relationship Types

The indicator now needs to support two relationship types:

- `positive`
- `inverse`

### Positive relationship

Use the current SSMT logic.

Bearish SSMT exists when:

1. chart current quarter high is greater than chart previous quarter high
2. comparison current quarter high is less than or equal to comparison previous quarter high

Bullish SSMT exists when:

1. chart current quarter low is less than chart previous quarter low
2. comparison current quarter low is greater than or equal to comparison previous quarter low

### Inverse relationship

Used only for `DXY` against `EURUSD` and `GBPUSD` in this version.

Bearish SSMT on the chart exists when:

1. chart current quarter high is greater than chart previous quarter high
2. inverse comparison current quarter low is greater than or equal to inverse comparison previous quarter low

Bullish SSMT on the chart exists when:

1. chart current quarter low is less than chart previous quarter low
2. inverse comparison current quarter high is less than or equal to inverse comparison previous quarter high

This is required because the expected directional structure is inverted.

---

## Feed Defaults

### Futures

Use explicit default symbols such as:

- `CME_MINI:NQ1!`
- `CME_MINI:ES1!`
- `CBOT_MINI:YM1!`
- `CME_MINI:MNQ1!`
- `CME_MINI:MES1!`
- `CBOT_MINI:MYM1!`

### Forex and Metals

Use `OANDA` defaults for the auto symbol inputs:

- `OANDA:EURUSD`
- `OANDA:GBPUSD`
- `OANDA:AUDUSD`
- `OANDA:NZDUSD`
- `OANDA:USDCHF`
- `OANDA:USDJPY`
- `OANDA:USDCAD`
- `OANDA:XAUUSD`
- `OANDA:XAGUSD`

### DXY

Use `TVC:DXY` as the default dollar index source.

Reason:

- it is a common TradingView source for the dollar index
- it is suitable as a macro confirmation source
- it does not need to come from the forex broker feed family

Still expose it as an input in case the user prefers another feed later.

---

## Input Design

### Group: Cycle Settings

- `Cycle` -> `Auto`, `22.5m`, `90m`, `6H`, `1D`, `1W`, `1M`

### Group: Comparison Mode

- `Comparison Mode` -> `Auto`, `Manual`

### Group: Auto Symbols

Add configurable default symbols for the supported auto-map universe:

- `NQ Auto Symbol`
- `ES Auto Symbol`
- `YM Auto Symbol`
- `MNQ Auto Symbol`
- `MES Auto Symbol`
- `MYM Auto Symbol`
- `EURUSD Auto Symbol`
- `GBPUSD Auto Symbol`
- `AUDUSD Auto Symbol`
- `NZDUSD Auto Symbol`
- `USDCHF Auto Symbol`
- `USDJPY Auto Symbol`
- `USDCAD Auto Symbol`
- `XAUUSD Auto Symbol`
- `XAGUSD Auto Symbol`
- `DXY Auto Symbol`

### Group: Manual Comparison Symbols

Keep the current manual controls as fallback mode:

- `Compare With ES`
- `ES Symbol`
- `Compare With YM`
- `YM Symbol`
- `Enable Custom Symbol 1`
- `Custom Symbol 1`
- `Custom Label 1`
- `Enable Custom Symbol 2`
- `Custom Symbol 2`
- `Custom Label 2`

### Group: Signal Settings

- `Show Bearish SSMT`
- `Show Bullish SSMT`

### Group: Historical Settings

- `Show Historical SSMT`
- `Historical SSMT To Keep`

### Group: Display Settings

- `Show Labels`
- `Show Active Cycle Tag`
- `Bearish Line Color`
- `Bullish Line Color`
- `Line Width`
- `Line Style`

---

## Data Model

For the chart symbol, keep tracking:

- previous quarter high
- previous quarter low
- previous quarter high bar
- previous quarter low bar
- current quarter high
- current quarter low
- current quarter high bar
- current quarter low bar

For each comparison slot, track:

- enabled flag
- symbol
- label name
- relationship type
- previous quarter high
- previous quarter low
- current quarter high
- current quarter low

### Fixed Slot Count

Keep `COMPARISON_COUNT = 4`.

This is enough for:

- 2 auto pairs in the current approved mappings
- 2 manual custom slots in manual mode

No slot-count expansion is needed in this pass.

---

## Symbol Normalization Strategy

Auto mode needs a stable chart key that works across futures and forex.

### Futures

Use `syminfo.root`.

Examples:

- `NQ1! -> NQ`
- `ES1! -> ES`
- `MNQ1! -> MNQ`

### Forex and Metals

Use `syminfo.ticker`.

Examples:

- `EURUSD -> EURUSD`
- `XAUUSD -> XAUUSD`

### Why

This lets the script re-map automatically whenever the chart symbol changes, while still using the correct key for continuous futures.

---

## Auto Mode Behavior

When `Comparison Mode = Auto`:

1. detect the chart key from `syminfo.root` or `syminfo.ticker`
2. resolve the approved comparison map for that key
3. populate the comparison arrays from the auto-symbol inputs
4. populate relationship type for each comparison
5. fetch comparison data from those resolved symbols
6. apply positive or inverse SSMT logic based on relationship type

If the chart key is not mapped:

- disable all comparison slots
- draw nothing
- do not error

Do not guess unsupported mappings.

---

## Manual Mode Behavior

When `Comparison Mode = Manual`:

- keep the current ES/YM/custom setup
- populate comparison arrays exactly from manual inputs
- assign `positive` relationship type to all manual slots in this version

Manual mode remains the fallback and debugging mode.

---

## request.security Strategy

Refactor the request layer so it is slot-driven instead of hardcoded per symbol.

### Preferred request pattern

For each active comparison slot, request high and low together:

- `request.security(symbol, timeframe.period, [high, low], gaps=barmerge.gaps_on, lookahead=barmerge.lookahead_off, ignore_invalid_symbol=true)`

### Why

- simpler than maintaining `cmpHigh0`, `cmpLow0`, etc.
- matches Pine v6 dynamic request capability
- fewer repeated requests
- safer when auto symbols change by chart

### Important settings

- `lookahead = barmerge.lookahead_off`
- `ignore_invalid_symbol = true`

This avoids future leakage and prevents hard runtime failure when a symbol feed is unavailable.

---

## Detection Logic

### Step 1: Determine active cycle

Reuse the existing NY-anchored cycle logic.

### Step 2: Detect quarter rollover

Reuse the existing quarter-start logic.

### Step 3: Track chart quarter extremes

Reuse the existing chart-symbol extreme tracking.

### Step 4: Track comparison quarter extremes

For each enabled comparison slot:

- maintain current quarter high and low
- roll current values into previous values at quarter start

### Step 5: Branch by relationship type

For each enabled comparison slot:

- if relationship is `positive`, use positive SSMT conditions
- if relationship is `inverse`, use inverse SSMT conditions

### Step 6: Draw lines and labels

Keep the current draw behavior.

The line is always drawn on the chart symbol using the chart symbol's previous and current quarter sweep points.

Label examples:

- `Bearish SSMT vs ES`
- `Bullish SSMT vs YM`
- `Bearish SSMT vs DXY (inv)`
- `Bullish SSMT vs DXY (inv)`

---

## Historical Mode Behavior

### When off

- show only live active SSMT lines and labels
- update or replace them as price evolves

### When on

- preserve completed SSMT lines and labels from prior quarters
- keep only the latest `N` retained signals
- delete oldest retained signals when the limit is exceeded

No change in retention architecture is required.

---

## How Simultaneous Comparisons Should Work

Each comparison slot is independent.

Examples:

- on `NQ`, `ES` may diverge while `YM` does not
- on `EURUSD`, `GBPUSD` may confirm one structure while `DXY` shows inverse SMT on the same chart
- if two comparisons diverge at once, both labels and lines may exist independently

This is already aligned with the current per-slot draw model.

---

## Special Notes on DXY

`DXY` should not be treated as a standard same-direction forex pair.

In this indicator version:

- `DXY` is only added to `EURUSD` and `GBPUSD`
- `DXY` is always treated as `inverse`
- `DXY` is a secondary macro confirmation comparison, not a replacement for `EURUSD <-> GBPUSD`

This gives proper structure without distorting the rest of the script.

---

## Special Notes on Metals

Keep the default metals pair as:

- `XAUUSD <-> XAGUSD`

Do not add copper in this version.

Reason:

- gold and silver are the cleaner SMT pair
- copper behaves differently and would add noise unless a separate industrial-metals mapping is introduced later

---

## Recommended Build Order

### Phase 1: Comparison mode and symbol inputs

- add `Comparison Mode`
- add `Auto Symbols` input group
- keep `Manual Comparison Symbols` group intact

### Phase 2: Auto mapping layer

- add chart-key normalization helper
- add auto-map resolver helper
- add relationship-type array

### Phase 3: Request layer refactor

- replace hardcoded comparison requests with slot-driven requests
- request `[high, low]` together
- add `ignore_invalid_symbol = true`

### Phase 4: Signal branching

- keep positive logic for standard pairs
- add inverse logic for `DXY`
- update label text for inverse relationships

### Phase 5: Verification

Validate these chart cases:

- `NQ`
- `ES`
- `MNQ`
- `EURUSD`
- `GBPUSD`
- `AUDUSD`
- `XAUUSD`
- `USDCHF`

---

## Verification Checklist

### Mapping checks

- `NQ` auto-selects `ES` and `YM`
- `ES` auto-selects `NQ` and `YM`
- `MNQ` auto-selects `MES` and `MYM`
- `EURUSD` auto-selects `GBPUSD` and `DXY`
- `GBPUSD` auto-selects `EURUSD` and `DXY`
- `AUDUSD` auto-selects `NZDUSD`
- `XAUUSD` auto-selects `XAGUSD`
- `USDCHF` auto-selects `USDJPY` and `USDCAD`

### Logic checks

- positive-pair SSMT still behaves exactly as before
- `EURUSD` vs `DXY` uses inverse logic correctly
- `GBPUSD` vs `DXY` uses inverse logic correctly
- switching chart symbol updates auto mappings with no manual input changes
- unavailable symbols return `na` and do not crash the indicator

---

## Final Recommendation

Implement auto mapping by extending the current indicator, not by rewriting it.

### Final architecture

- keep the existing cycle engine
- keep the existing quarter tracking model
- keep the existing line and label retention model
- add a new mapping and relationship layer above the current comparison engine

This is the cleanest path for:

- index futures now
- forex and metals now
- inverse `DXY` support for `EURUSD` and `GBPUSD`
- minimal risk to the current script structure

---

## Next Implementation Task

When editing `quarterly_theory_ssmt.pine`, do it in this order:

1. add `Comparison Mode`
2. add `Auto Symbols` inputs with futures defaults, `OANDA` forex/metals defaults, and `TVC:DXY`
3. add chart-key normalization
4. add auto-map resolver and relationship-type tracking
5. refactor comparison requests to be slot-driven
6. add inverse `DXY` logic for `EURUSD` and `GBPUSD`
7. update labels to include inverse marker
8. lint and verify the mapped chart cases
