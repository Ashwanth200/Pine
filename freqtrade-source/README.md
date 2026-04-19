# Freqtrade Local Source Workspace

This folder contains a native local setup for both the Freqtrade backend and the FreqUI frontend.

These were downloaded as source archives instead of cloned, so they do not carry upstream git history. This keeps both codebases as normal folders inside your own repository, which is useful if you want to customize the UI and backend later.

## Structure

- `backend/`: Freqtrade bot backend source
- `frontend/`: FreqUI frontend source

## Source Snapshot Used

- Backend: `freqtrade/freqtrade` `stable` branch snapshot
- Frontend: `freqtrade/frequi` `main` branch snapshot

## Local Setup Status

Completed:

- Native Python virtualenv created in `backend/.venv`
- Backend installed in editable mode
- TA-Lib installed on the machine with Homebrew
- Frontend dependencies installed with `pnpm`
- Local Binance spot dry-run config added
- Local EMA crossover strategy added
- Backend data download verified
- Backend backtest verified
- Frontend production build verified
- Frontend browser login verified against the local backend API

## Current Local Bot Setup

- Exchange: `binance`
- Market: `spot`
- Mode: `dry_run`
- Pairs: `BTC/USDT`, `ETH/USDT`
- Timeframe: `15m`
- Strategy: `EmaCrossStrategy`
- Stake amount: `50 USDT`
- Dry-run wallet: `1000 USDT`

## URLs

- Frontend UI: `http://127.0.0.1:3000`
- Backend API: `http://127.0.0.1:8080`
- API ping: `http://127.0.0.1:8080/api/v1/ping`
- OpenAPI docs: `http://127.0.0.1:8080/docs`

## Login Credentials

- Username: `ftuser`
- Password: `3d3103bc61dddb23aa984beb8be1a5f8`

## Important Files

- `backend/user_data/config.json`: local bot config
- `backend/user_data/strategies/EmaCrossStrategy.py`: starter strategy
- `frontend/src/components/BotLogin.vue`: UI login dialog default API URL adjusted to `:8080`

## Running The Local Setup

Start the backend:

```bash
cd "/Users/ashwanth/Documents/Pine/freqtrade-source/backend"
./.venv/bin/freqtrade trade --config user_data/config.json --strategy EmaCrossStrategy
```

Start the frontend:

```bash
cd "/Users/ashwanth/Documents/Pine/freqtrade-source/frontend"
pnpm run dev
```

Then open:

```text
http://127.0.0.1:3000
```

## One-Time Validation Commands

Backend config validation:

```bash
cd "/Users/ashwanth/Documents/Pine/freqtrade-source/backend"
./.venv/bin/freqtrade show-config --config user_data/config.json
```

Download data:

```bash
./.venv/bin/freqtrade download-data --config user_data/config.json --exchange binance --pairs BTC/USDT ETH/USDT --timeframes 15m --days 365
```

Backtest:

```bash
./.venv/bin/freqtrade backtesting --config user_data/config.json --strategy EmaCrossStrategy
```

Frontend build:

```bash
cd "/Users/ashwanth/Documents/Pine/freqtrade-source/frontend"
pnpm run build
```

## Verified Results

Backend:

- API ping returns `{"status":"pong"}`
- Local bot starts successfully on `127.0.0.1:8080`
- Dry-run mode starts successfully

Frontend:

- Dev server starts successfully on `127.0.0.1:3000`
- Production build succeeds
- Browser login to the backend works
- Dashboard data loads after selecting the bot

Backtest result for the starter strategy:

- Total profit: `-3.53%`
- Final balance: `964.696 USDT`
- Trades: `695`
- Win rate: `45.9%`
- Profit factor: `0.79`
- Max drawdown: `4.50%`

This means the setup is working, but the starter strategy is only a baseline and is not ready for live trading.

## Notes

- The frontend and backend are intentionally separate in this workspace.
- Future UI redesign work will mostly happen in `frontend/`.
- Future bot/config/strategy changes will mostly happen in `backend/`.
