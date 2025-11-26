/**
 * Autoship Agent Request Staggering and Retry Logic
 * 
 * This module provides sophisticated request staggering for the Chewy Autoship Agent
 * to prevent overwhelming the backend services and improve reliability when processing
 * large batches of autoship modifications, cancellations, or subscriptions.
 * 
 * Key Use Cases:
 * - Bulk autoship subscription updates across multiple SKUs
 * - Mass autoship cancellations during account cleanup
 * - Frequency adjustments for customer preference changes
 * - Retry logic for failed autoship API calls
 * - Load distribution during peak traffic periods
 * 
 * Integration with Chewy Agent:
 * - Use with chewy_agent.py for autoship-related button clicks
 * - Implement in data_driven_tester.py for bulk autoship testing
 * - Apply to hyperlink_automation.py for autoship URL generation
 */

// Query parameter constants for experiment overrides
const QUERY_PARAM_NAME_KEY = 'expName';
const QUERY_PARAM_VARIATION_KEY = 'expVar';
const COOKIE_PREFIX = 'chewy_exp_';

/**
 * Policy configuration for autoship agent request staggering
 */
interface RetryPolicy {
  strategy: 'exponential' | 'linear';
  baseDelayMs: number;
  maxDelayMs?: number;
  jitter: boolean;
  maxRetries?: number;
}

/**
 * Autoship request context for tracking agent operations
 */
interface AutoshipRequestContext {
  customerId: string;
  subscriptionId?: string;
  operation: 'create' | 'update' | 'cancel' | 'frequency_change' | 'pause' | 'resume';
  attempt: number;
  pageType: string; // For integration with chewy_agent.py page types
}

/**
 * Gets URL Experiment Overrides for AB Testing Autoship Features
 * 
 * This function integrates with Chewy's experimentation framework to allow
 * the autoship agent to participate in A/B tests for new autoship features.
 * 
 * Examples:
 * - Testing new autoship signup flows
 * - A/B testing autoship frequency options
 * - Experiment with autoship cancellation UX
 * 
 * @param cookiesValue - Cookie header string from browser automation
 * @param query - URL search parameters from agent navigation
 * @returns Experiment overrides object for autoship feature flags
 */
export const getExperimentOverrides = (cookiesValue: string, query: URLSearchParams) => {
  // Allow autoship agent to opt into experimental features via URL params
  // This overrides Optimizely experiment values with values from cookies
  const cookieOverrides: Record<string, string> = {};
  
  cookiesValue.split(';').forEach((cookie) => {
    const [name, ...rest] = cookie.trim().split('=');
    if (name.startsWith(COOKIE_PREFIX)) {
      const sanitizedCookieName = name.replace(COOKIE_PREFIX, '');
      const value = rest.join('=');
      if (value) cookieOverrides[sanitizedCookieName] = value;
    }
  });

  let experimentOverrides = Object.keys(cookieOverrides).length
    ? { ...cookieOverrides }
    : undefined;

  // Further override experiment values with query parameters
  // Useful when agent needs to test specific autoship experiment variations
  const urlExperimentOverrides = {
    urlExperimentName: query.get(QUERY_PARAM_NAME_KEY) ?? '',
    urlExperimentVariation: query.get(QUERY_PARAM_VARIATION_KEY) ?? '',
  };
  
  if (urlExperimentOverrides.urlExperimentName && urlExperimentOverrides.urlExperimentVariation) {
    experimentOverrides = {
      ...experimentOverrides,
      [urlExperimentOverrides.urlExperimentName]: urlExperimentOverrides.urlExperimentVariation,
    };
  }

  return experimentOverrides
    ? Object.fromEntries(Object.entries(experimentOverrides).filter(([, v]) => v !== '')) // Remove empty values
    : undefined;
};

/**
 * Computes backoff delay for autoship agent requests
 * 
 * This function calculates intelligent delays between autoship operations to:
 * 1. Prevent rate limiting from Chewy's autoship API
 * 2. Avoid overwhelming the subscription management system
 * 3. Distribute load during bulk autoship operations
 * 4. Implement retry logic for failed autoship modifications
 * 
 * Strategy Examples:
 * - Exponential: 100ms, 200ms, 400ms, 800ms (good for retries)
 * - Linear: 100ms, 200ms, 300ms, 400ms (good for bulk operations)
 * 
 * @param policy - Retry policy configuration for autoship operations
 * @param attempt - Current attempt number (0-based)
 * @returns Delay in milliseconds before next autoship request
 */
export function computeBackoffDelay(
  policy: RetryPolicy,
  attempt: number
): number {
  const { strategy, baseDelayMs, maxDelayMs, jitter } = policy;

  // Calculate base delay based on strategy
  let delay =
    strategy === 'exponential'
      ? baseDelayMs * Math.pow(2, attempt)  // Exponential: 100ms → 200ms → 400ms → 800ms
      : baseDelayMs * (attempt + 1);        // Linear: 100ms → 200ms → 300ms → 400ms

  // Cap delay at maximum if specified
  if (maxDelayMs) delay = Math.min(delay, maxDelayMs);
  
  // Add jitter to prevent thundering herd effects
  // When multiple agent instances run simultaneously
  if (jitter) {
    const jitterFactor = 0.8 + Math.random() * 0.4; // Random between 0.8 and 1.2
    delay = delay * jitterFactor;
  }

  return delay;
}

/**
 * Legacy backoff computation for backwards compatibility
 * Used by older autoship agent implementations
 */
