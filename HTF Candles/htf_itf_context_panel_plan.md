# HTF / ITF Context Panel Plan

## Goal

Build a Pine Script v6 indicator that helps low-timeframe execution by showing higher-timeframe candle context directly on the chart.

The indicator should display a compact right-side panel with stacked rows for:

- `ITF`
- `HTF1`
- `HTF2`

Each row should show the last `4 candles` of that higher timeframe so the trader can quickly judge directional context before taking entries on the current chart timeframe.

---

## Clarified Requirement

The final requirement is:

- show the candles on the `right side` in future bar space
- always show `3 timeframe groups`:
  - `ITF`
  - `HTF1`
  - `HTF2`
- each group must show `4 real candles`
- timeframe selection should be `automatic` based on the current chart timeframe
- even on higher charts like `1D` and `1W`, still provide `2 HTFs`

This means the indicator is best treated as a `right-side HTF candle overlay`, not a table dashboard or entry-signal tool.

### Final interpretation

To remove ambiguity, v1 should mean exactly this:

- the user trades on the current chart timeframe
- the script automatically chooses the next `3 higher-context groups`
- group 1 = `ITF`
- group 2 = `HTF1`
- group 3 = `HTF2`
- each group displays `4 candles`
- the newest candle should appear on the `right`
- the oldest candle should appear on the `left`
- all candles should be drawn with real `box` bodies and `line` wicks
- all candles should sit on actual chart price levels
- the groups should be separated mainly on the `x-axis`, not stacked in table rows

So the overlay reads naturally from left to right as older to newer context, with each timeframe group drawn to the right of the live chart.

---

## Recommended Timeframe Ladder

Use this fixed hierarchy:

- `1m`
- `3m`
- `5m`
- `15m`
- `1H`
- `4H`
- `1D`
- `1W`
- `1M`
- `3M`
- `12M`

### Auto mapping

- `1m` chart -> `ITF 3m`, `HTF1 5m`, `HTF2 15m`
- `3m` chart -> `ITF 5m`, `HTF1 15m`, `HTF2 1H`
- `5m` chart -> `ITF 15m`, `HTF1 1H`, `HTF2 4H`
- `15m` chart -> `ITF 1H`, `HTF1 4H`, `HTF2 1D`
- `1H` chart -> `ITF 4H`, `HTF1 1D`, `HTF2 1W`
- `4H` chart -> `ITF 1D`, `HTF1 1W`, `HTF2 1M`
- `1D` chart -> `ITF 1W`, `HTF1 1M`, `HTF2 3M`
- `1W` chart -> `ITF 1M`, `HTF1 3M`, `HTF2 12M`

### Why `3M` and `12M` are recommended

You specifically want `2 HTFs` even when the chart is already on `1D` or `1W`.

So:

- `1D` can still step up to `1W`, `1M`, `3M`
- `1W` can still step up to `1M`, `3M`, `12M`

This is the cleanest way to preserve a consistent 3-row panel.

---

## UI Recommendation

Use `chart overlays`, not a table.

### Why overlay candles are the correct UI

- the user explicitly wants `real candles`
- the candles should look like normal chart candles, not cell summaries
- each timeframe group should be placed in future bar space to the right of the current chart
- `box.new()` and `line.new()` match the desired visual behavior much better than `table.*`

### Overlay layout

Suggested structure:

- group 1: `ITF` candles
- group 2: `HTF1` candles
- group 3: `HTF2` candles
- each group contains `4 candles`
- each group has a label near the newest candle

### Refined visual structure

Recommended final layout for v1:

- current chart remains on the left
- future bar space on the right contains the 3 HTF groups
- `ITF` starts first
- `HTF1` starts after `ITF`
- `HTF2` starts after `HTF1`

Recommended x-axis behavior:

- oldest candle on the left within the group
- newest candle on the right within the group
- spacing between groups should be configurable
- candle width per group can be configurable

### Approximate UI sketch

