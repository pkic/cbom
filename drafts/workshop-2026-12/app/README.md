# CBOM Tabletop Live

The December 2026 tabletop ("Your supplier sent a CBOM. Now what?") as a web app for about 200 people.
It runs the same exercise as the paper version in `../README.md`. Teams read the three supplier
documents, fill in a shared plan, write gap cards and answer the four injects on their phones. The
facilitator drives the session from one console, and the projector shows the room's answers as they
come in.

One file, `index.html`, serves every view. The part after `#` in the address picks the view.

| Address | Who opens it | What it shows |
|---|---|---|
| `…/workshop/#join` | Every participant, from the QR code | Join form, then whatever stage the facilitator has opened |
| `…/workshop/#present` | Lead facilitator, on a laptop | Running order, injects, timer, answer reveals, moving cards on the wall, exports |
| `…/workshop/#screen` | The projector | Join QR code, documents, the room's plan, inject results, the mapping wall, poll |
| `…/workshop/#rehearse` | Anyone preparing | All three views in one page, with five simulated tables. Nothing is saved |

## How the paper exercise maps to the app

| Paper version | App |
|---|---|
| Scenario pack, one per person | Document tab on the phone; projector shows the same table |
| Role cards | Chosen at join; Role tab on the phone |
| Plan sheet, one per table | Plan tab. The table shares one plan; the last change wins |
| Gap cards | Gap cards tab. Same fields as the printed card |
| Inject envelopes | Facilitator presses Inject 1–4. It opens on every phone and on the projector. One answer per table |
| Wall placement by teams | "Mapping wall: place cards" stage. Each table picks a column and a row per card |
| The walk | "Mapping wall: the walk". The facilitator reveals the answer key one column at a time and moves cards to their final place |
| Formbricks poll | "Temperature poll" stage. Live bars on the projector |
| Sign-up sheet | "Close" stage. Emails are visible only to the facilitators |
| Photographing the wall, transcribing cards | "Copy gaps as Markdown" gives the GitHub issue body. "Download all results (CSV)" exports everything |

## Running it live

The app needs a small shared database so that 200 phones see the same stage. It uses
[Supabase](https://supabase.com) through its REST interface. No server code is needed.

1. **Create a Supabase project** in an EU region (for example Frankfurt), so that participants' names
   and answers stay in the EU.
2. **Run `schema.sql`** in the project's SQL editor. Change the facilitator PIN in the last line first.
3. **Copy the project URL and the anon key** (Project settings › API) into the `CONFIG` block at the
   top of `index.html`.
4. **Publish `index.html`** with the working group site, for example as `docs/workshop/index.html`. The
   join address is then `https://pkic.github.io/cbom/workshop/#join`.
5. **Dry run in mid-November** with working-group members on their own phones. Use "Reset session…"
   in the console afterwards. It deletes every answer, person and sign-up.

**Plan.** A free Supabase project pauses after a week without use, so wake it before the dry run and
again before the event. Alternatively, take the Pro plan (about US$25 a month) for November and
December. Check current terms on supabase.com/pricing. The load is small: phones ask for the stage
every 2 seconds and for their table's answers every 4 seconds. The console and projector fetch only
what changed every 3 seconds.

**Without Supabase**, the file runs in local mode. All tabs in one browser on one computer share their
state, which is useful for preparing, but not for the room.

## On the day

- Open `#present` on the facilitator laptop and enter the PIN. Press "Open projector view" and move
  that window to the projector.
- Put the QR code up during the lobby stage. The projector counts people and tables as they join.
- Inject 1 starts a 5-minute timer by itself. Use the timer buttons for the other segments.
- During the tabletop, the projector shows how the tables are planning each system. Use it to prompt
  the room, for example: "Eight tables chose Software update for svc-https. What told you that?"
- The console's card feed has a Hide button for anything that should not be on the screen.
- At the walk, reveal one column at a time, as in the paper script. End on the "No profile requires
  it yet" row.

## Privacy

- Participants enter a name and a table number. They choose to give an email at the close.
- Anyone with the join link can read names, tables and answers. The sign-up emails are not readable
  through the public key; only `ws_export_signups` returns them, and it needs the PIN.
- Delete the data after the write-up (Reset session, or delete the Supabase project).

## Changing the content

All workshop content is in the `CONTENT` section of `index.html`: roles, actions, the three
documents, injects with their answers, the answer-key gaps, poll statements and the running order.
It was taken from `scenario.md`, `cards.md` and `answer-key.md`. If those change after the dry run,
change both.
