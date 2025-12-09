The automated trivia approval on startup is not working with the following log errors:

INFO:bot.database_module:Creating approval session for user 337833732901961729, type: question_approval
ERROR:bot.database_module:❌ Error creating approval session - Exception type: KeyError
ERROR:bot.database_module:❌ Error creating approval session - Message: 0
ERROR:bot.database_module:❌ Error creating approval session - User ID: 337833732901961729, Session type: question_approval
❌ Failed to create persistent approval session
❌ SEQUENTIAL APPROVAL: Failed to send question 2

Could it be because we changed the state detection to the bot to bot_modular rather than main as we changed the standard entry point for the bot?

The error occurs in Live/bot/database_module.py in the _insert_approval_session helper method.
The bug is related to how the code accesses database query results when using psycopg2's RealDictCursor.

Your task is to fix the database result access pattern to work correctly with RealDictCursor,
which returns dictionary-like objects rather than tuples.

<environment_details>
# Visual Studio Code Visible Files
Live/bot/commands/trivia.py

# Visual Studio Code Open Tabs
Live/bot_modular.py
Live/bot/handlers/ai_handler.py
Live/bot/database_module.py
Live/bot/handlers/message_handler.py
Live/bot/commands/trivia.py
Live/bot/handlers/conversation_handler.py
Live/bot/integrations/youtube.py
</environment_details>