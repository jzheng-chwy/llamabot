#!/usr/bin/env python3
"""
Hyperlink-Driven Automation Interface
Abstracts the entire Chewy automation framework into clickable hyperlinks
"""

import json
import base64
import urllib.parse
from flask import Flask, request, jsonify, render_template_string
from chewy_agent import ChewyAutomationAgent
from datetime import datetime
import traceback

# Optional imports with fallbacks
try:
    from data_driven_tester import DataDrivenTester
    HAS_DATA_TESTER = True
except ImportError:
    HAS_DATA_TESTER = False
    class DataDrivenTester:
        def __init__(self, *args, **kwargs):
            pass
        def run_data_driven_tests(self, *args, **kwargs):
            return {"status": "error", "error": "DataDrivenTester not available. Install requirements_data.txt"}

try:
    from event_analyzer import EventAnalyzer
    HAS_EVENT_ANALYZER = True
except ImportError:
    HAS_EVENT_ANALYZER = False
    class EventAnalyzer:
        def __init__(self, *args, **kwargs):
            pass
        def extract_test_events(self, *args, **kwargs):
            return None
        def analyze_event_patterns(self, *args, **kwargs):
            return None
        def get_page_type_distribution(self, *args, **kwargs):
            return None

app = Flask(__name__)

class HyperlinkAutomationService:
    """Service that converts automation commands into clickable hyperlinks"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.agent = ChewyAutomationAgent()
        
        # Initialize optional components
        if HAS_DATA_TESTER:
            self.data_tester = DataDrivenTester()
        else:
            self.data_tester = DataDrivenTester()  # Fallback class
            
        if HAS_EVENT_ANALYZER:
            self.analyzer = EventAnalyzer()
        else:
            self.analyzer = EventAnalyzer()  # Fallback class
    
    def generate_automation_link(self, event_data, environment="dev", test_type="single"):
        """
        Generate a clickable hyperlink that executes automation
        
        Args:
            event_data: JSON event data to execute
            environment: Target environment (dev/qat/prod)
            test_type: Type of test (single/data_driven/analysis)
        
        Returns:
            Complete hyperlink URL
        """
        # Encode the event data
        encoded_data = base64.b64encode(
            json.dumps(event_data).encode('utf-8')
        ).decode('utf-8')
        
        # Build the automation URL
        params = {
            'data': encoded_data,
            'env': environment,
            'type': test_type
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.base_url}/execute?{query_string}"
    
    def generate_quick_links(self):
        """Generate common automation hyperlinks"""
        
        common_events = [
            {
                "name": "Search Button Click",
                "event": {
                    "page_type": "search",
                    "event": "Button Clicked",
                    "properties": {"button_text": "search"}
                }
            },
            {
                "name": "Account Login",
                "event": {
                    "page_type": "account",
                    "event": "Button Clicked", 
                    "properties": {"button_text": "sign in"}
                }
            },
            {
                "name": "Cart Navigation",
                "event": {
                    "page_type": "cart",
                    "event": "Page Load",
                    "properties": {"action": "view_cart"}
                }
            },
            {
                "name": "Account Tab Switch",
                "event": {
                    "page_type": "account",
                    "event": "Tab",
                    "properties": {"tab_name": "Orders"}
                }
            }
        ]
        
        links = {}
        for item in common_events:
            for env in ["dev", "qat", "prod"]:
                key = f"{item['name']} ({env.upper()})"
                links[key] = self.generate_automation_link(
                    item['event'], 
                    environment=env
                )
        
        return links

# Initialize the service
automation_service = HyperlinkAutomationService()

@app.route('/')
def index():
    """Main dashboard with clickable automation links"""
    
    quick_links = automation_service.generate_quick_links()
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chewy Automation Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c5aa0; border-bottom: 3px solid #2c5aa0; padding-bottom: 10px; }
            h2 { color: #555; margin-top: 30px; }
            .link-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin: 20px 0; }
            .automation-link { 
                display: block; padding: 15px; background: #e8f4fd; border: 2px solid #2c5aa0; 
                border-radius: 8px; text-decoration: none; color: #2c5aa0; font-weight: bold;
                transition: all 0.3s ease; text-align: center;
            }
            .automation-link:hover { background: #2c5aa0; color: white; transform: translateY(-2px); }
            .custom-form { background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            textarea, select, input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: monospace; }
            button { background: #2c5aa0; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
            button:hover { background: #1a4480; }
            .data-driven-section { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0; }
            .analytics-section { background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 20px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Chewy Automation Dashboard</h1>
            <p>Click any link below to execute automation directly in your browser!</p>
            
            <h2>🎯 Quick Action Links</h2>
            <div class="link-grid">
                {% for name, url in quick_links.items() %}
                <a href="{{ url }}" class="automation-link" target="_blank">{{ name }}</a>
                {% endfor %}
            </div>
            
            <div class="data-driven-section">
                <h2>📊 Data-Driven Testing</h2>
                <p>Execute comprehensive testing using real user data from Snowflake/Segment</p>
                <div class="link-grid">
                    <a href="/execute?type=data_driven&env=dev&data=e30=" class="automation-link" target="_blank">
                        📈 Run Data-Driven Tests (DEV)
                    </a>
                    <a href="/execute?type=data_driven&env=qat&data=e30=" class="automation-link" target="_blank">
                        🧪 Run Data-Driven Tests (QAT)
                    </a>
                </div>
            </div>
            
            <div class="analytics-section">
                <h2>🔍 Event Analysis</h2>
                <p>Analyze real user event patterns and generate test scenarios</p>
                <div class="link-grid">
                    <a href="/execute?type=analysis&env=prod&data=eyJkYXlzX2JhY2siOiAyfQ==" class="automation-link" target="_blank">
                        📋 Analyze Events (2 days)
                    </a>
                    <a href="/execute?type=analysis&env=prod&data=eyJkYXlzX2JhY2siOiA3fQ==" class="automation-link" target="_blank">
                        📋 Analyze Events (7 days)
                    </a>
                </div>
            </div>
            
            <h2>⚡ Custom Automation</h2>
            <div class="custom-form">
                <form id="customForm" onsubmit="generateCustomLink(event)">
                    <div class="form-group">
                        <label for="eventJson">Event JSON:</label>
                        <textarea id="eventJson" rows="8" placeholder='{
    "page_type": "search",
    "event": "Button Clicked",
    "properties": {
        "button_text": "search"
    }
}'></textarea>
                    </div>
                    <div class="form-group">
                        <label for="environment">Environment:</label>
                        <select id="environment">
                            <option value="dev">Development</option>
                            <option value="qat">QAT</option>
                            <option value="prod">Production</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="testType">Test Type:</label>
                        <select id="testType">
                            <option value="single">Single Event</option>
                            <option value="data_driven">Data-Driven Testing</option>
                            <option value="analysis">Event Analysis</option>
                        </select>
                    </div>
                    <button type="submit">🔗 Generate Automation Link</button>
                </form>
                <div id="generatedLink" style="margin-top: 20px; display: none;">
                    <h3>Generated Link:</h3>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #dee2e6;">
                        <a id="customLink" href="#" target="_blank" class="automation-link">Click to Execute</a>
                    </div>
                </div>
            </div>
            
            <h2>📖 Usage Guide</h2>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; line-height: 1.6;">
                <h3>How It Works:</h3>
                <ol>
                    <li><strong>Click Quick Links:</strong> Pre-configured automation for common scenarios</li>
                    <li><strong>Custom JSON:</strong> Create your own event JSON and generate a link</li>
                    <li><strong>Environment Selection:</strong> Choose dev/qat/prod for testing</li>
                    <li><strong>Share Links:</strong> Send generated links to anyone for instant automation</li>
                </ol>
                
                <h3>Example JSON Events:</h3>
                <pre style="background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 5px; overflow-x: auto;">
# Button Click
{
    "page_type": "search",
    "event": "Button Clicked",
    "properties": {"button_text": "search"}
}

# Tab Navigation  
{
    "page_type": "account", 
    "event": "Tab",
    "properties": {"tab_name": "Orders"}
}

# Page Load
{
    "page_type": "cart",
    "event": "Page Load",
    "properties": {"action": "view_cart"}
}</pre>
            </div>
        </div>
        
        <script>
            function generateCustomLink(event) {
                event.preventDefault();
                
                const eventJson = document.getElementById('eventJson').value;
                const environment = document.getElementById('environment').value;
                const testType = document.getElementById('testType').value;
                
                try {
                    // Validate JSON
                    JSON.parse(eventJson);
                    
                    // Encode the data
                    const encodedData = btoa(eventJson);
                    
                    // Generate URL
                    const url = `/execute?data=${encodeURIComponent(encodedData)}&env=${environment}&type=${testType}`;
                    
                    // Update the link
                    const linkElement = document.getElementById('customLink');
                    linkElement.href = url;
                    linkElement.textContent = `Execute ${testType} automation on ${environment.toUpperCase()}`;
                    
                    // Show the generated link
                    document.getElementById('generatedLink').style.display = 'block';
                    
                } catch (error) {
                    alert('Invalid JSON: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    
    from jinja2 import Template
    template = Template(html_template)
    return template.render(quick_links=quick_links)

@app.route('/execute')
def execute_automation():
    """Execute automation based on hyperlink parameters"""
    
    try:
        # Decode parameters
        encoded_data = request.args.get('data', '')
        environment = request.args.get('env', 'dev')
        test_type = request.args.get('type', 'single')
        
        # Decode the event data
        try:
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            event_data = json.loads(decoded_data)
        except:
            event_data = {}
        
        # Execute based on test type
        if test_type == 'single':
            # Single event automation
            agent = ChewyAutomationAgent(environment=environment)
            result = agent.execute_event(event_data)
            
        elif test_type == 'data_driven':
            # Data-driven testing
            if not HAS_DATA_TESTER:
                result = {
                    "status": "error",
                    "error": "Data-driven testing not available. Install: pip install -r requirements_data.txt",
                    "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                tester = DataDrivenTester(environment=environment)
                result = tester.run_data_driven_tests(days_back=event_data.get('days_back', 2))
            
        elif test_type == 'analysis':
            # Event analysis only
            if not HAS_EVENT_ANALYZER:
                result = {
                    "status": "error",
                    "error": "Event analysis not available. Install: pip install -r requirements_data.txt",
                    "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                analyzer = EventAnalyzer()
                events_df = analyzer.extract_test_events(days_back=event_data.get('days_back', 2))
                patterns_df = analyzer.analyze_event_patterns()
                page_types_df = analyzer.get_page_type_distribution()
                
                result = {
                    "status": "success",
                    "type": "analysis",
                    "events_extracted": len(events_df) if events_df is not None else 0,
                    "patterns_found": len(patterns_df) if patterns_df is not None else 0,
                    "page_types": len(page_types_df) if page_types_df is not None else 0,
                    "top_patterns": patterns_df.head(10).to_dict('records') if patterns_df is not None and not patterns_df.empty else [],
                    "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        
        else:
            result = {
                "status": "error", 
                "error": f"Unknown test type: {test_type}"
            }
        
        # Return formatted result
        return render_result(result, event_data, environment, test_type)
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return render_result(error_result, {}, environment, test_type)

def render_result(result, event_data, environment, test_type):
    """Render execution results in a nice HTML format"""
    
    result_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Automation Result</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; }
            .info { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; padding: 15px; border-radius: 5px; }
            pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; border: 1px solid #dee2e6; }
            .back-link { display: inline-block; margin-top: 20px; background: #2c5aa0; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
            .back-link:hover { background: #1a4480; color: white; }
            h1 { color: #2c5aa0; }
            .metadata { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Automation Result</h1>
            
            <div class="metadata">
                <h3>Execution Details</h3>
                <p><strong>Environment:</strong> {{ environment|upper }}</p>
                <p><strong>Test Type:</strong> {{ test_type|title }}</p>
                <p><strong>Timestamp:</strong> {{ result.completed_at }}</p>
            </div>
            
            {% if result.status == 'success' %}
            <div class="success">
                <h3>✅ Execution Successful!</h3>
                {% if result.page_navigated_to %}
                <p><strong>Page:</strong> {{ result.page_navigated_to }}</p>
                {% endif %}
                {% if result.actions_performed %}
                <p><strong>Actions:</strong> {{ result.actions_performed|join(', ') }}</p>
                {% endif %}
            </div>
            {% else %}
            <div class="error">
                <h3>❌ Execution Failed</h3>
                <p><strong>Error:</strong> {{ result.error }}</p>
            </div>
            {% endif %}
            
            <h3>📋 Full Result</h3>
            <pre>{{ result_json }}</pre>
            
            {% if event_data %}
            <h3>📝 Input Event Data</h3>
            <pre>{{ event_json }}</pre>
            {% endif %}
            
            <a href="/" class="back-link">← Back to Dashboard</a>
        </div>
    </body>
    </html>
    """
    
    from jinja2 import Template
    template = Template(result_template)
    return template.render(
        result=result,
        environment=environment,
        test_type=test_type,
        result_json=json.dumps(result, indent=2),
        event_data=event_data,
        event_json=json.dumps(event_data, indent=2) if event_data else ""
    )

@app.route('/api/generate-link', methods=['POST'])
def api_generate_link():
    """API endpoint to generate automation links programmatically"""
    
    try:
        data = request.get_json()
        event_data = data.get('event_data', {})
        environment = data.get('environment', 'dev')
        test_type = data.get('test_type', 'single')
        
        link = automation_service.generate_automation_link(
            event_data, environment, test_type
        )
        
        # Build short link parameters
        short_params = {
            'data': base64.b64encode(json.dumps(event_data).encode()).decode(),
            'env': environment,
            'type': test_type
        }
        
        return jsonify({
            "status": "success",
            "automation_link": link,
            "short_link": f"/execute?{urllib.parse.urlencode(short_params)}"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400

if __name__ == '__main__':
    print("🚀 Starting Hyperlink Automation Service...")
    print("📱 Dashboard: http://localhost:5000")
    print("🔗 API: http://localhost:5000/api/generate-link")
    app.run(debug=True, host='0.0.0.0', port=5000)