```text
current chart candles ...                    future space on right

                                        ITF              HTF1               HTF2
                                      |█| | |          |█| |█|           | | |█|
                                      | | |█|          | | | |           |█| | |
                                      label            label             label
```

Important note:

- these are not separate vertical rows anymore
- they are `3 side-by-side HTF candle groups`
- they use actual price values, so they can overlap vertically if price ranges are similar

---

## v1 Feature Scope

### Include in v1

- Pine Script v6 indicator
- `overlay=true`
- right-side table panel
- stacked rows for `ITF`, `HTF1`, `HTF2`
- auto timeframe mapping
- last `4 candles` per row
- bullish/bearish candle coloring
- optional header row
- optional panel position input
- optional size input

### Do not include in v1

- alerts
- BOS / CHOCH logic
- swing structure engine
- premium / discount engine
- SMT / divergence logic
- entry signals
- too many per-candle annotations

The first version should focus only on making higher-timeframe context visible and usable.

---

## Candle Rendering Approach

Use real drawing objects.

### Recommended rendering

For each of the 4 candles in a group:

- draw the body with `box.new()`
- draw upper and lower wicks with `line.new()`
- use actual OHLC values so candles sit on real price levels
- draw a label near the newest candle in each group
- optionally draw the prior candle `50%` level

### Current style direction

- one shared style for all 3 groups
- user can control:
  - bullish color
  - bearish color
  - wick color
  - border color
  - label text color
- user can optionally keep different candle widths per group

### Recommendation

Keep the rendering literal and simple:

- real candle body
- real wick
- no glyph fallback in the main version
- one label per group near the newest candle

---

## Data Requirements Per Timeframe

For each displayed timeframe, fetch at least:

- `open`
- `high`
- `low`
- `close`

for the last `4 candles`, with support for a live current HTF candle mode.

### Recommended behavior modes

The indicator should support 3 modes conceptually:

1. `Confirmed Only`
   - show 4 closed HTF candles
   - most stable

2. `Hybrid Live` (recommended)
   - first 3 candles confirmed
   - newest 4th candle is the current live forming HTF candle
   - best balance for execution

3. `Fully Live`
   - active candle data updates as the current HTF bar changes
   - useful, but naturally not final until the HTF candle closes

### Recommended default going forward

Use `Hybrid Live` as the recommended live mode.

Why:

- older context stays stable
- newest candle reflects current live HTF behavior
- gives useful intrabar awareness without turning all 4 candles into moving targets

### Exact candle set by mode

Confirmed only:

- candle `4 bars ago`
- candle `3 bars ago`
- candle `2 bars ago`
- candle `1 bar ago`

Hybrid live:

- candle `3 bars ago`
- candle `2 bars ago`
- candle `1 bar ago`
- current live candle

Fully live:

- the newest candle updates live
- earlier candles remain historical in practice, but the focus is the active candle behavior

---

## Live Updating And Accuracy

### What is possible

Live HTF candles are possible in Pine.

This means:

- the newest HTF candle can update as price moves
- the wick and body can expand or contract while that HTF candle is still forming
- updates occur when TradingView receives chart updates/ticks

### What is not possible

- the active HTF candle cannot be considered final until the HTF bar closes
- Pine does not run a separate independent update loop outside TradingView's normal chart update model

### Accurate interpretation

- `confirmed` candles are final
- `live` candles are accurate to the current moment, but still unfinished
- this is expected behavior, not an error

---

## Non-Repainting Plan

Use safe higher-timeframe requests.

### Recommended pattern

Use `request.security()` with confirmed offsets where appropriate, such as requesting prior confirmed HTF values instead of relying on unconfirmed current HTF values.

Relevant Pine guidance:

- avoid plain `lookahead_on` without offset
- prefer stable HTF reads for dashboard context
- keep the output consistent between historical and realtime bars

### Practical implementation direction

