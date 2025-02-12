import pandas as pd
import re
from typing import Tuple, List
import urllib.parse

class DataProcessor:
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        # Remove any spaces or special characters
        phone = str(phone).strip()
        phone = re.sub(r'[^0-9]', '', phone)

        # Check if it's a valid length (assuming international format)
        return len(phone) >= 10 and len(phone) <= 15

    @staticmethod
    def validate_file_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate if required columns are present"""
        required_columns = ['Mobile Number', 'Name', 'Message', 'Attachment', 'Time']
        missing_columns = [col for col in required_columns if col not in df.columns]
        return len(missing_columns) == 0, missing_columns

    @staticmethod
    def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean the dataframe"""
        # Create a copy to avoid modifying the original
        df = df.copy()

        # Clean phone numbers
        df['Mobile Number'] = df['Mobile Number'].astype(str).apply(
            lambda x: re.sub(r'[^0-9]', '', str(x))
        )

        # URL decode messages
        df['Message'] = df['Message'].apply(urllib.parse.unquote)

        # Initialize status column
        df['status'] = 'pending'
        df['error_message'] = ''

        return df

    @staticmethod
    def validate_row(row) -> Tuple[bool, str]:
        """Validate a single row of data"""
        if not DataProcessor.validate_phone_number(row['Mobile Number']):
            return False, "Invalid phone number"

        if not row['Message']:
            return False, "Message is empty"

        try:
            float(row['Time'])
        except ValueError:
            return False, "Invalid time delay value"

        return True, ""