# Siege Plans

This page explains how to create a siege plan and generate the plan JSON using the image-upload helper modal (the image helper uses the app's image/ML service to extract post data from screenshots).

## Checklist
- Prepare clear screenshots (one per post recommended)
- Create a new siege plan for the correct clan
- Use the Image Helper modal to upload screenshots and generate JSON
- Paste or insert the generated JSON into the plan and save
- Open the Assign page and pick players and arena teams

## Step-by-step

1) Prepare screenshots

- Take clear screenshots showing each post you want recognized. One image per post works best; crop to the relevant area when possible.

2) Create a new siege plan

- In the app go to the clan you want to plan for and choose Create Siege Plan.
- Give the plan a name and save it. You can leave the plan data blank if you will import via the image helper, otherwise add in the required `json` object.

![Create Siege](/static/clans/create_siege.png)

3) Extract Post Conditions via 'Extract From Images (AI)' Helper

![Extract Conditions](/static/clans/extract_siege.png)

4) Upload screenshots and generate JSON

- Upload the screenshots in the modal and click the button to process them. This may take a minute or two.
- The client sends the images to the server (the app's image helper endpoint). The service returns structured JSON describing posts (post numbers, suggested team choices, champion lists, etc.).
- The modal shows the parsed results and the JSON output.

![alt text](/static/clans/create_conditions.png)

5) Insert the generated JSON into the plan
- If the modal offers "Use as Plan Data" option to automatically save the JSON to the plan, which imports it into the plan data field.
- Otherwise, copy the JSON, open Edit Plan, paste the JSON into the plan data field (a big textarea).
- Press 'Create Plan'

6) Open the Assign Siege Plan page

- From the clan page or Recent Siege Plans, open the plan's Assign page. This is where posts, team types, players, and arena teams are chosen.

7) Confirm posts appear

- The posts should now be rendered from the plan.
- If any post is wrong, try re-running the image helper with better screenshots or edit the JSON manually. 

8) Assign players and arena teams

- For each post pick the Team Type (if applicable), then choose a player from the filtered list.
- After selecting a player their ArenaTeams will be shown, filtered to allow only teams that fit the selected condition. Pick a Team for the post.
- The app validates ownership (the team belongs to the selected player) and prevents a player from reusing the same champion where enforced.
![assigned](/static/clans/assigned.png)
9) Export the plan

- Use Export (Export to Discord) to produce a Discord-ready markdown list of posts, teams, players, and champions.
- Click Copy to copy the formatted text to the clipboard.
![export](/static/clans/export.png)

10) Troubleshooting & tips

- If posts aren't recognized: use higher-resolution screenshots or crop to the post area and retry.
- If arena teams won't save: ensure the selected arena team belongs to the chosen player and doesn't conflict with that player's other selected teams.
- If the image helper returns an error: check server logs or retry with different images.


