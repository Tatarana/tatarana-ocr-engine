import pandas as pd
import io
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CSVGenerator:
    """Service for generating CSV files from extracted data."""
    
    @staticmethod
    def create_csv_from_llm_response(llm_response: str) -> str:
        """Create CSV content from LLM response."""
        try:
            # Try to parse as CSV directly
            if llm_response.strip().startswith('date,'):
                # Already in CSV format
                csv_content = llm_response
            else:
                # Try to extract CSV from response
                lines = llm_response.split('\n')
                csv_lines = []
                
                for line in lines:
                    if line.strip() and ',' in line:
                        csv_lines.append(line.strip())
                
                if csv_lines:
                    csv_content = '\n'.join(csv_lines)
                else:
                    # Fallback: create basic structure
                    csv_content = "date,description,amount,balance,category\nNo data extracted,,,\n"
            
            # Validate and clean CSV
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Ensure required columns exist
            required_columns = ['date', 'description', 'amount']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Add missing optional columns
            optional_columns = ['balance', 'category', 'installments']
            for col in optional_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Reorder columns
            column_order = ['date', 'description', 'amount', 'balance', 'category', 'installments']
            df = df.reindex(columns=[col for col in column_order if col in df.columns])
            
            # Convert to CSV with UTF-8 BOM for Excel compatibility
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_content = csv_buffer.getvalue()
            
            logger.info(f"Generated CSV with {len(df)} rows")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error creating CSV from LLM response: {e}")
            # Return basic CSV structure
            return "date,description,amount,balance,category,installments\nError processing data,,,\n"
    
    @staticmethod
    def create_csv_from_transactions(transactions: List[Dict[str, Any]]) -> str:
        """Create CSV content from list of transaction dictionaries."""
        try:
            if not transactions:
                return "date,description,amount,balance,category,installments\nNo transactions found,,,\n"
            
            df = pd.DataFrame(transactions)
            
            # Ensure required columns
            required_columns = ['date', 'description', 'amount']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Add missing optional columns
            optional_columns = ['balance', 'category', 'installments']
            for col in optional_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Reorder columns
            column_order = ['date', 'description', 'amount', 'balance', 'category', 'installments']
            df = df.reindex(columns=[col for col in column_order if col in df.columns])
            
            # Convert to CSV with UTF-8 BOM
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_content = csv_buffer.getvalue()
            
            logger.info(f"Generated CSV with {len(df)} transactions")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error creating CSV from transactions: {e}")
            return "date,description,amount,balance,category,installments\nError processing transactions,,,\n"
    
    @staticmethod
    def generate_filename(bank: str, document_type: str, original_filename: str = None) -> str:
        """Generate appropriate CSV filename."""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if original_filename:
            base_name = original_filename.rsplit('.', 1)[0]
        else:
            base_name = f"{bank}_{document_type}"
        
        return f"{base_name}_extracted_{timestamp}.csv"
