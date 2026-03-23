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

- show the panel on the `right side`
- rows should be `stacked vertically`, one above the other
- always show `3 rows`:
  - `ITF`
  - `HTF1`
  - `HTF2`
- each row must show `4 candles`
- timeframe selection should be `automatic` based on the current chart timeframe
- even on higher charts like `1D` and `1W`, still provide `2 HTFs`

This means the indicator is best treated as a `top-down context dashboard`, not a market-structure engine or entry-signal tool.

### Final v1 interpretation

To remove ambiguity, v1 should mean exactly this:

- the user trades on the current chart timeframe
- the script automatically chooses the next `3 higher-context rows`
- row 1 = `ITF`
- row 2 = `HTF1`
- row 3 = `HTF2`
- each row displays the `4 most recent confirmed candles`
- the newest candle should appear on the `right`
- the oldest candle should appear on the `left`

So the panel reads naturally from left to right as older to newer context.

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

Use a `table` instead of chart overlays.

### Why table is better than overlay candles

- overlaying multiple HTF candle blocks on an LTF chart becomes cluttered fast
- a table stays readable across all chart zoom levels
- a right-side table works well for top-down decision support
- Pine tables are better for dashboard-style information than labels or boxes

### Panel layout

Suggested structure:

- column 1: row label (`ITF`, `HTF1`, `HTF2`)
- column 2: actual timeframe label (`3m`, `1H`, `1D`, etc.)
- columns 3 to 6: last `4 candles`

### Refined table structure

Recommended final layout for v1:

- optional row 0: compact header such as `HTF Context`
- row 1: `ITF`
- row 2: `HTF1`
- row 3: `HTF2`

Recommended column meaning:

- col 0 -> context label
- col 1 -> timeframe label
- col 2 -> candle 1 oldest
- col 3 -> candle 2
- col 4 -> candle 3
- col 5 -> candle 4 newest

This gives a fixed `4 x 6` or `5 x 6` table depending on whether the header is enabled.

Each candle cell should visually communicate:

- bullish vs bearish
- relative wick/body shape in simplified form
- optional sweep/inside/outside state later

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

Because Pine tables cannot draw native candles directly, use a simplified visual encoding.

### Recommended v1 rendering

For each of the 4 candles in a row:

- use one table cell per candle
- display a compact glyph or text block representing candle shape
- use background color for direction:
  - bullish = green family
  - bearish = red family
  - neutral/doji = gray family
- optionally include OHLC relationship markers using symbols or multiline text

### Example visual options

Possible approaches:

1. `Text glyph candles`
   - use block characters or slim text layout
   - simple and low-cost

2. `Body + wick approximation`
   - encode wick/body balance using 3-line text within the cell
   - more informative but slightly harder to tune

3. `Color-first dashboard`
   - body direction only in v1
   - fastest and most stable initial version

### Recommendation

Start with `color-first + simple glyph` in v1.

That gives fast visual recognition without overcomplicating the first build.

### Refined candle-cell design

Each candle cell should encode these things in v1:

- background color = bullish / bearish / doji
- text glyph = rough wick/body position
- tooltip-style meaning through consistency, not too much text

Recommended simplified glyph set:

- strong bull close near high -> `up-close`
- strong bear close near low -> `down-close`
- balanced candle / doji -> `neutral`

In Pine table terms, this likely becomes a compact multiline text layout rather than a literal candlestick drawing.

### Best practical v1 compromise

If glyph rendering feels too fragile in TradingView across devices, fall back to this stable version:

- cell background = bull / bear / doji
- cell text = `B`, `S`, or `D`

That is less visual, but very reliable for the first release.

---

## Data Requirements Per Timeframe

For each displayed timeframe, fetch at least:

- `open`
- `high`
- `low`
- `close`

for the last `4 completed candles`, and optionally the current active candle if you later want live HTF updating.

### Recommended v1 behavior

Use the last `4 confirmed candles` for stability.

Why:

- avoids repaint confusion
- keeps the panel consistent during live bars
- matches the real need of seeing finished HTF context

Optional later enhancement:

- toggle between `confirmed only` and `include live current candle`

### Exact candle set for v1

To avoid repaint and interpretation issues, v1 should show:

- candle `4 bars ago`
- candle `3 bars ago`
- candle `2 bars ago`
- candle `1 bar ago`

from each requested higher timeframe.

This means v1 intentionally does `not` show the currently forming higher-timeframe candle.

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
- use tuples to request multiple fields together where possible
- update the table on `barstate.islast`

### Recommended request pattern

For each timeframe row, request all needed values in one call when possible:

- `open[4]`, `high[4]`, `low[4]`, `close[4]`
- `open[3]`, `high[3]`, `low[3]`, `close[3]`
- `open[2]`, `high[2]`, `low[2]`, `close[2]`
- `open[1]`, `high[1]`, `low[1]`, `close[1]`

using a tuple expression with `lookahead=barmerge.lookahead_on` only when paired with historical offsets for confirmed values.

This matches TradingView guidance for non-repainting higher-timeframe access.

---

## Performance Plan

This indicator will rely on several higher-timeframe requests, so performance should be planned from the start.

### Recommended safeguards

