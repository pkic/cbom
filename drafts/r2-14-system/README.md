# Draft for R2-14: the subject type `system` (superseded)

R2-14 was applied to Release 1 on 17 November 2026: the published interface disclosure baseline
v0.10 accepts the subject types `service` and `system`. This draft is kept as the record of the test
that led to it. The OT system overlay and its system record are now in `drafts/ot-system/`.

`_to_delete/profile-interface-disclosure.rules.json` is the draft baseline, v0.10-draft. It differs
from the published v0.10 only in its version, date and comments. Delete the folder.

`build.py` still writes the draft baseline and the first system record. Run it only to reproduce the
test: against the published baseline v0.9, the system record failed P3 and P5 and nothing else.
