# Loading Clan Clash Scores (Hydra / Chimera / CvC)

This guide explains how to import clash scores for a clan — both the overall clan/opponent scores and per-player personal scores — using the app's forms, JSON input, or the image extraction helper.

## When to use this page
- You want to add a Hydra, Chimera, or CvC record for a clan.
- You have a screenshot of the results and prefer to extract personal scores automatically.
- You want to paste pre-collected scores in a structured JSON format.

## Options for importing scores
1. Manual entry via the form.
2. Paste structured JSON into the scores textarea.
3. Use the "Extract from Images (AI)" helper to OCR/ML-extract scores from screenshots.

## Placement Entry & Creation
- Open the clan page and choose the relevant activity (Hydra, Chimera, or CvC) then click Create or Edit.
- Use the table in the form to add opponent rows and enter numeric scores. The first row is pre-filled for your clan.
- Click Add Opponent to insert up to 4 opponents (5 clans total including yours).
- hydra allows for a 'deliberate throw' which excludes the score from
- Save

![clash creation](/static/clans/clashes.png)

## Personal scores - Use the Extract from Images (AI) helper
- Select the 'view/eye' option for the clash just created
- Click "Extract from Images (AI)".
- Paste or upload screenshots of the individual player scores screen. Prefer one screenshot per 4-6 players.
- The image helper sends images to the server which runs OCR/ML to extract clan names and scores and returns structured JSON.
- Review the parsed results in the modal. If correct, use the button to insert the JSON into the scores textarea or save the record directly.


## Manual Personal scores (per-player)
- The same view screen can allow for manual entering:
- a json array is used:
```
[
	{ "Name": "PlayerName1", "Score": 5.2, "Keys used": 1 },
	{ "Name": "PlayerName2", "Score": 3.0 }
]
```
- When you include personal scores, the server will map player names to existing Player records (by exact or case-insensitive match). If a player cannot be resolved, the score will still be stored in the activity record but will not be linked to a Player profile.

## Validation & common errors
- Non-numeric values for scores will cause an error. Verify the JSON uses numbers for scores.
- Mismatched names: ensure your player names are updated in each clan
- If image extraction fails or mis-parses names, edit the parsed JSON manually in the modal and re-insert.

## Troubleshooting tips
- If extraction produces unexpected names: crop closer to the score list and retry.
- If scores fail to save: check the browser console/network tab for response details. Server errors are returned as JSON with an `error` message.
- If personal scores do not link to players: verify player names in the clan roster (small differences in spacing or punctuation can prevent a match).


