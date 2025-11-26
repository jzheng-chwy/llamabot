"""
Event Data Analysis Module for Chewy Agent
Integrates with Snowflake to analyze real user events and generate test scenarios
"""

import json
import pandas as pd
import snowflake.connector
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class EventAnalyzer:
    """Analyzes real user events to inform agent testing strategies"""
    
    def __init__(self):
        self.conn = self._get_snowflake_connection()
    
    def _get_snowflake_connection(self):
        """Establish Snowflake connection"""
        return snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
    
    def extract_test_events(self, days_back: int = 2, limit: int = 10000) -> pd.DataFrame:
        """Extract real events from Segment data"""
        query = f"""
        create or replace local temp table ecom_sandbox.test_events as 
        select
            event_id
            ,session_id
            ,event_timestamp
            ,properties
        from
            segment.segment_hits
        where
            session_date_est = current_date-{days_back}
            and not is_bot
            and bot_type = 'Not Bot'
            and dw_site_id = 10
        limit {limit}
        ;
        
        select * from ecom_sandbox.test_events limit 1000;
        """
        
        return pd.read_sql(query, self.conn)
    
    def analyze_event_patterns(self) -> Dict[str, Any]:
        """Analyze flattened event properties to understand user behavior patterns"""
        
        # Create flattened event structure
        flatten_query = """
        create or replace local temp table ecom_sandbox.init_flatten as
        SELECT
            session_id
            ,event_id
            ,event_timestamp
            ,LOWER( REGEXP_REPLACE(f.path::string, '\\[\\d+\\]', '[]') ) AS key_path
            ,f.key::string AS key_name
            ,f.value AS v
            ,TYPEOF(f.value) AS vtype
        FROM 
            ecom_sandbox.test_events e,
            LATERAL FLATTEN(INPUT => e.properties, RECURSIVE => TRUE) f
        ;
        """
        
        # Execute flattening
        self.conn.cursor().execute(flatten_query)
        
        # Analyze patterns
        analysis_query = """
        SELECT 
            key_path,
            key_name,
            vtype,
            COUNT(*) as frequency,
            COUNT(DISTINCT session_id) as unique_sessions,
            CASE 
                WHEN vtype = 'VARCHAR' THEN COUNT(DISTINCT v::string)
                ELSE COUNT(DISTINCT v)
            END as unique_values
        FROM ecom_sandbox.init_flatten
        WHERE vtype IN ('VARCHAR','BOOLEAN','INTEGER','DECIMAL')
        GROUP BY key_path, key_name, vtype
        ORDER BY frequency DESC
        LIMIT 100
        """
        
        return pd.read_sql(analysis_query, self.conn)
    
    def get_page_type_distribution(self) -> pd.DataFrame:
        """Get distribution of page_type values from real events"""
        query = """
        SELECT 
            LOWER(v::string) as page_type,
            COUNT(*) as event_count,
            COUNT(DISTINCT session_id) as session_count
        FROM ecom_sandbox.init_flatten
        WHERE key_name ILIKE '%page_type%'
            AND vtype = 'VARCHAR'
            AND v IS NOT NULL
        GROUP BY LOWER(v::string)
        ORDER BY event_count DESC
        """
        
        return pd.read_sql(query, self.conn)
    
    def generate_test_scenarios(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Generate agent test scenarios based on real event patterns"""
        
        # Get most common event patterns
        patterns = self.analyze_event_patterns().head(top_n)
        page_types = self.get_page_type_distribution().head(10)
        
        test_scenarios = []
        
        for _, row in page_types.iterrows():
            page_type = row['page_type']
            
            # Create different event type scenarios for each page type
            scenarios = [
                {
                    "name": f"Navigation Click on {page_type}",
                    "event": {
                        "event": "Navigation Clicked",
                        "properties": {
                            "page_type": page_type,
                            "eventCategory": "mini-cart",
                            "eventAction": "click",
                            "eventLabel": "mini-cart"
                        }
                    }
                },
                {
                    "name": f"Button Click on {page_type}",
                    "event": {
                        "event": "Button Clicked", 
                        "properties": {
                            "page_type": page_type,
                            "eventCategory": "header-icon",
                            "eventAction": "click",
                            "eventLabel": "search-icon"
                        }
                    }
                },
                {
                    "name": f"Tab Navigation on {page_type}",
                    "event": {
                        "event": "tab",
                        "properties": {
                            "page_type": page_type
                        }
                    }
                },
                {
                    "name": f"Element View on {page_type}",
                    "event": {
                        "event": "Element Viewed",
                        "properties": {
                            "page_type": page_type,
                            "eventCategory": "mini-cart",
                            "eventAction": "view",
                            "eventLabel": "cart-summary"
                        }
                    }
                }
            ]
            
            test_scenarios.extend(scenarios)
        
        return test_scenarios
    
    def create_feature_vectors(self):
        """Create ML-ready feature vectors using your hashing approach"""
        
        # Execute your full feature engineering pipeline
        pipeline_queries = [
            # Pre-tokens filtering
            """
            CREATE OR REPLACE TEMP TABLE ecom_sandbox.pre_tokens AS
            WITH leafs AS (
              SELECT *
              FROM ecom_sandbox.init_flatten
              WHERE vtype IN ('VARCHAR','BOOLEAN','NULL_VALUE', 'INTEGER', 'DECIMAL')
            ),
            filtered AS (
              SELECT *
              FROM leafs
              WHERE
                NOT REGEXP_LIKE(key_name, '^(session(_id)?|user(_id)?|visitor(_id)?|uuid|guid|transaction(_id)?|event(_id)?|cookie(_id)?)$','i')
                and not key_name ilike '%id%'
                AND NOT REGEXP_LIKE(key_name, '^(time(stamp)?|date(_?time)?|ts)$', 'i')
                AND (vtype <> 'VARCHAR' OR LENGTH(v::string) <= 50)
            )
            SELECT * FROM filtered
            """,
            
            # Token normalization
            """
            CREATE OR REPLACE TEMP TABLE ecom_sandbox.tokens AS
            WITH norm AS (
              SELECT
                session_id, event_id, event_timestamp, key_path,
                CASE vtype
                  WHEN 'DECIMAL'  THEN TO_VARCHAR(v::int)
                  WHEN 'INTEGER' THEN TO_VARCHAR(v)
                  WHEN 'BOOLEAN' THEN IFF(TO_BOOLEAN(v), 'true', 'false')
                  WHEN 'NULL_VALUE'    THEN '<MISSING>'
                  WHEN 'VARCHAR'  THEN LOWER( REGEXP_REPLACE(v::string, '[?#].*$', '') )
                  ELSE LOWER(v::string)
                END AS val_norm
              FROM ecom_sandbox.pre_tokens
            ),
            clean AS (
              SELECT *,
                IFF(REGEXP_LIKE(val_norm, '^\\\\b[0-9a-f]{16,}\\\\b', 'i'), '<ID>', val_norm) AS val_sanitized
              FROM norm
            )
            SELECT session_id, event_id, event_timestamp, key_path, val_sanitized AS val_str
            FROM clean
            """,
            
            # Feature hashing
            """
            CREATE OR REPLACE TEMP TABLE ecom_sandbox.hashed_features AS
            SELECT
              session_id, event_id, event_timestamp,
              MOD(ABS(HASH(key_path || '=' || val_str, 13)), 1048576) AS dim,
              IFF( BITAND(HASH(key_path || '=' || val_str, 29), 1) = 0, +1.0, -1.0 ) * 1.0 AS val
            FROM ecom_sandbox.tokens
            
            UNION ALL
            
            SELECT
              session_id, event_id, event_timestamp,
              MOD(ABS(HASH(key_path, 13)), 1048576) AS dim,
              IFF( BITAND(HASH(key_path, 29), 1) = 0, +1.0, -1.0 ) * 1.0 AS val
            FROM ecom_sandbox.tokens
            """,
            
            # Final feature aggregation
            """
            CREATE OR REPLACE TEMP TABLE ecom_sandbox.event_features AS
            SELECT
              session_id, event_id, event_timestamp, dim,
              SUM(val) AS value,
              ln(1 + count(*)) * sign(SUM(val)) as log_scaled_count
            FROM ecom_sandbox.hashed_features
            GROUP BY session_id, event_id, event_timestamp, dim
            """
        ]
        
        # Execute pipeline
        cursor = self.conn.cursor()
        for query in pipeline_queries:
            cursor.execute(query)
        
        # Return feature summary
        summary_query = """
        SELECT 
            COUNT(DISTINCT event_id) as total_events,
            COUNT(DISTINCT dim) as total_dimensions,
            AVG(total_features) as avg_features_per_event
        FROM (
            SELECT event_id, COUNT(*) as total_features
            FROM ecom_sandbox.event_features
            GROUP BY event_id
        )
        """
        
        return pd.read_sql(summary_query, self.conn)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Example usage of EventAnalyzer"""
    analyzer = EventAnalyzer()
    
    try:
        print("Extracting test events...")
        events = analyzer.extract_test_events()
        print(f"Extracted {len(events)} events")
        
        print("\\nAnalyzing event patterns...")
        patterns = analyzer.analyze_event_patterns()
        print(f"Found {len(patterns)} unique patterns")
        print(patterns.head())
        
        print("\\nGetting page type distribution...")
        page_types = analyzer.get_page_type_distribution()
        print(page_types.head())
        
        print("\\nGenerating test scenarios...")
        scenarios = analyzer.generate_test_scenarios(top_n=5)
        for scenario in scenarios[:3]:
            print(f"  - {scenario['name']}")
            print(f"    Event: {json.dumps(scenario['event'], indent=2)}")
        
        print("\\nCreating feature vectors...")
        features = analyzer.create_feature_vectors()
        print(features)
        
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()