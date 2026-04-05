# Quarterly Theory Non-Sequential SSMT / Doubling SMT Indicator Plan

## Goal

Build a new Pine Script indicator for **Non-Sequential SSMT** that keeps the same practical feature set as `SSMT/quarterly_theory_ssmt.pine`, but replaces the quarter reference model.

This new indicator should:

- keep the same NY-anchored cycle engine
- keep the same auto and manual intermarket comparison-symbol system
- keep the same inverse `DXY` handling for `EURUSD` and `GBPUSD`
- keep the same historical retention and display behavior
- replace adjacent-quarter comparison with a fixed non-sequential quarter-class comparison model

This indicator should be separate from the current `SSMT` script.

---

## File Strategy

Use a separate folder and file:

- folder: `Doubling_SSMT/`
- file: `quarterly_theory_doubling_ssmt.pine`

Do not merge this into `SSMT/quarterly_theory_ssmt.pine`.

### Why separate is better

- the current `SSMT` script is now cleanly built around adjacent previous-quarter logic
- this new model needs completed quarter history storage and quarter-class lookup
- keeping them separate makes each script easier to reason about and debug
- both indicators can coexist on the chart if needed

---

## Core Concept

This indicator is **not** sequential quarter-to-next-quarter SSMT.

Instead, each active quarter compares against one or more **non-adjacent quarter classes**.

### Approved Quarter-Class Mapping

- `Q1 -> none`
- `Q2 -> none`
- `Q3 -> Q1`
- `Q4 -> Q1, Q2`

This means the active quarter will use the most recent completed quarter record of the mapped quarter class.

Examples:

- active `Q1` does not produce Non-Sequential / Doubling SMT references
- active `Q2` does not produce Non-Sequential / Doubling SMT references
- active `Q3` compares against the latest completed `Q1`
- active `Q4` compares against the latest completed `Q1` and latest completed `Q2`

---

## Naming

Use the name:

- `Non-Sequential SSMT`

Short internal name:

- `NSSMT`
- `Doubling SMT`

Suggested title:

- `Quarterly Theory Non-Sequential SSMT / Doubling SMT | Auto NY Cycles`

---

## Scope

### Include

- same cycle choices as current `SSMT`
  - `Auto`
  - `22.5m`
  - `90m`
  - `6H`
  - `1D`
  - `1W`
  - `1M`
- NY-anchored cycle logic
- non-sequential quarter reference model
- multiple comparison symbols at the same time
- `Comparison Mode` with `Auto` and `Manual`
- same approved auto symbol map as current `SSMT`
- positive-correlation SMT logic
- inverse SMT logic for `DXY` on `EURUSD` and `GBPUSD`
- historical line and label retention
- labels showing comparison symbol and reference quarter class

### Do not include in the first pass

- alerts
- score/grading system
- optional quarter-pair customization UI
- copper in metals map
- DXY expansion beyond `EURUSD` and `GBPUSD`
- multi-reference consensus rules such as requiring both quarter references to agree before signaling

---

## Reused Comparison Mapping

Carry over the same comparison map from `SSMT/quarterly_theory_ssmt.pine`.

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

## Feature Parity With Current SSMT

The new indicator should preserve all of these behaviors from the current script:

- auto/manual comparison mode
- auto symbol defaults
- symbol normalization using `syminfo.root` and `syminfo.ticker`
- slot-driven `request.security()` calls
- same positive and inverse relationship types
- same line and label creation style
- same historical retention behavior
- same display settings and UI structure where possible

The only major engine change should be the reference-quarter source.

---

## Key Difference From Current SSMT

### Current SSMT

Uses:

- chart current quarter extremes
- chart previous quarter extremes
- comparison current quarter extremes
- comparison previous quarter extremes

### New NSSMT

Must use:

- chart current quarter extremes
- comparison current quarter extremes
- most recent completed reference quarter record(s) based on active quarter class
- most recent completed reference quarter record(s) for each comparison symbol using the same target quarter class

So the current script's `previous quarter` variables are not sufficient on their own.

---

## Data Model

### Current Quarter State

For the chart symbol, track live current-quarter values:

- current quarter high
- current quarter low
- current quarter high bar
- current quarter low bar
- current quarter class
- current cycle start

For each comparison slot, track live current-quarter values:

- current quarter high
- current quarter low

### Completed Quarter History

For the chart symbol, maintain arrays of completed quarter records containing:

- quarter class: `0..3` or `Q1..Q4`
- cycle start timestamp
- quarter high
- quarter low
- quarter high bar index
- quarter low bar index

For each comparison slot, maintain equivalent completed quarter history arrays containing:

