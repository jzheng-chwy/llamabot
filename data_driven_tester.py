#!/usr/bin/env python3
"""
Data-Driven Agent Testing
Combines real Segment event analysis with Chewy automation agent testing
"""

import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from event_analyzer import EventAnalyzer
from chewy_agent import ChewyAutomationAgent

class DataDrivenTester:
    """Orchestrates data analysis and agent testing"""
    
    def __init__(self, environment: str = "dev"):
        self.analyzer = EventAnalyzer()
        self.agent = ChewyAutomationAgent(environment=environment)
        self.test_results = []
    
    def run_data_driven_tests(self, days_back: int = 2) -> Dict[str, Any]:
        """Run comprehensive data-driven testing"""
        
        print("="*80)
        print("CHEWY DATA-DRIVEN AUTOMATION TESTING")
        print("="*80)
        
        try:
            # 1. Extract and analyze real events
            print("\\n1. EXTRACTING REAL USER EVENTS")
            print("-" * 40)
            events_df = self.analyzer.extract_test_events(days_back=days_back)
            print(f"✅ Extracted {len(events_df)} real events from {days_back} days ago")
            
            # 2. Analyze event patterns
            print("\\n2. ANALYZING EVENT PATTERNS")
            print("-" * 40)
            patterns_df = self.analyzer.analyze_event_patterns()
            print(f"✅ Found {len(patterns_df)} unique event patterns")
            print("\\nTop event patterns:")
            for _, row in patterns_df.head(5).iterrows():
                print(f"  - {row['key_path']}: {row['frequency']} occurrences")
            
            # 3. Get page type distribution
            print("\\n3. PAGE TYPE DISTRIBUTION")
            print("-" * 40)
            page_types_df = self.analyzer.get_page_type_distribution()
            print(f"✅ Found {len(page_types_df)} unique page types")
            print("\\nTop page types:")
            for _, row in page_types_df.head(5).iterrows():
                print(f"  - {row['page_type']}: {row['event_count']} events, {row['session_count']} sessions")
            
            # 4. Generate test scenarios based on real data
            print("\\n4. GENERATING TEST SCENARIOS")
            print("-" * 40)
            scenarios = self.analyzer.generate_test_scenarios(top_n=10)
            print(f"✅ Generated {len(scenarios)} test scenarios")
            
            # 5. Execute agent tests on real-world scenarios
            print("\\n5. EXECUTING AGENT TESTS")
            print("-" * 40)
            
            test_results = []
            for i, scenario in enumerate(scenarios[:6], 1):  # Test first 6 scenarios
                print(f"\\n--- Test {i}/6: {scenario['name']} ---")
                
                try:
                    result = self.agent.execute_event(scenario['event'])
                    success = result['status'] == 'success'
                    
                    test_result = {
                        'scenario_name': scenario['name'],
                        'page_type': scenario['event']['properties']['page_type'],
                        'event_type': result.get('event', 'Unknown'),
                        'success': success,
                        'duration_seconds': result.get('duration_seconds', 0),
                        'hour_completed': result.get('hour'),
                        'result_summary': result.get('result', '')[:100],
                        'error': result.get('error', '') if not success else None
                    }
                    
                    test_results.append(test_result)
                    
                    status_icon = "✅" if success else "❌"
                    print(f"{status_icon} {scenario['name']}: {result.get('result', 'No result')[:80]}...")
                    
                except Exception as e:
                    print(f"❌ Test failed with exception: {str(e)}")
                    test_results.append({
                        'scenario_name': scenario['name'],
                        'page_type': scenario['event']['properties']['page_type'],
                        'success': False,
                        'error': str(e)
                    })
            
            # 6. Create feature vectors from real events
            print("\\n6. CREATING FEATURE VECTORS")
            print("-" * 40)
            feature_summary = self.analyzer.create_feature_vectors()
            print(f"✅ Created feature vectors")
            print(feature_summary)
            
            # 7. Generate comprehensive report
            print("\\n7. GENERATING REPORT")
            print("-" * 40)
            
            success_rate = len([r for r in test_results if r['success']]) / len(test_results) * 100
            avg_duration = sum([r.get('duration_seconds', 0) for r in test_results]) / len(test_results)
            
            report = {
                'test_summary': {
                    'total_tests': len(test_results),
                    'successful_tests': len([r for r in test_results if r['success']]),
                    'success_rate_percent': round(success_rate, 2),
                    'average_duration_seconds': round(avg_duration, 2),
                    'test_timestamp': datetime.now().isoformat()
                },
                'data_analysis': {
                    'events_analyzed': len(events_df),
                    'event_patterns_found': len(patterns_df),
                    'page_types_found': len(page_types_df),
                    'feature_summary': feature_summary.to_dict('records')[0] if not feature_summary.empty else {}
                },
                'test_results': test_results,
                'top_page_types': page_types_df.head(10).to_dict('records'),
                'top_patterns': patterns_df.head(10).to_dict('records')
            }
            
            # Save report
            report_filename = f"chewy_agent_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"✅ Report saved to {report_filename}")
            
            # 8. Print summary
            print("\\n" + "="*80)
            print("TEST EXECUTION SUMMARY")
            print("="*80)
            print(f"📊 Tests Run: {len(test_results)}")
            print(f"✅ Successful: {len([r for r in test_results if r['success']])}")
            print(f"❌ Failed: {len([r for r in test_results if not r['success']])}")
            print(f"📈 Success Rate: {success_rate:.1f}%")
            print(f"⏱️  Average Duration: {avg_duration:.2f} seconds")
            print(f"📋 Report: {report_filename}")
            print("="*80)
            
            return report
            
        except Exception as e:
            print(f"❌ Data-driven testing failed: {str(e)}")
            raise
        finally:
            self.analyzer.close()
    
    def test_specific_page_types(self, page_types: List[str]) -> Dict[str, Any]:
        """Test specific page types with various event types"""
        
        print(f"\\n🎯 Testing specific page types: {', '.join(page_types)}")
        
        test_results = []
        event_templates = [
            {
                "event": "Navigation Clicked",
                "properties": {
                    "eventCategory": "mini-cart",
                    "eventAction": "click", 
                    "eventLabel": "mini-cart"
                }
            },
            {
                "event": "Button Clicked",
                "properties": {
                    "eventCategory": "header-icon",
                    "eventAction": "click",
                    "eventLabel": "search-icon"
                }
            },
            {
                "event": "tab",
                "properties": {}
            }
        ]
        
        for page_type in page_types:
            for template in event_templates:
                event_data = template.copy()
                event_data["properties"]["page_type"] = page_type
                
                try:
                    result = self.agent.execute_event(event_data)
                    test_results.append({
                        'page_type': page_type,
                        'event_type': template['event'],
                        'success': result['status'] == 'success',
                        'duration': result.get('duration_seconds', 0),
                        'result': result.get('result', '')
                    })
                    
                    status = "✅" if result['status'] == 'success' else "❌"
                    print(f"{status} {page_type} + {template['event']}")
                    
                except Exception as e:
                    print(f"❌ {page_type} + {template['event']}: {str(e)}")
        
        return test_results


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run data-driven Chewy agent tests')
    parser.add_argument('--environment', choices=['dev', 'qat', 'prod'], default='dev',
                       help='Environment to test against')
    parser.add_argument('--days-back', type=int, default=2,
                       help='Days back to analyze events from')
    parser.add_argument('--specific-pages', nargs='+',
                       help='Test specific page types only')
    
    args = parser.parse_args()
    
    tester = DataDrivenTester(environment=args.environment)
    
    if args.specific_pages:
        # Test specific page types
        results = tester.test_specific_page_types(args.specific_pages)
        print(f"\\nTested {len(results)} scenarios")
    else:
        # Full data-driven testing
        report = tester.run_data_driven_tests(days_back=args.days_back)
        print(f"\\n🎉 Data-driven testing completed!")


if __name__ == "__main__":
    main()