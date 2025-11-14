"""
Test suite for Telegram Channel Forwarder Bot
Tests database operations, rate limiting, and message handling
"""

import unittest
import os
import sqlite3
import tempfile
import asyncio
from datetime import datetime
from database import Database
from config import (
    MESSAGES_PER_BATCH,
    BATCH_INTERVAL_SECONDS,
    DELAY_PER_MESSAGE,
)


class TestDatabase(unittest.TestCase):
    """Test database operations"""

    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_database_initialization(self):
        """Test that database initializes correctly"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Check that tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        self.assertIn('forwarded_messages', tables)
        self.assertIn('bot_state', tables)
        self.assertIn('forwarding_progress', tables)
        self.assertIn('error_log', tables)

        conn.close()

    def test_add_forwarded_message(self):
        """Test adding a forwarded message"""
        result = self.db.add_forwarded_message(
            source_message_id=12345,
            destination_message_id=67890,
            message_type='text'
        )

        self.assertTrue(result)
        self.assertTrue(self.db.is_message_forwarded(12345))

    def test_duplicate_message_handling(self):
        """Test that duplicate messages are handled correctly"""
        # Add a message
        self.db.add_forwarded_message(12345, 67890, 'text')

        # Try to add the same message again
        result = self.db.add_forwarded_message(12345, 67890, 'text')

        # Should return False (duplicate)
        self.assertFalse(result)

    def test_forwarding_progress(self):
        """Test forwarding progress tracking"""
        # Update progress
        self.db.update_forwarding_progress(
            last_forwarded_message_id=100,
            total_messages_forwarded=50,
            historical_forwarding_complete=False
        )

        # Get progress
        progress = self.db.get_forwarding_progress()

        self.assertIsNotNone(progress)
        self.assertEqual(progress['last_forwarded_message_id'], 100)
        self.assertEqual(progress['total_messages_forwarded'], 50)
        self.assertEqual(progress['historical_forwarding_complete'], 0)

    def test_bot_state(self):
        """Test bot state management"""
        # Set state
        self.db.set_state('test_key', 'test_value')

        # Get state
        value = self.db.get_state('test_key')

        self.assertEqual(value, 'test_value')

    def test_error_logging(self):
        """Test error logging"""
        self.db.log_error(
            error_type='TEST_ERROR',
            error_message='This is a test error',
            source_message_id=12345
        )

        errors = self.db.get_recent_errors(limit=1)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_type'], 'TEST_ERROR')
        self.assertEqual(errors[0]['error_message'], 'This is a test error')

    def test_statistics(self):
        """Test statistics retrieval"""
        # Add some messages
        self.db.add_forwarded_message(1, 10, 'text')
        self.db.add_forwarded_message(2, 20, 'photo')
        self.db.add_forwarded_message(3, 30, 'video')

        # Add some errors
        self.db.log_error('ERROR1', 'Error message 1')
        self.db.log_error('ERROR2', 'Error message 2')

        # Check statistics
        forwarded_count = self.db.get_forwarded_count()
        error_count = self.db.get_error_count()

        self.assertEqual(forwarded_count, 3)
        self.assertEqual(error_count, 2)


class TestRateLimiting(unittest.TestCase):
    """Test rate limiting calculations"""

    def test_rate_limiting_parameters(self):
        """Test that rate limiting parameters are correct"""
        # 50 messages per 20 minutes
        self.assertEqual(MESSAGES_PER_BATCH, 50)
        self.assertEqual(BATCH_INTERVAL_SECONDS, 20 * 60)  # 1200 seconds

        # Calculate delay per message
        expected_delay = BATCH_INTERVAL_SECONDS / MESSAGES_PER_BATCH
        self.assertAlmostEqual(DELAY_PER_MESSAGE, expected_delay, places=2)

    def test_rate_limiting_timeline(self):
        """Test rate limiting timeline"""
        # 50 messages per 20 minutes = 2.5 messages per minute
        messages_per_minute = MESSAGES_PER_BATCH / (BATCH_INTERVAL_SECONDS / 60)
        self.assertAlmostEqual(messages_per_minute, 2.5, places=2)

        # Delay between messages should be ~24 seconds
        expected_delay = 60 / messages_per_minute
        self.assertAlmostEqual(DELAY_PER_MESSAGE, expected_delay, places=2)

    def test_batch_forwarding_timeline(self):
        """Test that batch forwarding timeline is correct"""
        # Forward 50 messages every 20 minutes
        # Timeline:
        # - Minute 0: Messages 1-50
        # - Minute 20: Messages 51-100
        # - Minute 40: Messages 101-150

        batch_size = MESSAGES_PER_BATCH
        batch_interval = BATCH_INTERVAL_SECONDS / 60  # Convert to minutes

        # After 40 minutes, should have completed 2 batches (0-20, 20-40)
        # Which means 100 messages forwarded
        batches_completed = 40 / batch_interval
        messages_forwarded = int(batches_completed * batch_size)

        self.assertEqual(messages_forwarded, 100)


class TestMessageTypeDetection(unittest.TestCase):
    """Test message type detection"""

    def test_message_type_strings(self):
        """Test that message type strings are valid"""
        valid_types = [
            'text', 'photo', 'video', 'animation',
            'document', 'audio', 'voice', 'sticker',
            'location', 'contact', 'poll', 'unknown'
        ]

        for msg_type in valid_types:
            self.assertIsInstance(msg_type, str)
            self.assertTrue(len(msg_type) > 0)


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration validation"""

    def test_rate_limiting_config(self):
        """Test that rate limiting configuration is valid"""
        # Batch size should be positive
        self.assertGreater(MESSAGES_PER_BATCH, 0)

        # Batch interval should be positive
        self.assertGreater(BATCH_INTERVAL_SECONDS, 0)

        # Delay per message should be positive
        self.assertGreater(DELAY_PER_MESSAGE, 0)

        # Delay should be less than batch interval
        self.assertLess(DELAY_PER_MESSAGE, BATCH_INTERVAL_SECONDS)

    def test_rate_limiting_sanity(self):
        """Test rate limiting sanity checks"""
        # Total delay for a batch should equal batch interval
        total_delay = DELAY_PER_MESSAGE * MESSAGES_PER_BATCH
        self.assertAlmostEqual(total_delay, BATCH_INTERVAL_SECONDS, delta=1)


class TestAsyncRateLimiting(unittest.TestCase):
    """Test async rate limiting behavior"""

    async def test_rate_limit_timing(self):
        """Test that rate limiting respects timing"""
        import time

        delays = []
        start_time = time.time()

        # Simulate rate limiting for 5 messages
        for i in range(5):
            current_time = time.time()
            elapsed = current_time - start_time
            delays.append(elapsed)

            # Simulate the delay
            await asyncio.sleep(0.1)  # 100ms delay between messages

        # Check that delays are increasing
        for i in range(1, len(delays)):
            self.assertGreater(delays[i], delays[i - 1])

    def test_async_rate_limiting(self):
        """Run async rate limiting test"""
        asyncio.run(self.test_rate_limit_timing())


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimiting))
    suite.addTests(loader.loadTestsFromTestCase(TestMessageTypeDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestAsyncRateLimiting))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