export function computeBackoff(policy: any, attempt: number): number {
  const { strategy, baseDelayMs, maxDelayMs, jitter } = policy;
  let delay = strategy === 'exponential'
    ? baseDelayMs * Math.pow(2, attempt)
    : baseDelayMs * (attempt + 1);
  if (maxDelayMs) delay = Math.min(delay, maxDelayMs);
  if (jitter) delay = delay * (0.8 + Math.random() * 0.4);
  return delay;
}

/**
 * Autoship Agent Request Staggerer Class
 * 
 * Manages intelligent request distribution for autoship operations
 * Integrates with the existing Chewy automation agent framework
 */
export class AutoshipRequestStaggerer {
  private policy: RetryPolicy;
  private activeRequests: Map<string, AutoshipRequestContext> = new Map();

  constructor(policy: RetryPolicy) {
    this.policy = policy;
  }

  /**
   * Executes an autoship operation with intelligent staggering
   * 
   * Example integration with chewy_agent.py:
   * ```python
   * # In chewy_agent.py execute_event method
   * if event_data.get('operation') == 'autoship_bulk_update':
   *     # Call this TypeScript staggerer via Node.js subprocess
   *     delay_ms = await staggerer.getNextDelay(context)
   *     await asyncio.sleep(delay_ms / 1000)
   * ```
   */
  async executeWithStagger<T>(
    context: AutoshipRequestContext,
    operation: () => Promise<T>
  ): Promise<T> {
    const requestKey = `${context.customerId}-${context.operation}`;
    
    // Check if we need to wait based on previous requests
    if (this.activeRequests.has(requestKey)) {
      const existingContext = this.activeRequests.get(requestKey)!;
      const delay = this.computeBackoffDelay(this.policy, existingContext.attempt);
      
      console.log(`[Autoship Agent] Staggering ${context.operation} request for customer ${context.customerId} by ${delay}ms`);
      await this.sleep(delay);
    }

    // Track this request
    this.activeRequests.set(requestKey, context);

    try {
      const result = await operation();
      
      // Clean up successful request
      this.activeRequests.delete(requestKey);
      return result;
    } catch (error) {
      // Handle failed autoship operation
      console.error(`[Autoship Agent] Operation ${context.operation} failed for customer ${context.customerId}:`, error);
      
      // Increment attempt count for retry logic
      const updatedContext = { ...context, attempt: context.attempt + 1 };
      this.activeRequests.set(requestKey, updatedContext);
      
      // Check if we should retry
      if (this.policy.maxRetries && context.attempt >= this.policy.maxRetries) {
        this.activeRequests.delete(requestKey);
        throw new Error(`Max retries (${this.policy.maxRetries}) exceeded for autoship ${context.operation}`);
      }
      
      throw error;
    }
  }

  /**
   * Gets the next recommended delay for an autoship operation
   * Useful for external integration with Python automation agent
   */
  public getNextDelay(context: AutoshipRequestContext): number {
    return this.computeBackoffDelay(this.policy, context.attempt);
  }

  /**
   * Sleep utility for async delay
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Predefined autoship staggering policies for common scenarios
 */
export const AutoshipPolicies = {
  // For bulk autoship subscription updates (gentle approach)
  BULK_SUBSCRIPTION_UPDATE: {
    strategy: 'linear' as const,
    baseDelayMs: 500,
    maxDelayMs: 5000,
    jitter: true,
    maxRetries: 3
  },

  // For individual autoship modifications (quick with retries)
  SINGLE_MODIFICATION: {
    strategy: 'exponential' as const,
    baseDelayMs: 100,
    maxDelayMs: 2000,
    jitter: true,
    maxRetries: 5
  },

  // For autoship cancellations (moderate approach)
  CANCELLATION: {
    strategy: 'linear' as const,
    baseDelayMs: 300,
    maxDelayMs: 3000,
    jitter: true,
    maxRetries: 3
  },

  // For frequency changes (balanced approach)
  FREQUENCY_CHANGE: {
    strategy: 'exponential' as const,
    baseDelayMs: 200,
    maxDelayMs: 4000,
    jitter: true,
    maxRetries: 4
  },

  // For high-volume testing scenarios
  LOAD_TEST: {
    strategy: 'linear' as const,
    baseDelayMs: 50,
    maxDelayMs: 1000,
    jitter: true,
    maxRetries: 2
  }
};

/**
 * Example usage with Chewy Agent automation:
 * 
 * ```typescript
 * // Initialize staggerer for bulk autoship updates
 * const staggerer = new AutoshipRequestStaggerer(AutoshipPolicies.BULK_SUBSCRIPTION_UPDATE);
 * 
 * // Example autoship context from agent
 * const context: AutoshipRequestContext = {
 *   customerId: "12345",
 *   subscriptionId: "sub_67890",
 *   operation: "frequency_change",
 *   attempt: 0,
 *   pageType: "account" // Matches chewy_page_types.csv
 * };
 * 
 * // Execute with intelligent staggering
 * await staggerer.executeWithStagger(context, async () => {
 *   // This would be the actual autoship API call or browser automation
 *   console.log(`Updating autoship frequency for ${context.customerId}`);
 *   return { success: true };
 * });
 * ```
 * 
 * Integration with chewy_agent.py hyperlink automation:
 * 
 * ```
 * http://localhost:5000/execute?data=<encoded_json>&env=dev&type=autoship_bulk
 * 
 * Where encoded_json contains:
 * {
 *   "page_type": "account",
 *   "event": "Autoship Bulk Update",
 *   "properties": {
 *     "operation": "frequency_change",
 *     "customer_ids": ["12345", "67890"],
 *     "stagger_policy": "BULK_SUBSCRIPTION_UPDATE"
 *   }
 * }
 * ```
 */

export default {
  AutoshipRequestStaggerer,
  AutoshipPolicies,
  computeBackoffDelay,
  computeBackoff,
  getExperimentOverrides
};