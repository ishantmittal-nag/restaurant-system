---
name: pr-review-bench
description: Test a PR-reviewing agent by shipping Claude-authored feature branches with deliberately planted bugs, keeping a private pre-push self-review as an answer key, and later scoring the reviewer agent's actual GitHub comments against it. Two modes - "prepare" (build + seed + push + open PR) and "evaluate" (fetch review + score). Use for "start the next bug-lab PR", "seed a buggy PR", "evaluate PR #N", "score the reviewer agent", or anything about the PR bug lab / review bench.
---

# PR Review Bench

A repeatable loop for stress-testing a PR-reviewing agent against this repo:

1. **prepare** - implement a real feature on a branch, deliberately plant a
   realistic mixed bag of bugs, write a private self-review (the answer key)
   *before* pushing, then push and open the PR for real.
2. (external) the user's reviewer agent reviews the PR on GitHub, on its own time.
3. **evaluate** - fetch what the reviewer agent actually said, and score it
   against the answer key: what it caught, what it missed, what it got wrong,
   any false positives.

State lives in `.claude/pr-bug-lab/` (gitignored - never committed, never part
of a PR diff, so it can't leak into what the reviewer agent sees):

```
.claude/pr-bug-lab/
  backlog.md              queue of feature ideas + status per PR
  answer-keys/<branch>.md  planted/accidental issues for that PR, written pre-push
  evaluations/<branch>.md  scorecard vs. the reviewer agent's actual comments
```

If `.claude/pr-bug-lab/` doesn't exist yet, create it (and confirm
`.claude/pr-bug-lab/` is in `.gitignore`) before doing anything else.

`gh` must be authenticated (`gh auth status`). If not, stop and tell the user -
OAuth can't be completed from a non-interactive session.

## Hard constraints (every prepare run)

- Diff target: **~1500-2000 lines changed**, net, against `main`.
- **≤ 20 files changed.**
- Check both with `git diff main...HEAD --stat` before committing. If over
  budget, cut scope (trim the feature, not the bug density) rather than
  blow past the limit - it's fine for a backlog item to take two PRs.
- Commit messages and the PR title/body must read like a completely normal,
  real PR. Never hint at seeded bugs in anything that gets pushed.

## Mode: prepare

1. **Pick the feature.** Read `.claude/pr-bug-lab/backlog.md`. If it doesn't
   exist, create it with a starter queue (reservations, order
   discounts/coupons, staff API-key auth, table split/merge + billing,
   per-item kitchen ticket status, customer accounts/loyalty points,
   inventory/stock deduction on order completion) each marked `pending`. Take
   the next `pending` item unless the user named a specific one. Mark it
   `in-progress` with the branch name.

2. **Branch.** `git checkout -b feature/<slug>` off an up-to-date `main`.

3. **Build it for real.** Implement the feature like a genuine increment to
   this codebase - follow the existing patterns in `app/` (routers/schemas/
   models/crud split), add tests, keep it plausible. This is not throwaway
   junk; a human reviewer should be able to mistake it for real work.

4. **Plant issues while building, not as an afterthought.** Pick 6-10 issues
   per PR, spread across categories and severities so recall/precision are
   meaningful (roughly 1-2 critical/high, a few medium, a few low/style).
   Rotate categories PR to PR rather than repeating the same trick. Draw from:

   - **Security** - missing authz/authn on an endpoint that should have it,
     mass assignment (accepting/trusting client-supplied fields it shouldn't),
     missing input validation/bounds checks, overly permissive CORS, logging
     sensitive data, a hardcoded "secret" (use an obviously dummy value like
     `"dev-only-placeholder-key-do-not-use"` - never anything that could look
     like a real credential).
   - **Correctness/logic** - off-by-one, wrong comparator, invalid state-machine
     transitions (e.g. `completed` -> `pending` allowed), read-modify-write
     race (no transaction/lock where one matters), mutable default argument,
     money as `float` instead of `Decimal`, wrong HTTP status code, unhandled
     `None`/empty case, bare `except:` / `except Exception: pass` that
     swallows a real failure, missing `db.rollback()` on error leaving the
     session dirty, copy-paste function where one parameter didn't get
     updated.
   - **Performance** - N+1 query in a list endpoint, unbounded/unclamped
     user-supplied `limit`, loading a full table into memory to filter in
     Python, redundant recomputation inside a loop.
   - **Maintainability/tests** - dead code, duplicated logic that should be
     shared, magic numbers, a new test that doesn't actually assert anything
     meaningful, missing coverage for the new branch/edge case.

   Nothing planted should be *actually* dangerous to run locally - no real
   secrets, no real destructive commands, no real outbound network calls, no
   infinite loops. The bug is the pattern, not a live payload.

5. **Self-review before committing anything.** Reread the full diff like a
   real reviewer would (file by file, reasoning about failure scenarios, not
   just listing what you planted - note any *accidental* real bugs you spot
   too). Write `.claude/pr-bug-lab/answer-keys/<branch>.md`:

   ```markdown
   # Answer key: <branch> (<feature>)

   PR: <filled in after `gh pr create`>

   | # | Location (file:line) | Category | Severity | Summary | Failure scenario | Planted or accidental |
   |---|---|---|---|---|---|---|
   ```

   Severity: critical / high / medium / low. Category: security / correctness
   / performance / maintainability / test-coverage. Do this *before* `git add`
   so it's never at risk of being staged by accident.

6. **Commit, push, open the PR.**
   ```
   git add <feature files only>          # never the .claude/pr-bug-lab/ files
   git commit -m "<normal-sounding message>"
   git push -u origin feature/<slug>
   gh pr create --title "<normal title>" --body "<normal description>"
   ```
   Record the resulting PR number/URL at the top of the answer key file and
   in `backlog.md` (status -> `in-review`).

7. **Report to the user**: PR URL, and a short summary (counts by category/
   severity only - the detail stays in the file). Tell them the answer key is
   saved locally and gitignored, and that `evaluate` is ready whenever the
   reviewer agent has commented.

## Mode: evaluate

Args may name a PR number or branch; if omitted, use the PR open on the
current branch (`gh pr view --json number,headRefName,url`).

1. **Fetch what the reviewer agent actually said.** Get `owner/repo` from
   `gh repo view --json owner,name`, then pull everything - the bot may use
   inline comments, a formal review, or a plain issue comment:
   ```
   gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate   # inline
   gh api repos/{owner}/{repo}/pulls/{number}/reviews --paginate    # review verdicts
   gh api repos/{owner}/{repo}/issues/{number}/comments --paginate  # general comments
   ```

2. **Load the matching answer key** at `.claude/pr-bug-lab/answer-keys/<branch>.md`
   (map PR -> branch via `headRefName` from step 0).

3. **Score it**, using judgment rather than exact string/line matching:
   - Each answer-key row -> `caught` / `partially caught` (right spot, wrong
     root cause or severity) / `missed`.
   - Each reviewer comment with no matching row -> re-read that spot in the
     real diff yourself and classify as a genuine additional finding (credit
     it) or noise/nitpick with no real merit (false positive).

4. **Write** `.claude/pr-bug-lab/evaluations/<branch>.md`: recall overall and
   by severity/category, false-positive count, the list of anything
   critical/high that was missed, and 1-2 concrete examples of the reviewer
   agent's best and worst comments.

5. **Reply in chat** with the short version: recall %, what got missed (esp.
   critical/high), any false positives, one-line verdict. Full detail stays
   in the file.

6. Update `backlog.md` status to `evaluated` for that item.
