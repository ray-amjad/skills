# [Project / change] Technical Specification

| Metadata | Value |
| --- | --- |
| Author | |
| Status | Draft |
| Created / updated | |
| Compatibility posture | |

## Executive summary

State the problem, selected solution, impact, and central doors in under 200 words.

## Context and verified current state

Describe current architecture and behavior with citations. Identify leaking doors, duplicated dangerous effects, and relevant constraints.

## Goals and non-goals

### Goals

### Non-goals

## Backwards compatibility

State the decided posture, compatibility-sensitive surfaces, and migration obligations.

## Proposed architecture

### Architecture view

### Components and responsibilities

### Door set — names alone

Mark doors guarding irreversible effects.

## Detailed design

### Door contracts

For each door: typed signature; one-sentence guarantee; named exits; refusals; capability; state/effects; idempotency/concurrency; enforcement; boundary tests.

### Transport contracts

### Data model, identity, source of truth, and lifecycle states

### Permissions — verb × actor

### Flows and algorithms

## Invariants and enforcement

| Invariant | Enforcement or detection point | Check (machine-runnable / human) | Evidence/test |
| --- | --- | --- | --- |

## Failure, retry, observability, and execution budget

Include each flow's trigger, named terminal states, and stopping rule.

## Migration and cutover

## Changes to existing behavior

| Surface | Before | After | Compatibility/operational effect |
| --- | --- | --- | --- |

## Alternatives considered

## Verification plan

Include exact commands or requests, boundary-visible expected results, and pass/fail conditions.

## Verified facts

| Fact | Scope/configuration | Evidence | Checked |
| --- | --- | --- | --- |

## Open Questions

Only questions the user was asked and explicitly deferred. Otherwise state: None.
