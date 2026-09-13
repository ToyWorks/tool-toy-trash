# Tool, Toy, or Trash?

Every AI gadget is some mix of three things:

| | Earns its place by | You know it when |
| --- | --- | --- |
| 🟢 **Tool** | removing a step from someone's day | it breaks and the workflow breaks with it |
| 🟡 **Toy** | delight: materials, surprise, room to explore and mod | people keep it on the desk with nothing to do |
| 🔴 **Trash** | nothing: it adds friction, leaks privacy, or duplicates a free phone app | it is in a drawer within a month |

That question is worth asking *before* building hardware, not after.
**T3** turns it into an audit an AI agent can run on any product page, as the
`t3-hardware-scoring` agent skill.

## Try it

```bash
npx skills add toyworks/tool-toy-trash
```

or, in Claude Code:

```bash
/plugin marketplace add ToyWorks/tool-toy-trash
/plugin install t3-hardware-scoring@tool-toy-trash
```

Then hand your agent a product link:

> Run a T3 audit on https://example.com/some-ai-pendant

Any agent that supports the [Agent Skills standard](https://agentskills.io) can load it.

## How it scores

```text
product page + reviews
  └─ brand-blind          strip names, so the hype can't vote
      ├─ tool auditor  ┐
      ├─ toy auditor   ├─ fixed rubrics, verbatim evidence only, run in parallel
      └─ trash auditor ┘
          └─ eagle eye    re-check the fatal flags: "on-device" claims that can't be, apps it duplicates
              └─ judge    normalize, apply the gates and the veto → label
```

- **Evidence first.** No score above 0 without a quote from the source text, and
  a test checks that every quote really is in it.
- **Math in code.** Normalization, the Gray Zone and the veto live in
  [`synthesize_results.py`](skills/t3-hardware-scoring/scripts/synthesize_results.py),
  not in the model's head.
- **One veto.** A single Eagle Eye flag (privacy tension, a core flaw, app
  redundancy) forces Trash into the label, however good the rest looks.

A run on the fictional AI pendant in the test fixtures (the "second memory" that
promises nothing leaves the device, plus a $19/month plan):

```text
tool  33.3   toy  27.3   trash  71.4   composite  -38.1
→ Trash (Eagle Eye)   confidence: Review Required
```

## What's inside

```text
skills/t3-hardware-scoring/
├── SKILL.md       the procedure the agent follows, step by step
├── references/    auditor rubrics, brand blinding, Eagle Eye, the judge's rules
├── scripts/       validate + merge the auditor reports, synthesize the verdict
└── tests/         unit tests, a golden worked audit, link and consistency checks
```

The rules in full: [`t3-classification.md`](skills/t3-hardware-scoring/references/t3-classification.md).

## Hack on it

```bash
skills/t3-hardware-scoring/tests/run_tests.sh
```

Stdlib Python only, no install step. CI runs the suite and a link check on every
push and pull request.

Change a rule and its test in the same commit; each test names the spec section
it pins. Pull requests are welcome, especially new Eagle Eye red flags: add them
to [`trash-red-flags.md`](skills/t3-hardware-scoring/references/trash-red-flags.md)
first, and the trigger-consistency test will tell you where else they go.

## License

MIT
