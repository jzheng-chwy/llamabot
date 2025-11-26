(https://github.com/jzheng-chwy/geminiShoppingAgent_0pageviews)




Chewy Automation Agent
A comprehensive data-driven browser automation framework for Chewy website testing using OpenAI, Playwright, and real user event analysis.

Overview
This project provides an intelligent automation agent that:

Processes JSON events and performs corresponding actions on the Chewy website
Integrates with real user data from Snowflake/Segment for data-driven testing
Supports multiple environments (dev, qat, prod) with 59+ page type mappings
Uses AI-powered decision making via OpenAI for intelligent automation
Features comprehensive search strategies with 27+ element detection methods
📁 Project Structure
🛠️ Core Components
1. ChewyAutomationAgent (chewy_agent.py)
The main automation engine featuring:

27+ search element selectors for robust button/link detection
CSV-driven page type mapping for 59+ Chewy page types
Multi-environment support (dev/qat/prod URL conversion)
OpenAI integration for intelligent decision making
Tab navigation handling for complex UI interactions
Comprehensive error handling and logging
2. EventAnalyzer (event_analyzer.py)
Real user data analysis featuring:

Snowflake integration for Segment event data
Recursive JSON flattening for complex event structures
ML-ready feature engineering with hashing pipeline
Event pattern analysis for test scenario generation
Page type distribution analysis for coverage optimization
3. DataDrivenTester (data_driven_tester.py)
Orchestration framework that:

Combines real data analysis with automation testing
Generates test scenarios from actual user behavior
Provides comprehensive reporting with success/failure metrics
Supports targeted testing of specific page types
📋 Prerequisites
Python 3.11+
OpenAI API Key
Snowflake Access (for data analysis features)
Playwright Browsers installed