- fetch HTF candle series with safe `request.security()` usage
- use fixed offsets for confirmed candles
- use `lookahead=barmerge.lookahead_off` for the live current candle
- update drawing objects on `barstate.islast`

### Recommended request pattern

For each timeframe group, request the needed OHLC values explicitly.

Confirmed only mode:

- request confirmed candles with historical offsets

Hybrid live mode:

- first 3 candles use confirmed offsets
- 4th candle uses live `open/high/low/close`

This keeps the older candles stable while allowing the newest candle to update.

### Recommended default logic

- confirmed candles: safe historical offsets
- live current candle: `request.security(..., lookahead=barmerge.lookahead_off)`
- label countdown can use `time_close`

---

## Performance Plan

This indicator will rely on several higher-timeframe requests, so performance should be planned from the start.

### Recommended safeguards

- avoid dynamic looping over arbitrary timeframe lists
- keep the timeframe ladder fixed
- update overlay objects only on the last bar
- keep object arrays for cleanup
- reuse a small fixed drawing footprint: `3 groups x 4 candles`

### Refined call budget

The clean target should be:

- `3` higher timeframe groups
- `4` candles per group
- wick + body objects for each candle
- one label per group
- optional one midpoint line per historical transition

The design should avoid unnecessary duplicate requests for the same timeframe.

### Why this matters

Pine has limits around unique `request.*()` calls and object counts. A fixed `3-group, 4-candle` overlay is reasonable if kept disciplined.

---

## Input Design

### Group: General

- `Right Offset Bars`
- `Spacing Between Groups`
- `Show Labels`
- `Show Time Remaining`
- `Show Prior Candle 50%`
- `Use Confirmed HTF Candles Only`
- later: `Live Mode = Confirmed / Hybrid / Live`

### Group: Style

- `Bull Candle Color`
- `Bear Candle Color`
- `Wick Color`
- `Border Color`
- `Label Text Color`
- `ITF Candle Width`
- `HTF1 Candle Width`
- `HTF2 Candle Width`

### Recommended default values

- `Right Offset Bars` -> `4`
- `Spacing Between Groups` -> moderate default
- `Show Labels` -> `true`
- `Show Time Remaining` -> `true`
- `Show Prior Candle 50%` -> optional
- `Use Confirmed HTF Candles Only` -> `false` once hybrid mode is added cleanly
- `Use Strict Ladder Only` -> `true`

### Optional future inputs

- `Live Mode`
- `Group Background Boxes`
- `Show Previous Candle High/Low`
- `Show Sweep Marker`

---

## Logic Plan

### Step 1: Detect current chart timeframe

Map the active chart timeframe into the supported ladder.

If the user is on an unsupported timeframe, choose one of these behaviors:

- nearest supported timeframe mapping, or
- show a message that the panel is designed for the core ladder only

### Recommendation

For v1, support only the core ladder cleanly and show a friendly message for unsupported chart timeframes.

### Supported chart timeframes in v1

Support these chart periods explicitly:

- `1`
- `3`
- `5`
- `15`
- `60`
- `240`
- `1D`
- `1W`

These correspond to:

- `1m`
- `3m`
- `5m`
- `15m`
- `1H`
- `4H`
- `1D`
- `1W`

### Unsupported chart timeframe behavior

If the chart timeframe is outside the supported ladder:

- do not guess by rounding silently in v1
- show a small message in the panel such as `Use 1m, 3m, 5m, 15m, 1H, 4H, 1D, or 1W`

This is better than hidden remapping because it keeps the tool predictable.

### Step 2: Resolve the 3 display groups

For the current chart timeframe, determine:

- `itfTf`
- `htf1Tf`
- `htf2Tf`

### Step 3: Request candle data

For each resolved timeframe, fetch the last 4 candles of:

- open
- high
- low
- close

and optionally:

- `time`
- `time_close`

### Step 4: Build candle groups

For each timeframe group:

