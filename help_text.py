HELP = {
"BOT": """```
The immersion bot converts your immersion be it anime, reading, listening into points by logging them with /log. By logging you will be placed on the immersion leaderboards where you can compete in a friendly environment against other learnes for the first place.

Multipliers for immersion = {
    'BOOK': 1,
    'MANGA': 0.2,
    'VN': 1 / 350,
    'ANIME': 9.5,
    'READING': 1 / 350,
    'LISTENING': 0.45,
    'READTIME': 0.45
}

For feedback: @timm04
Github: https://github.com/themoeway/Immersionbot```""",
"achievements": """```py
/achievements

Displays all of your immersion milestones.
You can get the following titles:
['Beginner', 'Initiate', 'Apprentice', 'Hobbyist', 'Enthusiast', 'Aficionado', 'Sage', 'Master']```""",
"export": """```/export

Arguments:
- timeframe: Span of logs used
Optional:
- media_type: Export only logs of a specify media type.
- date: Entering a date will further specify the timeframe argument. [year-month-day i.e '2022-12-19']

For example:
Selecting timeframe=Monthly and date=2023-2-5, will export all of your logs in Feburary
Selecting timeframe=Weekly and date=2023-5-18, will export all of your logs between the 15th-21th of Mai.```""",
"goal": """```/goals

Displays all of your goals.```""",
"set_goal": """```/set_goal_media & /set_goal_points

Set a goal for a medium or set a point goal for example get 200 points.

Arguments:
- media type
- amount to be reached to complete goal
- span: Day=Till the end of today, Daily=Everyday, Date=Till a certain date [year-month-day]
- name: Name of your immersion material, you can use Anilist or VNDB ids, enter the name directly or find it in the dropdown menu.

Examples:
Setting a goal to watch 5 eps of Neon Genesis Evangelion till the end of the day.
/set_goal_media media_type:Anime amount:1 span:DAY name:Shin Seiki Evangelion (新世紀エヴァンゲリオン)
You can also use codes to abbreviate the name (https://anilist.co/anime/30/Neon-Genesis-Evangelion/):
/set_goal_media media_type:Anime amount:1 span:DAY name:30

Note: With the above goal set, only logs that EXACTLY have Shin Seiki Evangelion (新世紀エヴァンゲリオン) or the abbreviation code set as name, count towards it. So if you do this instead
/log media_type:Anime amount:1 name:Neon Genesis Evangelion
it won't count, so spelling is important.

Setting a goal to read 25k characters of any Visual Novel everyday:
/set_goal_media media_type:Visual Novel amount:25000 span:Daily

Note: With the above goal set, you can log anything that has Visual Novel as media_type and it will count towards that goal.

Setting a goal to listen 6hrs till the 2024-01-28 (28th January):
/set_goal_media media_type:Listening amount:6:00 span:2024-01-28

Setting a goal of logging 500 points of ANYTING till the end of today:
/set_goal_points media_type:Anything amount:500 span:DAY```""",
"leaderboard": """```/leaderboard
    
Arguments:
- timeframe: Span of logs used
Optional:
- media_type: Export only logs of a specify media type.
- date: Entering a date will further specify the timefram argument. [year-month-day i.e '2022-12-19']

Examples:
Leadboard for Anime between the 11th and 18th December 2023:
/leaderboard timeframe:Weekly media_type:Anime date:2023-12-12```""",
"user": """```/user
    
Arguments:
- user: A user
- timeframe: Span of logs used
Optional:
- media_type: Export only logs of a specify media type.
- date: Entering a date will further specify the timefram argument. [year-month-day i.e '2022-12-19']
Examples:
/user user:@alexmarscat timeframe:Monthly
/user user:@ayamisensei timeframe:Monthly media_type:Listening date:2024-01-25```""",
"undo": """```/undo

Removes your latest log.```""",
"log": """```/log

Logs your immersion.
If you want your log to count towards a goal you set with /set_goal, make sure the name matches of the goal matches EXACTLY the one from the log.

Arguments:
- media type
- amount to be reached to complete goal
Optional:
- name: Name of your immersion material, you can use Anilist or VNDB ids, enter the name directly or find it in the dropdown menu.
- comment: Your comment

Examples:
/log media_type:Readtime amount:35
/log media_type:Visual Novel amount:20000 name:v2016 comment:鬼に逢うては鬼を斬る 仏に逢うては仏を斬る ツルギの理ここに在り
Note: Instead of 'v2016' Muramasa would've as well.
/log media_type:Anime amount:1 name:LycoReco comment:Ep.2```""",
"backfill": """```/backfill [date] [media_type] [amount] [name(optional)] [comment(optional)]

Arguments:
- date: Backfill date [year-month-day i.e '2022-12-19']
- media type (VN, anime, etc)
- amount to backfill
Optional:
- name of the series
- comment

Examples:
/backfill date:2024-01-07 media_type:Reading amount:126673  name:乙女ゲームの破滅フラグしかない悪役令嬢に転生してしまった 7
/backfill date:2023-12-26 media_type:Anime amount:1 name:Shita-kiri Suzume (したきりすずめ)
/backfill date:2023-09-02 media_type:Listening amount:60 name:youtube```""",
"delete_goal": """```/delete_goal

Deletes a set goal.

Arguments:
- media type
- amount
- span: Goal type of the goal you want to delete```""",
"logs": """```/logs

Display your past logs```"""
}