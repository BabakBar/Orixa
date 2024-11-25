"""Preprocessor for Google Analytics 4 data."""
import pandas as pd
from typing import List, Dict, Any

class GA4Preprocessor:
    """Handles preprocessing of GA4 data exports."""
    
    @staticmethod
    def flatten_event_params(df: pd.DataFrame) -> pd.DataFrame:
        """
        Flatten the event_params nested structure into columns.
        
        Args:
            df: DataFrame containing GA4 data with event_params
            
        Returns:
            DataFrame with flattened event parameters
        """
        # Create a copy to avoid modifying original
        processed_df = df.copy()
        
        # Extract event parameter columns
        param_columns = [col for col in df.columns if col.startswith('event_params')]
        
        # Create dictionary to store parameter values
        param_values: Dict[str, List[Any]] = {}
        
        # Process each row
        for idx in df.index:
            # Get parameter key and values
            key = df.at[idx, 'event_params.key'] if 'event_params.key' in df.columns else None
            
            # Skip if no key
            if pd.isna(key):
                continue
                
            # Get values from different value columns
            value = None
            for val_type in ['string_value', 'int_value', 'float_value', 'double_value']:
                col_name = f'event_params.value.{val_type}'
                if col_name in df.columns and pd.notna(df.at[idx, col_name]):
                    value = df.at[idx, col_name]
                    break
            
            # Store in parameter values
            if key not in param_values:
                param_values[key] = [None] * len(df)
            param_values[key][idx] = value
        
        # Add parameter columns to processed DataFrame
        for key, values in param_values.items():
            processed_df[f'param_{key}'] = values
            
        # Drop original parameter columns
        processed_df.drop(columns=[col for col in param_columns if col in processed_df.columns], inplace=True)
        
        return processed_df
    
    @staticmethod
    def process_sessions(df: pd.DataFrame) -> pd.DataFrame:
        """
        Process session-related data.
        
        Args:
            df: DataFrame containing GA4 data
            
        Returns:
            DataFrame with added session metrics
        """
        # Create copy for processing
        processed_df = df.copy()
        
        # Extract ga_session_id from params if it exists
        if 'param_ga_session_id' in processed_df.columns:
            processed_df['ga_session_id'] = processed_df['param_ga_session_id']
        
        # Sort by user and timestamp
        if 'user_pseudo_id' in processed_df.columns and 'event_timestamp' in processed_df.columns:
            processed_df.sort_values(['user_pseudo_id', 'event_timestamp'], inplace=True)
            
            # Calculate time between events
            processed_df['time_to_next'] = processed_df.groupby('user_pseudo_id')['event_timestamp'].diff(-1)
        
        # Mark session starts
        if 'event_name' in processed_df.columns:
            session_starts = processed_df['event_name'] == 'session_start'
            processed_df['is_session_start'] = session_starts
        
        return processed_df
    
    @staticmethod
    def extract_page_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and process page-related data.
        
        Args:
            df: DataFrame containing GA4 data
            
        Returns:
            DataFrame with processed page data
        """
        # Create copy for processing
        processed_df = df.copy()
        
        # Extract page views if event_name exists
        if 'event_name' in processed_df.columns:
            page_views = processed_df['event_name'] == 'page_view'
            processed_df['is_page_view'] = page_views
        
        # Get page paths from params
        if 'param_page_location' in processed_df.columns:
            processed_df['page_path'] = processed_df['param_page_location'].apply(
                lambda x: str(x).split('?')[0] if pd.notna(x) else ''
            )
        
        return processed_df
    
    @staticmethod
    def process_traffic_sources(df: pd.DataFrame) -> pd.DataFrame:
        """
        Process traffic source data.
        
        Args:
            df: DataFrame containing GA4 data
            
        Returns:
            DataFrame with processed traffic source data
        """
        # Create copy for processing
        processed_df = df.copy()
        
        # Combine source and medium if they exist
        source_col = 'traffic_source.source'
        medium_col = 'traffic_source.medium'
        
        if source_col in processed_df.columns and medium_col in processed_df.columns:
            processed_df['source_medium'] = processed_df.apply(
                lambda row: f"{row.get(source_col, '(none)')} / {row.get(medium_col, '(none)')}", 
                axis=1
            )
        
        return processed_df
    
    @staticmethod
    def preprocess_ga4_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Main preprocessing function for GA4 data.
        
        Args:
            df: Raw GA4 data DataFrame
            
        Returns:
            Preprocessed DataFrame ready for analysis
        """
        # Apply preprocessing steps safely
        processed_df = df.copy()
        
        try:
            processed_df = GA4Preprocessor.flatten_event_params(processed_df)
        except Exception as e:
            print(f"Warning: Error in flatten_event_params: {e}")
        
        try:
            processed_df = GA4Preprocessor.process_sessions(processed_df)
        except Exception as e:
            print(f"Warning: Error in process_sessions: {e}")
        
        try:
            processed_df = GA4Preprocessor.extract_page_data(processed_df)
        except Exception as e:
            print(f"Warning: Error in extract_page_data: {e}")
        
        try:
            processed_df = GA4Preprocessor.process_traffic_sources(processed_df)
        except Exception as e:
            print(f"Warning: Error in process_traffic_sources: {e}")
        
        return processed_df