- request OHLC values in tuples to reduce unique `request.security()` calls
- avoid dynamic looping over arbitrary timeframe lists
- keep the timeframe ladder fixed
- update table cells only on the last bar
- use `var table` so the panel is created once and then updated

### Refined call budget

The clean v1 target should be:

- `3` higher timeframe rows
- `1` tuple request per row if Pine allows the full packed structure cleanly
- otherwise `4` series groups per row in a controlled pattern

The design should avoid unnecessary duplicate requests for the same timeframe.

### Why this matters

Pine has limits around unique `request.*()` calls. A fixed 3-row dashboard with tuple requests is well within a safe architecture if implemented carefully.

---

## Input Design

### Group: Display Settings

- `Show Header`
- `Panel Position`
- `Text Size`
- `Cell Width Mode`
- `Bull Candle Color`
- `Bear Candle Color`
- `Neutral Candle Color`
- `Header Background`
- `Border Color`

### Group: Behavior Settings

- `Use Confirmed HTF Candles Only` -> default `true`
- `Show Timeframe Labels` -> default `true`
- `Show Row Labels` -> default `true`
- `Use Strict Ladder Only` -> default `true`

### Recommended default values

- `Show Header` -> `true`
- `Panel Position` -> `Top Right`
- `Text Size` -> `Small`
- `Cell Width Mode` -> `Compact`
- `Use Confirmed HTF Candles Only` -> `true`
- `Show Timeframe Labels` -> `true`
- `Show Row Labels` -> `true`
- `Use Strict Ladder Only` -> `true`

### Optional future inputs

- `Include Current Live HTF Candle`
- `Show Sweep Marker`
- `Show Inside / Outside Marker`
- `Compact Mode`

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

### Step 2: Resolve the 3 display rows

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

### Step 4: Convert candles into display state

For each candle:

- determine bullish / bearish / doji
- determine simple body-to-range impression if used
- convert into color + text representation

### Refined candle classification rules

Use simple stable rules in v1:

- `bullish` when `close > open`
- `bearish` when `close < open`
- `doji` when `close == open` or body is below a small threshold of total range

Optional shape grading if added in v1:

- strong close near high
- strong close near low
- balanced / indecisive

### Step 5: Draw/update the table

- create the table once using `var table`
- update all visible cells on `barstate.islast`
- place the panel at the selected right-side position

### Refined draw rules

- only redraw contents when `barstate.islast`
- keep the table object persistent
- clear and repopulate cells deterministically each update
- avoid creating new tables repeatedly

---

## Edge Cases

The implementation should explicitly handle:

- unsupported chart timeframes
- symbols with limited history on higher timeframes
- missing data on `3M` or `12M`
- very small screens where table width becomes tight

### Recommendation for missing data

Show `na` or a placeholder cell instead of failing silently.

### Specific fallback display

Recommended missing-data text:

- timeframe cell still shows the target TF
- candle cells show `-`

This makes it obvious that the row exists but the symbol lacks enough history.

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

Build the base dashboard:

- timeframe auto mapping
- 3 rows
- 4 candles each
- bull/bear color display
- right-side table

### Phase 1a: Core reliability first

Before visual polish, validate these exact things:

- timeframe mapping works correctly for all supported chart timeframes
- `1D` resolves to `1W`, `1M`, `3M`
- `1W` resolves to `1M`, `3M`, `12M`
- panel stays stable during realtime updates
- unsupported chart timeframes fail gracefully

### Phase 2

Improve candle readability:

- better glyphs
- doji styling
- tighter spacing
- optional compact mode

### Phase 3

Add lightweight context markers:

- inside bar
- outside bar
- prior high sweep
- prior low sweep

### Phase 4

Add optional advanced context:

- live current HTF candle mode
- alerts later if useful
- optional structure labels

---

## Final Recommendation

This indicator should be built as a `clean right-side HTF context dashboard` with exactly:

- `ITF`
- `HTF1`
- `HTF2`
- `4 candles` per row
- `automatic timeframe mapping`

The best architecture is a Pine v6 table-based indicator using safe higher-timeframe requests and a fixed timeframe ladder that extends to `3M` and `12M` so the panel still works well on `1D` and `1W` charts.

---

## Next Implementation Target

When building the script, implement in this order:

1. Create timeframe mapping helpers
2. Resolve `ITF`, `HTF1`, `HTF2` from the current chart timeframe
3. Fetch last 4 confirmed candles for each row
4. Build a right-side `table`
5. Render candle state with color-first visualization
6. Add display inputs and fallback handling

---

## Locked Decisions For Build

These decisions are now recommended as fixed unless you want to change them before coding:

- use a `table`, not price-chart overlays
- show exactly `3 rows`: `ITF`, `HTF1`, `HTF2`
- show exactly `4 confirmed candles` per row
- newest candle is on the far right
- support `1m`, `3m`, `5m`, `15m`, `1H`, `4H`, `1D`, `1W` chart timeframes in v1
- map `1D` to `1W`, `1M`, `3M`
- map `1W` to `1M`, `3M`, `12M`
- do not include live unconfirmed HTF candle in v1
- do not add BOS, CHOCH, SMT, or alerts in v1
- if glyph candles are unstable visually, use `B / S / D` text with directional cell coloring as the fallback
