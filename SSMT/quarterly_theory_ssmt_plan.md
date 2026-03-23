# Quarterly Theory SSMT Indicator Plan

## Goal

Build a separate Pine Script indicator that detects and draws quarter-to-quarter Sequential SMT (SSMT) divergence lines using the same quarterly cycle engine concept as `quarterly_theory_boxes.pine`, but focused on intermarket comparison instead of quarter boxes.

This indicator should work first for index relationships like:

- `NQ` vs `ES`
- `NQ` vs `YM`
- and show both at the same time when both divergences exist

It should also be designed so we can later extend it to forex pairs and other correlated markets.

---

## Recommended File Strategy

Create a new file:

- `quarterly_theory_ssmt.pine`

Do not merge this into `quarterly_theory_boxes.pine`.

### Why separate is better

- `quarterly_theory_boxes.pine` is a time-structure visualization tool.
- SSMT is an intermarket divergence engine using comparison symbols and `request.security()`.
- Keeping them separate makes each script easier to debug, maintain, and extend.
- You can run both indicators on the same chart without turning one script into a very large mixed-purpose system.
- Forex expansion later becomes much cleaner.

---

## Core Concept

The SSMT script should evaluate quarter extremes in the chart symbol and compare them against selected correlated symbols.

### Bearish SSMT

Bearish SSMT occurs when:

1. The chart symbol takes the previous quarter high in the current quarter.
2. A comparison symbol does **not** take its previous quarter high in the same quarter.
3. A line is drawn on the chart symbol from the previous quarter high point to the current quarter sweep high point.

Example:

- Chart: `NQ`
- Prior quarter high in `NQ` is taken in the next quarter
- `ES` does not take its own prior quarter high
- Draw bearish SSMT line on `NQ`, labeled `vs ES`

### Bullish SSMT

Bullish SSMT occurs when:

1. The chart symbol takes the previous quarter low in the current quarter.
2. A comparison symbol does **not** take its previous quarter low in the same quarter.
3. A line is drawn on the chart symbol from the previous quarter low point to the current quarter sweep low point.

---

## v1 Feature Scope

### Include in v1

- Same cycle choices as the box indicator:
  - `Auto`
  - `22.5m`
  - `90m`
  - `6H`
  - `1D`
  - `1W`
  - `1M`
- NY-anchored cycle logic
- Quarter-to-next-quarter comparison only
- Detect both bullish and bearish SSMT
- Support multiple comparison symbols at the same time
- Historical SSMT retention toggle
- Labels showing which comparison symbol failed confirmation

### Do not include in v1

- Multi-quarter pattern chaining
- SMT grading/scoring
- Forex session-specific overrides
- Panel/table analytics
- alerts

---

## Input Design

### Group: Cycle Settings

- `Cycle` -> `Auto`, `22.5m`, `90m`, `6H`, `1D`, `1W`, `1M`

### Group: Comparison Symbols

- `Compare With ES` -> checkbox
- `Compare With YM` -> checkbox
- `Custom Symbol 1` -> symbol input
- `Enable Custom Symbol 1` -> checkbox
- `Custom Symbol 2` -> symbol input
- `Enable Custom Symbol 2` -> checkbox

### Why not a single dropdown

- You want `NQ vs ES` and `NQ vs YM` simultaneously.
- A single dropdown only supports one selection at a time.
- Checkboxes plus optional custom symbol fields are more flexible and future-proof.

### Group: Signal Settings

- `Show Bearish SSMT`
- `Show Bullish SSMT`
- `Only Confirm At Quarter Close` -> recommended default `false` for live structure, optional `true` for stricter confirmation
- `Max Signals Per Comparison` -> optional future input, not required in first pass

### Group: Historical Settings

- `Show Historical SSMT`
- `Historical SSMT To Keep`

### Group: Display Settings

- `Show Labels`
- `Show Symbol In Label`
- `Show Cycle Tag`
- `Bearish Line Color`
- `Bullish Line Color`
- `Line Width`
- `Line Style`

---

## Data Model

For the chart symbol and each comparison symbol, track:

- previous quarter high
- previous quarter low
- previous quarter high bar/time
- previous quarter low bar/time
- current quarter high
- current quarter low
- current quarter high bar/time
- current quarter low bar/time

### Important note

For comparison symbols, we do not need to draw on their charts. We only need their quarter extreme values and whether they did or did not sweep their previous quarter extreme.

---

## Detection Logic

### Step 1: Determine active cycle

Reuse the same NY-anchored cycle logic pattern from `quarterly_theory_boxes.pine`.

The active cycle defines quarter boundaries.

