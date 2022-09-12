BANNER_DESC = "This module can help servers manipulate their banner through commands. Servers naturally must have access to this feature before use."
BANNER_HELP = """
Post server banner in chat:
    .banner get

Set server banner
    .banner set {<link> | [--random | -r]}
    
    OPTIONS:
    <link> : Set banner to a linked image
    --random | -r : Set to a random image found in server's gallery

Start the banner cycle:
    .banner start

Stop the banner cycle:
    .banner stop

Update how long it takes for banner to cycle to the next. NOTE: Discord may limit data transfer if made too frequent, would recommend at least 20 minutes between cycles.
    .banner timer {<None> | [--set | -s <minutes>]}

    OPTIONS:
    <None> : Shows the current timer
    --set | -s <minutes> : Set the timer 
"""