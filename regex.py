# regex strings
quests = r"""🌲Forest \d{1,2}min
Many things can happen in the forest.

🍄Swamp \d{1,2}min
Who knows what is lurking in mud.

🏔Mountain Valley \d{1,2}min
Watch out for landslides.

🗡Foray 🔋🔋
Foray is a dangerous activity. Someone can notice you and may beat you up. But if you go unnoticed, you will acquire a lot of loot.

📯Arena [🔒]{0,1}
Arena isn't a place for the weak. Here you fight against other players and if you stand victorious, you acquire precious experience."""
quests_arena_open = r"""🌲Forest \d{1,2}min
Many things can happen in the forest.

🍄Swamp \d{1,2}min
Who knows what is lurking in mud.

🏔Mountain Valley \d{1,2}min
Watch out for landslides.

🗡Foray 🔋🔋
Foray is a dangerous activity. Someone can notice you and may beat you up. But if you go unnoticed, you will acquire a lot of loot.

📯Arena 
Arena isn't a place for the weak. Here you fight against other players and if you stand victorious, you acquire precious experience."""
quests_arena_locked = r"""🌲Forest \d{1,2}min
Many things can happen in the forest.

🍄Swamp \d{1,2}min
Who knows what is lurking in mud.

🏔Mountain Valley \d{1,2}min
Watch out for landslides.

🗡Foray 🔋🔋
Foray is a dangerous activity. Someone can notice you and may beat you up. But if you go unnoticed, you will acquire a lot of loot.

📯Arena 🔒
Arena isn't a place for the weak. Here you fight against other players and if you stand victorious, you acquire precious experience."""
arena_capture_remaining_fights = r"""📯Welcome to Arena!
Dirty air is soaked with the thick smell of blood\. No one ends up here by an accident: you can't leave once you begin your battle\. I hope, your sword is sharp and your shield is steady\.

Your rank: \d+
Your fights: (\d)\/5

Combat Ranking: \/top5
Fastest-growing: \/top6

Entrance fee: 5💰"""
arena_response = r"""-{0,1}\d{0,4}❤️.+
VS
-{0,1}\d{0,4}❤️.+

.+! \d{0,4}(?:\([-+]{0,1}\d{1,4}\)){0,1}

.+! \d{0,4}(?:\([-+]{0,1}\d{1,4}\)){0,1}

.+ stands victorious over .+
You received: \d{0,4} exp.
Leaderboard of fighters are updated: .top5 & .top6.*"""
error_not_enough_stamina = r"""Not enough stamina. Come back after you take a rest.

To get more stamina, invite friends to the game via invite link. Press /promo to get it."""
error_too_busy = r"""You are too busy with a different adventure. Try a bit later."""
arena_too_dark = r"""It’s hard to see your opponent in the dark. Wait until the morning."""
war_finished = """The wind is howling in the meadows, castles are unusually quiet. Warriors are mending their wounds and repairing armor after a tiresome battle. All the establishments and castle gates are closed for the next couple of minutes. Await the battle report at @chtwrsReports"""
level_up_bytes = b'RIFF\xe6\x14\x00\x00WEBPVP8X\n\x00\x00\x00\x10\x00\x00\x00\x7f\x00\x00\x7f\x00\x00ALPH\xb5\x05\x00'
help_message = r"""Welcome to control chat.
Here are the following commands:

/arena - Go arena until 5/5

/{valley | swamp} {#,#}+
Quest X number of times
Additionally, adding a "+" after the number appends an additional quest action when saving energy

/{valley | swamp}
Quest until out of energy

/status - current status of your control bot

/stop - stops the control bot from sending commands at cw bot

/ping - confirm the bot is running

/help - help message

Bugs:
Stopping and starting again without a few minutes in between will cause it to run twice, causing itself to error"""
status_update_capture_stamina = r"""Atk: \d+ 🛡Def: \d+\\n🔥Exp: \d+\/\d+\\n❤️Hp: \d+\/\d+\\n🔋Stamina: (\d+)\/\d+"""