# Solution Design: Cold-Chain Alerting Engine

## Problem

Nimbus Freight needs an operations view that surfaces sustained warm conditions for individual refrigerated trucks without treating every brief sensor excursion as an alert. The demo reads the provided sample data, groups readings into per-truck episodes, and shows only episodes meeting a duration rule.

## Assumptions

- Use **8°C** as the initial upper limit and **20 minutes** as the minimum sustained duration. These are demo defaults from the starter utility, not validated pharmaceutical or grocery limits; production values must come from cargo and customer requirements.
- A reading exactly at the threshold is not a violation. Episode duration is elapsed wall-clock time between the first and last violating readings.
- Sort timestamps per truck. Allow a missed 5-minute sample; a gap greater than 10 minutes breaks continuity because the system should not claim sustained exposure when it has no observations.
- Treat timestamps as comparable local times. The seed timestamps contain no timezone information.
- Humidity does not influence alerting because the brief provides no corresponding safe range.

## Approach and trade-offs

The implementation separates a pure Python detection module from a Flask presentation layer. The app loads the bundled JSON at startup and renders a server-side dashboard. Users can change the threshold and duration, then rerun the detector through a standard form submission. This keeps the take-home easy to run and inspect without introducing a database, streaming infrastructure, or external service.

Each truck is sorted independently. A non-violating reading or a gap over 10 minutes closes an episode. Qualifying episodes are ordered by start time and displayed with their time window, elapsed duration, peak temperature, reading count, and the applied rule. The UI includes validation messages and a no-alert state.

The app computes results afresh for each request. This is intentionally simpler than the customer’s eventual streaming workflow, but it does not maintain alert identity or prevent the same open incident from notifying repeatedly across runs. A live implementation should store episode state and emit an initial notification once, then apply a clear recovery policy.

## Future work

Before production, confirm thresholds by cargo and customer, normalize timestamps and late-arriving readings, define the behavior for duplicate readings and sensor outages, and add durable state, notification delivery, recovery alerts, access control, and monitoring. Evaluate rules against labeled historical incidents to tune sensitivity and alert volume. Uploads and generated natural-language summaries are outside this v1.
