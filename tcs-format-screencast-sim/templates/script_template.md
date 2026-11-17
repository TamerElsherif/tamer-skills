# Screencast step script — <lesson_id> · task: <task>

System: <fictional or generic name> · Screen kind: form | table | list | settings | dashboard | screenshot

| step | cue | do | target (field id) | value / label | narration (`^` before the verb) | why (only if non-obvious) | source |
|---|---|---|---|---|---|---|---|
| 1 | 0 | click | date | | ^ Pick the date. | | S08#c1 |
| 2 | 1 | select | cat | Taxi | ^ Choose the category. | | |
| 3 | 2 | type | amount | 23.50 | ^ Type the amount. | | |
| 4 | 3 | click | receipt | Attach the photo | ^ Attach the receipt. | mandatory → hint | S01#p3 |
| 5 | 4 | click | submit | | ^ Press submit… | | |
| 6 | 5 | toast | | Claim sent to your manager | ^ …and it goes to your manager. | | |

Practice: task "<…>" · expect [<target=value>…] · hints {…} · max_attempts 3 · on_fail replay_demo