- quarter class
- cycle start timestamp
- quarter high
- quarter low

### Recommended Retention

Keep a bounded rolling history per symbol, for example the latest `12` or `16` completed quarters.

This is enough to support the approved quarter-class mapping without unbounded memory growth.

---

## Quarter-Class Reference Rules

Use the following lookup table:

- if active quarter is `Q1`, there is no target reference
- if active quarter is `Q2`, there is no target reference
- if active quarter is `Q3`, target reference is `Q1`
- if active quarter is `Q4`, target references are `Q1` and `Q2`

### Reference selection rule

For each target quarter class, use the **most recent completed quarter record** of that class.

Examples:

- active `Q1` does not evaluate a reference quarter in this model
- active `Q4` can use current-cycle completed `Q1` and `Q2`

This keeps the logic deterministic.

---

## Signal Behavior

### Reference quarters are evaluated independently

If the active quarter has two target references, evaluate them separately.

Examples:

- active `Q1` may produce a signal vs `ES | ref Q3`
- active `Q1` may also produce a signal vs `ES | ref Q4`
- both may appear if both conditions are met

Do not require both reference quarters to agree in v1.

### Why independent is better

- simpler logic
- easier to debug
- preserves visibility into which specific reference quarter produced the signal
- avoids hiding valid setups

---

## Relationship Types

Use the same relationship types as current `SSMT`:

- `positive`
- `inverse`

### Positive relationship logic

Bearish NSSMT exists when:

1. chart current quarter high is greater than chart reference quarter high
2. comparison current quarter high is less than or equal to comparison reference quarter high

Bullish NSSMT exists when:

1. chart current quarter low is less than chart reference quarter low
2. comparison current quarter low is greater than or equal to comparison reference quarter low

### Inverse relationship logic

Used only for `DXY` against `EURUSD` and `GBPUSD` in this version.

Bearish NSSMT exists when:

1. chart current quarter high is greater than chart reference quarter high
2. inverse comparison current quarter low is greater than or equal to inverse comparison reference quarter low

Bullish NSSMT exists when:

1. chart current quarter low is less than chart reference quarter low
2. inverse comparison current quarter high is less than or equal to inverse comparison reference quarter high

---

## Drawing Model

Draw on the chart symbol exactly like the current `SSMT` indicator.

### Bearish line

- `x1 = reference quarter high bar on the chart symbol`
- `y1 = reference quarter high price`
- `x2 = current quarter sweep high bar on the chart symbol`
- `y2 = current quarter sweep high price`

### Bullish line

- `x1 = reference quarter low bar on the chart symbol`
- `y1 = reference quarter low price`
- `x2 = current quarter sweep low bar on the chart symbol`
- `y2 = current quarter sweep low price`

### Label format

Include both comparison symbol and reference quarter class.

Examples:

- `Bearish NSSMT vs ES | Q3`
- `Bullish NSSMT vs YM | Q4`
- `Bearish NSSMT vs DXY (inv) | Q4`

This is required so the user can tell which quarter-class reference produced the signal.

---

## Input Design

Keep the same UI model as current `SSMT` as much as possible.

### Group: Cycle

- `Cycle` -> `Auto`, `22.5m`, `90m`, `6H`, `1D`, `1W`, `1M`

### Group: Comparison

- `Comparison Mode` -> `Auto`, `Manual`

### Group: Auto Map Symbols

Carry over the same auto symbol inputs:

- `NQ`
- `ES`
- `YM`
- `MNQ`
- `MES`
- `MYM`
- `EURUSD`
- `GBPUSD`
- `AUDUSD`
- `NZDUSD`
- `USDCHF`
- `USDJPY`
- `USDCAD`
- `XAUUSD`
- `XAGUSD`
- `DXY`

### Group: Manual Symbols

Carry over the same manual controls:

- `Enable ES`
- `ES Symbol`
- `Enable YM`
- `YM Symbol`
- `Enable Custom 1`
- `Custom 1 Symbol`
- `Custom 1 Label`
- `Enable Custom 2`
- `Custom 2 Symbol`
- `Custom 2 Label`

### Group: Signals

- `Show Bearish NSSMT`
- `Show Bullish NSSMT`

### Group: History

- `Show Historical NSSMT`
- `Historical NSSMT To Keep`

### Group: Display

- `Show Labels`
- `Show Cycle Tag`
- `Line Width`
- `Line Style`
- `Bearish Line Color`
- `Bullish Line Color`

No new input for quarter mapping is needed in v1 because the mapping is fixed by design.

---

## Feed Defaults

Carry over the same feed defaults as current `SSMT`.

