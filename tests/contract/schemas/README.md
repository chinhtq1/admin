# Contract schemas

One file per message schema, named after its `schema` field: `ems.telemetry.v1.json`, `ems.event.v1.json`,
`ems.cmd-ack.v1.json`, `ems.state.v1.json`, `ems.command.v1.json`. Draft-07 (`"$schema": "http://json-schema.org/draft-07/schema#"`)
because the 07 §7.3 gauge schema is invalid under Draft 2020-12 (A3 §3.3). Each file states its source section
(07 §x.y) and whether it is normative (07) or "PoC shape" (07 has only examples, A2 Q6).
