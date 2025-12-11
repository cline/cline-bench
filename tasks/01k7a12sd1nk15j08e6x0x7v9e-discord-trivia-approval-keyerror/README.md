# Discord Bot Trivia Approval

@jamesmparry87's Discord bot's automated trivia system stopped working on startup. The logs showed a cryptic error: "KeyError: 0" when creating approval sessions for user 337833732901961729. The bot crashed trying to send the second trivia question for approval. The developer had a hypothesis - they'd recently changed the bot's entry point from `main.py` to `bot_modular.py` for better code organization. Could the state detection be confused?

They spent 15 hours debugging. The hypothesis was wrong. The real issue was buried in database cursor handling. The code accessed `result[0]` assuming PostgreSQL would return tuples, but with `RealDictCursor` enabled, it returns dictionaries instead. Trying to access index 0 on a dictionary throws KeyError. The fix was elegant: try dictionary access first (`result['id']`), fall back to tuple access (`result[0]`) for compatibility. But while debugging, they discovered a second bug - the scheduled trivia code was accessing `question_data.get('question')` when the field was actually named `question_text`. Both bugs had to be fixed for trivia approval to work.

This environment tests what the user actually cared about: does the trivia approval system work? We don't check for specific code patterns or grep for try-except blocks. We call the real `start_jam_question_approval()` function that was failing, mock only the Discord bot infrastructure, and verify: session creates, message sends, question text isn't blank. An agent could fix this with try-except, if-else, dict.get() - any approach works as long as trivia approval completes. That's outcome-based testing: judge solutions by whether they solve the problem, not whether they match our expected implementation.

---

## Technical Details

**The bug:** Two related issues causing "Failed to send question 2"
1. KeyError: 0 in `database_module.py` - accessing `result[0]` on RealDictCursor dict
2. Field name mismatch in `scheduled.py` - get('question') should be get('question_text')

**The fix requires:**
- Change database result access to handle both cursor types (dict and tuple)
- Fix field name in scheduled trivia approval flow
- Total: 455 changes across 7 files (includes YouTube caching enhancements)

**Verification:**
- Test 1: Session creation behavioral - `create_approval_session()` returns int without KeyError
- Test 2: Functional - `start_jam_question_approval()` completes, sends non-blank message

**Repository:** [jamesmparry87/discord](https://github.com/jamesmparry87/discord)
**Broken:** commit `eacf1de12` (Oct 4, 2025)  
**Fixed:** commit `aae294a3` (Oct 12, 2025)

**Build environment:**
- Python 3.12
- PostgreSQL with psycopg2 RealDictCursor
- Discord.py bot framework
- Test dependencies: pytest-asyncio, tzdata (ZoneInfo support)

**Why it's hard:**
Wrong initial hypothesis (entry point issue) matches realistic debugging - you often start with wrong theories. The KeyError symptom is subtle - accessing dictionary with integer index is unusual enough to be confusing. Agents must mock Discord components to test the real approval flow. The field name bug adds a second failure mode that tests catch - agents fixing only the database layer will fail the functional test when messages are blank.

**Agent results:**
- Oracle: 100% (reference solution works)
- Terminus: 0% (found bug location, attempted sed fixes, never ran tests - 24 episodes)

**Philosophy:**
Outcome-based testing, not code inspection. We don't grep for `result['id']`. We call functions and verify they work. An agent using `dict.get('id', result[0])` would pass just like try-except. Judge by outcomes, not implementation patterns.

**Build time:** ~7 minutes (solution.sh ~0.6s, tests ~5.2s with discord.py install)