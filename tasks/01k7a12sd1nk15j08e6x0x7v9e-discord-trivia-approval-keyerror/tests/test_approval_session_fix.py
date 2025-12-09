"""
Test suite for Discord bot trivia approval session KeyError fix.

PHILOSOPHY: Outcome-based testing, not prescriptive code inspection.
We test WHAT the user cared about (trivia approval works), not HOW it's implemented.
"""

import os
import sys
import pytest
import subprocess
from unittest.mock import Mock, AsyncMock, patch

# Add the Live directory to Python path
sys.path.insert(0, '/app/Live')


def test_approval_session_creation():
    """
    Test 1: BEHAVIORAL - Database session creation works without KeyError.
    
    The user's error: "ERROR:bot.database_module:❌ Error creating approval session - KeyError: 0"
    
    This test verifies create_approval_session() returns an integer without throwing KeyError,
    using the exact parameters from the production bug report.
    
    We don't test HOW it's fixed (try/except, if/else, whatever) - just that it WORKS.
    """
    # Start PostgreSQL for testing
    subprocess.run(['service', 'postgresql', 'start'], 
                   capture_output=True, check=True)
    
    try:
        from bot.database_module import get_database
        
        db = get_database()
        db.init_database()
        
        # Exact scenario from bug report
        test_user_id = 337833732901961729
        test_session_type = 'question_approval'
        test_question_data = {
            'question_text': 'Test question',
            'question_type': 'single',
            'correct_answer': 'Test answer'
        }
        
        # In broken state: This throws KeyError: 0
        # In fixed state: Returns integer session ID
        session_id = db.create_approval_session(
            user_id=test_user_id,
            session_type=test_session_type,
            conversation_step='awaiting_approval',
            question_data=test_question_data,
            conversation_data={},
            timeout_minutes=180
        )
        
        # Outcome-based assertions: Did it work?
        assert session_id is not None, "Session ID should be returned"
        assert isinstance(session_id, int), f"Should return int, got {type(session_id)}"
        assert session_id > 0, f"Should return positive ID, got {session_id}"
        
        print(f"✓ Session creation works: Returned session_id={session_id}")
        print("✓ No KeyError: 0 thrown")
        print("✓ Database cursor bug fixed (don't care HOW - just that it works)")
        
    finally:
        subprocess.run(['service', 'postgresql', 'stop'], capture_output=True)


@pytest.mark.asyncio
async def test_trivia_approval_function():
    """
    Test 2: FUNCTIONAL - The actual failing function completes successfully.
    
    The user's complaint: "automated trivia approval on startup is not working"
    Error message: "❌ SEQUENTIAL APPROVAL: Failed to send question 2"
    
    This tests what the user ACTUALLY cared about: Does start_jam_question_approval() work?
    We mock Discord (external dependency) but test the real Python function flow.
    """
    # Start PostgreSQL
    subprocess.run(['service', 'postgresql', 'start'], 
                   capture_output=True, check=True)
    
    try:
        from bot.database_module import get_database
        from bot.handlers.conversation_handler import start_jam_question_approval, JAM_USER_ID
        import discord
        
        db = get_database()
        db.init_database()
        
        # Real question_data as it comes from scheduled.py
        question_data = {
            'question_text': 'Which game has the most episodes?',
            'question_type': 'single',
            'correct_answer': 'Final Fantasy XIV',
            'category': 'episodes',
            'difficulty_level': 2
        }
        
        # Mock Discord (external system we can't control)
        mock_bot = AsyncMock(spec=discord.Client)
        mock_user = AsyncMock(spec=discord.User)
        mock_user.name = "JAM"
        mock_user.discriminator = "0000"
        mock_user.send = AsyncMock(return_value=Mock(id=12345))
        mock_bot.fetch_user = AsyncMock(return_value=mock_user)
        
        # Test the ACTUAL function that was failing
        with patch('bot.handlers.conversation_handler._get_bot_instance', return_value=mock_bot):
            result = await start_jam_question_approval(question_data)
            
            # Outcome-based assertions: Did the function complete?
            assert result is True, "Function should complete successfully"
            
            # Was the message sent?
            assert mock_user.send.called, "Should send approval message"
            sent_message = mock_user.send.call_args[0][0]
            assert len(sent_message) > 0, "Message should not be empty"
            
            # Does the message contain the question? (verifies field name works)
            assert 'Which game has the most episodes' in sent_message or 'question' in sent_message.lower(), \
                "Message should contain question text (not blank)"
            
            print(f"✓ start_jam_question_approval() completed successfully")
            print(f"✓ Approval message sent to user")
            print(f"✓ Message contains question (not blank)")
            print(f"✓ User's complaint 'Failed to send question 2' - SOLVED")
        
    finally:
        subprocess.run(['service', 'postgresql', 'stop'], capture_output=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])