- determine the x positions for the 4 candles
- draw the candle bodies using `box.new()`
- draw upper/lower wicks using `line.new()`
- draw optional previous-candle midpoint lines
- attach one label near the newest candle

### Step 5: Live update logic

In hybrid live mode:

- candles 1 to 3 are confirmed
- candle 4 is the active live candle
- redraw the objects on each chart update while the bar is active

### Step 6: Cleanup and redraw rules

- clear prior objects on `barstate.islast`
- recreate the small fixed set of objects deterministically
- keep the object count bounded

This is simpler and more reliable than trying to manage many persistent per-candle mutations in the first version.

---

## Edge Cases

The implementation should explicitly handle:

- unsupported chart timeframes
- symbols with limited history on higher timeframes
- missing data on `3M` or `12M`
- very small screens where future bar space is too narrow
- live candle overlaps with current chart if right offset is too small

### Recommendation for missing data

Skip missing candles and still keep the label visible.

### Specific fallback display

Recommended fallback:

- keep the group label
- do not draw invalid candles

This makes it obvious that the timeframe exists but the symbol lacks enough HTF history.

---

## Suggested File Strategy

Create a new standalone file such as:

- `htf_itf_context_panel.pine`

### Why separate is best

- this tool solves a different problem than the existing quarterly indicators
- it is a dashboard, not a cycle box or SSMT engine
- keeping it separate improves maintenance and iteration speed

---

## Build Phases

### Phase 1

Build the base overlay:

- timeframe auto mapping
- 3 groups
- 4 candles each
- real candles with body + wick
- right-side future-bar placement

### Phase 1a: Core reliability first

Before visual polish, validate these exact things:

- timeframe mapping works correctly for all supported chart timeframes
- `1D` resolves to `1W`, `1M`, `3M`
- `1W` resolves to `1M`, `3M`, `12M`
- overlay stays stable during realtime updates
- unsupported chart timeframes fail gracefully

### Phase 2

Add live behavior improvements:

- hybrid live mode
- time-remaining labels
- better spacing defaults
- style cleanup

### Phase 3

Add lightweight context markers:

- inside bar
- outside bar
- prior high sweep
- prior low sweep

### Phase 4

Add optional advanced context:

- full live mode toggle
- alerts later if useful
- optional structure labels

---

## Final Recommendation

This indicator should be built as a `clean right-side HTF candle overlay` with exactly:

- `ITF`
- `HTF1`
- `HTF2`
- `4 candles` per group
- `automatic timeframe mapping`

The best architecture is a Pine v6 overlay indicator using `box.new()` and `line.new()` with safe higher-timeframe requests and a fixed timeframe ladder that extends to `3M` and `12M` so the overlay still works on `1D` and `1W` charts.

---

## Next Implementation Target

When building the script, implement in this order:

1. Create timeframe mapping helpers
2. Resolve `ITF`, `HTF1`, `HTF2` from the current chart timeframe
3. Fetch candle data for `Confirmed`, `Hybrid`, and `Live` behavior
4. Draw right-side candle groups using `box.new()` and `line.new()`
5. Add labels, midpoint lines, and spacing controls
6. Add fallback handling for unsupported timeframes and missing HTF history

---

## Locked Decisions For Build

These decisions are now recommended as fixed unless you want to change them before coding:

- use `price-chart overlays`, not a table
- show exactly `3 groups`: `ITF`, `HTF1`, `HTF2`
- show exactly `4 candles` per group
- newest candle is on the far right
- support `1m`, `3m`, `5m`, `15m`, `1H`, `4H`, `1D`, `1W` chart timeframes in v1
- map `1D` to `1W`, `1M`, `3M`
- map `1W` to `1M`, `3M`, `12M`
- draw candles with `box.new()` bodies and `line.new()` wicks
- place groups in future bar space to the right of the chart
- recommended live behavior is `3 confirmed + 1 live current candle`
- do not add BOS, CHOCH, SMT, or alerts in v1
- use one shared style block for colors unless separate styling is needed later
