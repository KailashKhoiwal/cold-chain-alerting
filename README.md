# Cold-Chain Alerting Dashboard

A small Flask dashboard that detects sustained warm-temperature episodes in the supplied synthetic truck readings. The page lets you adjust the threshold and minimum duration and immediately recompute the alert list.

## Run locally

Requires Python 3.10 or newer.

```powershell
cd path\to\cold-chain-alerting
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>. The bundled dataset is loaded when the app starts. Dashboard controls use query parameters, so a selected rule can be bookmarked or shared locally.

## Detection behavior

- A reading violates the temperature limit only when it is strictly greater than the threshold (default **8°C**).
- An alertable episode lasts at least the configured elapsed duration (default **20 minutes**, measured from first to last violating reading).
- Readings are sorted independently per truck before grouping. A gap of up to 10 minutes is accepted; a longer gap ends the current episode.
- The result shows the truck, episode window, duration, peak temperature, number of readings, and qualification rule.
- Invalid threshold or duration values produce validation feedback and use the default for that field.

## Tests

```powershell
python -m unittest discover -s tests -v
```

The tests cover the bundled dataset, unsorted input, brief spikes, exact duration and threshold boundaries, gaps, and independent truck episodes.

## Limitations and next steps

This is a local batch demo over a fixed dataset. It recalculates each request and does not persist alert state, send notifications, deduplicate alerts across runs, or report episode recovery. Production use would need customer-approved cargo limits, timezone normalization, durable per-truck state, an ingestion source, authentication, monitoring, and operational notification/recovery behavior. Humidity is present in the dataset but is not used because no humidity rule was specified. No uploaded data or AI-generated summary is included.
