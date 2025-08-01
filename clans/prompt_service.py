from .models import TEAM_CHOICES, Clan

def generate_siege_post_prompt():
    return (
        "Extract the post number and all choices from this image of a Raid Shadow Legends siege post. "
        "There should be a post number and a list of exactly 3 choices. "
        "The choices should be selected only from this list of valid team types: "
        f"{[choice[0] for choice in TEAM_CHOICES]}. "
        "Return only a JSON object like: {{\"Post\": <number>, \"Choices\": [\"choice1\", \"choice2\", ...]}}."
    )

def generate_clash_player_prompt(clan_id):
    clan_players = [player.name for player in Clan.objects.get(clan_id=clan_id).players.all()]

    json_schema_string = """
        {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "List of User Accounts",
        "description": "A list of user accounts.",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
            "Name": {
                "type": "string"
            },
            "Score": {
                "type": "number"
            },
            "Keys used": {
                "type": "integer",
                "enum": [0, 1, 2, 3]
            }
            },
            "required": [
            "Name",
            "Score",
            "Keys used"
            ]
        }
        }
    """

    return f"""
        Extract the Player name, score and keys used, per player, from these images of a Raid Shadow Legends Clash Results page. 
        Scores are shown in the format "<decimal>B" (e.g. "1.5B" for 1.5 billion). and will only ever be 2 decimal places followed by "B" (billions) or "M" Millions.
        Make sure to convert the score to a decimal number, e.g. "1.5B" should be converted to 1500000000, and "150.5M" should be converted to 1505000000.
        You should then format the score as a decimal number, using Billions as the units, without any suffixes or prefixes (e.g. 1500000000 should be formatted as 1.5, 1505000000 should be formatted as 0.1505).
        The keys used are shown as a number from 0 to 3, representing the number of keys used by the player.
        The results should be returned as a JSON array of objects, each with "Name", "Score" and "Keys used" fields.
        The "Name" field should be the player's name, the "Score" field should be a decimal number, and the "Keys used" field should be an integer.
        The player names should be selected only from this list of valid players: 
        {clan_players}. 
        if a player is not in this list, they should not be included in the results.
        if a player is in the list but has no score, they should be included with a score of 0 and keys used of 0.
        Return only a JSON object that fits the following schema:
        {json_schema_string}
    """