### Futures

- `CME_MINI:NQ1!`
- `CME_MINI:ES1!`
- `CBOT_MINI:YM1!`
- `CME_MINI:MNQ1!`
- `CME_MINI:MES1!`
- `CBOT_MINI:MYM1!`

### Forex and Metals

Use `OANDA` defaults:

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

- `TVC:DXY`

---

## request.security Strategy

Reuse the current slot-driven request model.

For each active comparison slot:

- request `[high, low]` together
- use `lookahead = barmerge.lookahead_off`
- use `ignore_invalid_symbol = true`

Do not redesign the comparison request layer unless required.

---

## Engine Changes Required

### 1. Replace previous-quarter storage with quarter history storage

The current script keeps only one completed reference quarter.

This new script must keep a rolling history of completed quarters for:

- chart symbol
- each comparison symbol

### 2. Add quarter-history lookup helpers

Helpers will be needed to:

- push completed quarter records at quarter rollover
- find the latest completed quarter of a target quarter class
- retrieve chart and comparison reference quarter data consistently

### 3. Evaluate multiple reference quarters per active quarter

Some active quarters map to two references, so the script must evaluate:

- comparison slot
- target reference quarter class

independently.

### 4. Expand live object tracking

The current `COMPARISON_COUNT = 4` line/label arrays are tied only to comparison slots.

The new script likely needs a second dimension because one comparison slot may create more than one active signal.

Recommended approach:

- flatten `(comparison slot, reference quarter class)` into a signal slot index
- manage live lines and labels per flattened signal slot

---

## Recommended Signal Slot Model

Because one comparison symbol may produce signals for two reference quarters, define signal capacity separately from comparison capacity.

Example:

- `COMPARISON_COUNT = 4`
- `MAX_REFERENCE_COUNT = 2`
- `SIGNAL_SLOT_COUNT = COMPARISON_COUNT * MAX_REFERENCE_COUNT`

This avoids rewriting the drawing model into nested arrays.

Each signal slot should store:

- comparison slot index
- target reference quarter class
- line
- label

---

## Historical Behavior

Keep the same retention architecture as current `SSMT`.

### When history is off

- only current active NSSMT lines and labels remain visible

### When history is on

- completed signals are retained in arrays
- oldest retained signals are deleted when the cap is exceeded

This logic can be adapted from the current script with minimal changes.

---

## Verification Plan

### Quarter mapping checks

- active `Q1` resolves references `Q3` and `Q4`
- active `Q2` resolves reference `Q4`
- active `Q3` resolves reference `Q1`
- active `Q4` resolves references `Q1` and `Q2`

### Symbol mapping checks

- all current auto comparison mappings resolve exactly as in `SSMT`
- `EURUSD` and `GBPUSD` still include inverse `DXY`

### Logic checks

- positive-pair bearish and bullish logic works against non-adjacent references
- inverse `DXY` logic works against non-adjacent references
- two-reference quarters can show independent signals
- labels clearly identify the reference quarter
- chart switching still updates auto comparison symbols correctly

### Example scenarios to test

- `NQ` during `Q1`: signals may appear vs `ES | Q3`, `ES | Q4`, `YM | Q3`, `YM | Q4`
- `EURUSD` during `Q4`: signals may appear vs `GBPUSD | Q1`, `GBPUSD | Q2`, `DXY (inv) | Q1`, `DXY (inv) | Q2`

---

## Recommended Build Order

### Phase 1

Create the base file:

- `quarterly_theory_doubling_ssmt.pine`
- copy the current `SSMT` input and comparison mapping layer

### Phase 2

Build quarter history storage:

- chart completed quarter arrays
- comparison completed quarter arrays
- quarter rollover push logic

### Phase 3

Build reference lookup:

- active quarter -> target quarter classes
- latest completed quarter-of-class resolution

### Phase 4

Adapt signal evaluation:

- per comparison slot
- per target reference quarter class
- positive and inverse logic support

### Phase 5

Adapt drawing and history retention:

- flattened signal slots
- labels with reference quarter class
- historical retention

### Phase 6

Verify mapped symbol cases and quarter-class behavior

---

## Final Recommendation

Build `Doubling SMT` as a separate indicator that reuses the current `SSMT` comparison and display architecture, but replaces previous-quarter references with a quarter-class lookup engine.

### Final architecture

- keep the current `SSMT` script unchanged
- create a new `Doubling SMT` script for non-sequential quarter references
- keep auto correlation, inverse `DXY`, history, and UI consistent across both scripts

This is the cleanest approach for maintaining both tools without mixing two different quarter reference models into one file.
