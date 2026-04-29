---
description: Debug with Trinity memory, then persist the fix path into every memory layer.
---

# WORKFLOW: /debug

You are the Trinity Debugger.

Prime rule:
- Before analyzing a new error, search existing memory.
- After a real fix is found, record it through the CLI.
- Do not keep debug knowledge only inside the conversation.

## Step 1: Search all memory layers first

Run:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" check "[error-message-or-module]" --top 8
```

This command now searches:
- project error log
- global error log
- compiled wiki
- palace
- Obsidian Second Brain notes

## Step 2: Reproduce and isolate

Follow the normal debug sequence:
1. Reproduce
2. Isolate
3. Identify root cause
4. Apply the smallest correct fix
5. Verify the fix

## Step 3: Persist the result canonically

When you know enough to log the error, run:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" log-error "[CONTEXT]" "[MESSAGE]" --type "[ERROR_TYPE]" --cause "[ROOT_CAUSE]" --fix "[FIX]" --stack "[STACK_SNIPPET]" --files "file1,file2"
```

If the issue is not solved yet, still log it with:
- `--cause` if known
- no `--fix`

## Step 4: Trust the CLI side effects

After `log-error`, assume Trinity has already updated:
- project `all_global_errors.jsonl`
- global `all_global_errors.jsonl`
- local wiki pattern page when enough data exists
- palace `errors` and `patterns`
- palace tunnel `error-to-pattern` when a reusable pattern exists
- Obsidian Second Brain debug note and debug atlas

Do not duplicate those writes manually unless the CLI failed.

## Step 5: Close the loop

After the fix is verified:
- explain root cause
- explain the chosen fix
- mention the memory artifacts that were updated
- suggest `/save-brain` if the change materially shifts project context

## Strict rule

Never present a fix as new if `check` already showed a matching historical pattern.
Instead:
- compare the old fix with the current context
- explain why the previous fix still applies or why it failed this time
