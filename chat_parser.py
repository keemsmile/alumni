import re
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional
import logging

class ChatParser:
    def __init__(self):
        # Core message pattern - handles Unicode characters and emojis
        self.message_pattern = r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?\s*[APMapm]{2})\]\s*([^:]+):\s*(.+)$'
        
        # Special message patterns (for system messages and group notifications)
        self.system_msg_pattern = r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?\s*[APMapm]{2})\]\s*(.+)$'
        
        # Track conversation contexts
        self.conversations = []
        
        # Set up logging
        logging.basicConfig(filename='chat_parser.log', 
                          level=logging.INFO,
                          format='%(asctime)s - %(message)s')

    def parse_timestamp(self, date_str: str, time_str: str) -> Optional[datetime]:
        """Convert timestamp string to datetime object"""
        formats = [
            '%m/%d/%y, %I:%M %p',
            '%m/%d/%Y, %I:%M %p',
            '%m/%d/%y, %I:%M:%S %p',
            '%m/%d/%Y, %I:%M:%S %p',
        ]
        ts_str = f"{date_str}, {time_str}"
        for fmt in formats:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue
        logging.error(f"Failed to parse timestamp: {ts_str}")
        return None

    def clean_username(self, username: str) -> str:
        """Standardize username format"""
        username = re.sub(r'@\d+', '', username)
        return username.strip()

    def clean_message(self, message: str) -> str:
        """Remove control characters while preserving emojis and meaningful content"""
        # Remove Left-to-Right Mark and other control characters
        message = message.replace('\u200e', '')  # Remove LTR mark
        message = message.replace('\u200f', '')  # Remove RTL mark
        # Remove other invisible control characters in range U+200B to U+200F
        message = re.sub(r'[\u200b-\u200f]', '', message)
        return message.strip()

    def detect_message_type(self, message: str) -> str:
        """Detect if message contains media or is system message"""
        media_markers = ['sticker omitted', 'image omitted', 'audio omitted', 'video omitted', 'Contact card omitted']
        system_markers = [
            'Messages and calls are end-to-end encrypted',
            'created this group',
            'added',
            'left',
            'removed',
            'changed the subject',
            'changed this group\'s icon',
            'deleted this message'
        ]
        if any(marker in message for marker in media_markers):
            return 'media'
        if any(marker in message for marker in system_markers):
            return 'system'
        return 'text'

    def extract_message(self, line: str) -> Optional[Dict]:
        """Extract structured data from a chat line"""
        # Try normal message pattern
        match = re.match(self.message_pattern, line)
        if match:
            date_str, time_str, username, message = match.groups()
            message = self.clean_message(message)
            return {
                'timestamp': self.parse_timestamp(date_str, time_str),
                'username': self.clean_username(username),
                'message': message,
                'type': self.detect_message_type(message)
            }
        
        # Try system message pattern
        match = re.match(self.system_msg_pattern, line)
        if match:
            date_str, time_str, message = match.groups()
            message = self.clean_message(message)
            return {
                'timestamp': self.parse_timestamp(date_str, time_str),
                'username': 'SYSTEM',
                'message': message,
                'type': 'system'
            }
            
        return None

    def detect_conversation_break(self, current_msg: Dict, prev_msg: Optional[Dict]) -> bool:
        """Detect if this message starts a new conversation"""
        if not prev_msg or not prev_msg['timestamp'] or not current_msg['timestamp']:
            return True
            
        # Time gap > 1 hour suggests new conversation
        time_gap = current_msg['timestamp'] - prev_msg['timestamp']
        if time_gap.total_seconds() > 3600:
            return True
            
        return False

    def parse_chat(self, text: str) -> pd.DataFrame:
        """Parse entire chat log into structured format"""
        messages = []
        prev_msg = None
        buffer = ''
        conversation_id = -1  # Start from -1 so first increment gives 0

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line is the start of a new message
            if re.match(self.message_pattern, line) or re.match(self.system_msg_pattern, line):
                # Process the previous buffered message
                if buffer:
                    msg = self.extract_message(buffer)
                    if msg:
                        # Check for conversation breaks
                        if self.detect_conversation_break(msg, prev_msg):
                            conversation_id += 1
                            self.conversations.append([])
                        msg['conversation_id'] = conversation_id
                        self.conversations[-1].append(msg)
                        messages.append(msg)
                        prev_msg = msg
                buffer = line  # Start buffering the new message
            else:
                # Continuation of the previous message
                buffer += f' {line}'

        # Process the last buffered message
        if buffer:
            msg = self.extract_message(buffer)
            if msg:
                if self.detect_conversation_break(msg, prev_msg):
                    conversation_id += 1
                    self.conversations.append([])
                msg['conversation_id'] = conversation_id
                self.conversations[-1].append(msg)
                messages.append(msg)

        # Create DataFrame
        df = pd.DataFrame(messages)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['username'] = df['username'].fillna('UNKNOWN')
            df['message'] = df['message'].fillna('')
            df['type'] = df['type'].fillna('text')
            df['conversation_id'] = df['conversation_id'].fillna(0).astype(int)
        else:
            df = pd.DataFrame(columns=['timestamp', 'username', 'message', 'type', 'conversation_id'])

        return df

    def get_user_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate per-user statistics"""
        stats = {}
        for user in df['username'].unique():
            user_msgs = df[df['username'] == user]
            if user_msgs.empty:
                continue
            stats[user] = {
                'message_count': len(user_msgs),
                'avg_message_length': user_msgs['message'].str.len().mean(),
                'most_active_hour': user_msgs['timestamp'].dt.hour.mode().iloc[0] if not user_msgs['timestamp'].dt.hour.mode().empty else None,
                'first_message': user_msgs['timestamp'].min(),
                'last_message': user_msgs['timestamp'].max()
            }
        return stats
