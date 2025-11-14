"""
Bot Manager Module
Handles the lifecycle of all cloned bot instances:
- Starts all bots found in the database on startup.
- Spawns a new process for a newly cloned bot.
- Monitors running processes and restarts them if they fail.
"""

import logging
import asyncio
import subprocess
import sys
from typing import List, Dict, Optional
from database import Database
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class BotManager:
    """Manages the lifecycle of multiple ForwarderBotCore instances"""

    def __init__(self, db: Database):
        self.db = db
        # Dictionary to hold running processes: {bot_id: subprocess.Popen}
        self.running_bots: Dict[int, subprocess.Popen] = {}
        self.monitor_task: Optional[asyncio.Task] = None

    def start_all_cloned_bots(self):
        """Starts all bots marked as 'running' or 'pending' in the database"""
        cloned_bots = self.db.get_cloned_bots()
        logger.info(f"Found {len(cloned_bots)} cloned bot configurations in the database.")
        
        for bot_config in cloned_bots:
            if bot_config['status'] in ['running', 'pending']:
                self.spawn_bot_process(bot_config)

    def spawn_bot_process(self, bot_config: Dict):
        """Spawns a new subprocess for a single bot instance"""
        bot_id = bot_config['id']
        bot_token = bot_config['bot_token']
        
        if bot_id in self.running_bots and self.running_bots[bot_id].poll() is None:
            logger.warning(f"Bot {bot_id} is already running. Skipping spawn.")
            return

        try:
            # Command to run the core forwarder logic
            command = [
                sys.executable,  # Use the same Python interpreter
                'forwarder_core.py',
                bot_token
            ]
            
            # Start the subprocess
            process = subprocess.Popen(
                command,
                cwd='.',  # Current working directory (telegram-forwarder-bot)
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_bots[bot_id] = process
            
            # Update the database with the new process ID and status
            self.db.update_cloned_bot_status(bot_id, 'running', process.pid)
            logger.info(f"Successfully spawned bot {bot_id} (PID: {process.pid})")

        except Exception as e:
            logger.error(f"Failed to spawn bot {bot_id}: {e}")
            self.db.update_cloned_bot_status(bot_id, 'error')

    async def monitor_bots(self):
        """Asynchronously monitors all running bot processes"""
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            bots_to_check = list(self.running_bots.keys())
            for bot_id in bots_to_check:
                process = self.running_bots.get(bot_id)
                if process is None:
                    continue

                # Check if the process has terminated
                return_code = process.poll()
                if return_code is not None:
                    # Process has terminated
                    del self.running_bots[bot_id]
                    
                    # Read the bot's configuration from the database
                    bot_config = self.db.get_cloned_bot_by_id(bot_id)
                    
                    if bot_config:
                        # Log output for debugging
                        stdout, stderr = process.communicate()
                        logger.warning(f"Bot {bot_id} (PID: {bot_config.get('process_id')}) terminated with code {return_code}.")
                        logger.debug(f"Bot {bot_id} STDOUT: {stdout}")
                        logger.error(f"Bot {bot_id} STDERR: {stderr}")
                        
                        # Attempt to restart the bot
                        logger.info(f"Attempting to restart bot {bot_id}...")
                        self.spawn_bot_process(bot_config)
                    else:
                        logger.error(f"Configuration for terminated bot {bot_id} not found in DB.")

    async def start_monitoring(self):
        """Starts the background monitoring task"""
        if self.monitor_task is None or self.monitor_task.done():
            self.monitor_task = asyncio.create_task(self.monitor_bots())
            logger.info("Bot manager monitoring task started.")

    def stop_all_bots(self):
        """Terminates all running bot processes"""
        if self.monitor_task:
            self.monitor_task.cancel()
        
        for bot_id, process in self.running_bots.items():
            if process.poll() is None:
                try:
                    process.terminate()
                    self.db.update_cloned_bot_status(bot_id, 'stopped')
                    logger.info(f"Terminated bot {bot_id} (PID: {process.pid})")
                except Exception as e:
                    logger.error(f"Error terminating bot {bot_id}: {e}")
        self.running_bots.clear()

    def stop_bot_by_id(self, bot_id: int) -> bool:
        """Stops a single bot process by its ID"""
        process = self.running_bots.get(bot_id)
        if process and process.poll() is None:
            try:
                process.terminate()
                self.db.update_cloned_bot_status(bot_id, 'stopped')
                del self.running_bots[bot_id]
                logger.info(f"Stopped bot {bot_id} (PID: {process.pid})")
                return True
            except Exception as e:
                logger.error(f"Error stopping bot {bot_id}: {e}")
                return False
        return False

# Example usage (for testing purposes, will be integrated into the main bot.py)
# if __name__ == "__main__":
#     # This part is for demonstration and will be removed/integrated
#     db = Database(db_path=DATABASE_PATH)
#     manager = BotManager(db)
#     
#     # Start all existing bots
#     manager.start_all_cloned_bots()
#     
#     # Start monitoring
#     asyncio.run(manager.start_monitoring())