### Step 2: Track quarter extremes

For each bar:

- determine current quarter index
- maintain current quarter high/low for chart symbol
- maintain current quarter high/low for each comparison symbol

At quarter rollover:

- move current quarter values into previous quarter storage
- reset current quarter tracking for the new quarter

### Step 3: Detect bearish SSMT

On each bar inside the current quarter:

- if chart current quarter high > chart previous quarter high
- and comparison current quarter high <= comparison previous quarter high
- then bearish SSMT exists for that comparison symbol

### Step 4: Detect bullish SSMT

On each bar inside the current quarter:

- if chart current quarter low < chart previous quarter low
- and comparison current quarter low >= comparison previous quarter low
- then bullish SSMT exists for that comparison symbol

### Step 5: Draw the line

Bearish line:

- x1 = bar/time of chart previous quarter high
- y1 = chart previous quarter high price
- x2 = bar/time of current quarter sweep high
- y2 = current quarter sweep high price

Bullish line:

- x1 = bar/time of chart previous quarter low
- y1 = chart previous quarter low price
- x2 = bar/time of current quarter sweep low
- y2 = current quarter sweep low price

### Step 6: Label the line

Label examples:

- `Bearish SSMT vs ES`
- `Bearish SSMT vs YM`
- `Bullish SSMT vs ES`

If both `ES` and `YM` fail confirmation, both lines should be drawn.

---

## Historical Mode Behavior

### When off

- Show only active/current SSMT lines and labels.
- Replace or update them as price evolves.

### When on

- Preserve finished SSMT lines and labels from prior quarters/cycles.
- Keep only the latest `N` retained signals.
- Delete oldest retained signals when the limit is exceeded.

### Recommended retention model

Use arrays of:

- `line`
- `label`
- signal metadata if needed later

---

## request.security Strategy

For comparison symbols:

- use `request.security()` to fetch `high`, `low`, and time-aligned quarter data
- avoid future leakage
- prefer confirmed logic when reading quarter transitions

### Important caution

Do not build this using arbitrary bar counts.

Use the same cycle timestamps and quarter rollover logic so all symbols are evaluated against the same NY quarterly structure.

---

## How ES and YM Should Work Together

For `NQ` chart:

- if `Compare With ES` is enabled, run one comparison engine for `ES`
- if `Compare With YM` is enabled, run another comparison engine for `YM`

These engines should be independent.

That means:

- only `ES` divergence -> show only `vs ES`
- only `YM` divergence -> show only `vs YM`
- both diverge -> show both lines and both labels

This also scales naturally to forex later.

---

## Forex Expansion Plan

When you later move into forex, keep the same engine and only change the comparison set.

Possible examples:

- `EURUSD` vs `GBPUSD`
- `GBPUSD` vs `EURUSD`
- `DXY` vs `EURUSD`
- `XAUUSD` vs `DXY`

Because the script is built around generic comparison-symbol slots, you will not need to redesign the core logic.

---

## Recommended Build Order

### Phase 1

Build the base file:

- `quarterly_theory_ssmt.pine`
- same cycle engine as box script
- chart symbol + one comparison symbol
- bearish and bullish SSMT line detection
- line + label drawing

### Phase 2

Extend to multiple comparison symbols:

- ES checkbox
- YM checkbox
- optional custom symbol inputs
- separate line/label output for each comparison

### Phase 3

Add historical SSMT mode:

- retain old lines and labels
- cap retained count

### Phase 4

Add polish:

- label styling
- signal filtering options
- optional close-confirmed mode
- optional alerts later

---

## Recommended Naming

Suggested title:

- `Quarterly Theory SSMT | Auto NY Cycles`

Suggested internal feature naming:

- `Sequential SMT`
- `SSMT`
- `Quarter-to-Quarter SMT`

Use `SSMT` in the UI because that matches the concept you described most closely.

---

## Final Recommendation

Build SSMT as a separate indicator.

### Final architecture

- Keep `quarterly_theory_boxes.pine` for quarter structure, boxes, and true opens
- Build `quarterly_theory_ssmt.pine` for intermarket divergence lines

This is the cleanest setup for:

- NQ / ES / YM now
- forex pairs later
- better maintainability
- less performance risk

---

## Next Build Task

When ready, implement `quarterly_theory_ssmt.pine` with this exact order:

1. Copy/adapt the NY cycle engine from `quarterly_theory_boxes.pine`
2. Track previous/current quarter highs and lows for chart symbol
3. Add one comparison engine using `request.security()`
4. Draw bullish and bearish SSMT lines and labels
5. Extend to ES + YM together
6. Add historical SSMT retention
