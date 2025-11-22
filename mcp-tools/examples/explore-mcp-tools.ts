/**
 * Explore Context7 and Sequential Thinking MCP Tools
 *
 * This script demonstrates how to:
 * 1. Connect to MCP servers
 * 2. List available tools
 * 3. Call tools with different parameters
 * 4. View results
 */

import {
  createContext7Client,
  createSequentialThinkingClient,
  createPerplexityClient
} from '../index';

// ============================================
// 1. EXPLORE CONTEXT7 MCP SERVER
// ============================================
async function exploreContext7() {
  console.log('\n════════════════════════════════════════');
  console.log('📚 EXPLORING CONTEXT7 MCP SERVER');
  console.log('════════════════════════════════════════\n');

  const client = createContext7Client();

  // Suppress stderr noise
  client.on('error', (msg) => {
    if (!msg.includes('Context7') && !msg.includes('running on stdio')) {
      console.error('Error:', msg);
    }
  });

  await client.connect();

  // List all available tools
  console.log('📋 Available Tools:');
  const tools = await client.listTools();
  console.log(JSON.stringify(tools, null, 2));

  console.log('\n🔍 Example 1: Resolve Library ID');
  console.log('Query: "fastapi"\n');

  const fastapiLibs = await client.callTool({
    name: 'resolve-library-id',
    arguments: { libraryName: 'fastapi' }
  });
  console.log('Result:', JSON.stringify(fastapiLibs, null, 2));

  console.log('\n🔍 Example 2: Get Library Documentation');
  console.log('Query: FastAPI + "async HTTP requests"\n');

  const fastapiDocs = await client.callTool({
    name: 'get-library-docs',
    arguments: {
      context7CompatibleLibraryID: '/websites/fastapi_tiangolo_com',
      topic: 'async HTTP requests httpx dependencies'
    }
  });
  console.log('Result:', JSON.stringify(fastapiDocs, null, 2));

  console.log('\n🔍 Example 3: Get SQLAlchemy Documentation');
  console.log('Query: SQLAlchemy + "migrations alembic"\n');

  const sqlalchemyLibs = await client.callTool({
    name: 'resolve-library-id',
    arguments: { libraryName: 'sqlalchemy' }
  });
  console.log('Available Libraries:', JSON.stringify(sqlalchemyLibs, null, 2));

  const sqlalchemyDocs = await client.callTool({
    name: 'get-library-docs',
    arguments: {
      context7CompatibleLibraryID: '/websites/docs_sqlalchemy_org',
      topic: 'adding columns migration alembic'
    }
  });
  console.log('Docs Result:', JSON.stringify(sqlalchemyDocs, null, 2));

  client.disconnect();
  console.log('\n✅ Context7 exploration complete!\n');
}

// ============================================
// 2. EXPLORE SEQUENTIAL THINKING MCP SERVER
// ============================================
async function exploreSequentialThinking() {
  console.log('\n════════════════════════════════════════');
  console.log('🧠 EXPLORING SEQUENTIAL THINKING MCP SERVER');
  console.log('════════════════════════════════════════\n');

  const client = createSequentialThinkingClient();

  // Suppress stderr noise
  client.on('error', (msg) => {
    if (!msg.includes('Sequential') && !msg.includes('running on stdio')) {
      console.error('Error:', msg);
    }
  });

  await client.connect();

  // List all available tools
  console.log('📋 Available Tools:');
  const tools = await client.listTools();
  console.log(JSON.stringify(tools, null, 2));

  console.log('\n💭 Example: Multi-step Problem Solving');
  console.log('Problem: "How to optimize WordPress plugin scanning?"\n');

  // Thought 1
  console.log('🔹 Thought 1/3: Initial Analysis');
  const thought1 = await client.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Let me analyze how to optimize WordPress plugin scanning:

1. Current bottlenecks:
   - Sequential file processing (slow for large plugins)
   - Synchronous API calls to deprecation database
   - Full file reads even for small checks

2. Optimization opportunities:
   - Parallel file processing with worker pools
   - Batch API queries instead of one-by-one
   - Stream processing for large files
   - Cache frequently accessed deprecation data

3. Next: Consider implementation approach`,
      thoughtNumber: 1,
      totalThoughts: 3,
      nextThoughtNeeded: true
    }
  });
  console.log('Result:', JSON.stringify(thought1, null, 2));

  // Thought 2
  console.log('\n🔹 Thought 2/3: Implementation Strategy');
  const thought2 = await client.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Implementation strategy for optimization:

1. Parallel Processing:
   - Use asyncio.gather() for concurrent file scanning
   - Worker pool size: CPU cores * 2
   - Limit: 10-20 concurrent files to avoid memory issues

2. Batch API Queries:
   - Collect all function names first
   - Single batch query to deprecation DB
   - Reduces API calls from 100s to 1-2

3. Caching Layer:
   - Redis for deprecation data (TTL: 24h)
   - In-memory LRU cache for hot functions
   - Reduces DB queries by ~80%

4. Next: Identify potential risks`,
      thoughtNumber: 2,
      totalThoughts: 3,
      nextThoughtNeeded: true
    }
  });
  console.log('Result:', JSON.stringify(thought2, null, 2));

  // Thought 3
  console.log('\n🔹 Thought 3/3: Risk Analysis & Conclusion');
  const thought3 = await client.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Risks and final recommendations:

1. Risks:
   - Parallel processing: Higher memory usage
   - Caching: Stale data if deprecation DB updates
   - Complexity: More error handling needed

2. Mitigations:
   - Memory: Process in batches of 50 files
   - Cache: Implement cache invalidation on DB updates
   - Errors: Graceful degradation to sequential mode

3. Expected Performance:
   - Before: 30-60 seconds for 500 files
   - After: 5-10 seconds for 500 files
   - 6x speedup with acceptable complexity

Conclusion: Implement parallel processing first (biggest impact),
then add caching, then optimize batch queries.`,
      thoughtNumber: 3,
      totalThoughts: 3,
      nextThoughtNeeded: false
    }
  });
  console.log('Result:', JSON.stringify(thought3, null, 2));

  client.disconnect();
  console.log('\n✅ Sequential Thinking exploration complete!\n');
}

// ============================================
// 3. EXPLORE PERPLEXITY MCP SERVER
// ============================================
async function explorePerplexity() {
  console.log('\n════════════════════════════════════════');
  console.log('🔬 EXPLORING PERPLEXITY MCP SERVER');
  console.log('════════════════════════════════════════\n');

  const client = createPerplexityClient();

  // Suppress stderr noise
  client.on('error', (msg) => {
    if (!msg.includes('Perplexity') && !msg.includes('running on stdio')) {
      console.error('Error:', msg);
    }
  });

  await client.connect();

  // List all available tools
  console.log('📋 Available Tools:');
  const tools = await client.listTools();
  console.log(JSON.stringify(tools, null, 2));

  console.log('\n🔎 Example 1: Web Search');
  console.log('Query: "EPSS vulnerability scoring best practices 2025"\n');

  const searchResults = await client.callTool({
    name: 'perplexity_search',
    arguments: {
      query: 'EPSS vulnerability scoring best practices 2025',
      max_results: 5
    }
  });
  console.log('Search Results:', JSON.stringify(searchResults, null, 2));

  console.log('\n💬 Example 2: Conversational AI (Ask)');
  console.log('Question: "What are the benefits of EPSS over CVSS?"\n');

  const conversation = await client.callTool({
    name: 'perplexity_ask',
    arguments: {
      messages: [
        {
          role: 'user',
          content: 'What are the key benefits of using EPSS (Exploit Prediction Scoring System) over traditional CVSS scores for vulnerability prioritization?'
        }
      ]
    }
  });
  console.log('AI Response:', JSON.stringify(conversation, null, 2));

  console.log('\n📚 Example 3: Deep Research');
  console.log('Research: "FastAPI async best practices for external API integration"\n');

  const research = await client.callTool({
    name: 'perplexity_research',
    arguments: {
      messages: [
        {
          role: 'user',
          content: 'Research best practices for integrating external REST APIs in FastAPI applications, focusing on async/await patterns, error handling, and retry logic.'
        }
      ],
      strip_thinking: true
    }
  });
  console.log('Research Results:', JSON.stringify(research, null, 2));

  client.disconnect();
  console.log('\n✅ Perplexity exploration complete!\n');
}

// ============================================
// 4. PRACTICAL WORKFLOW EXAMPLE
// ============================================
async function practicalWorkflow() {
  console.log('\n════════════════════════════════════════');
  console.log('🎯 PRACTICAL WORKFLOW: Plan a Feature');
  console.log('Feature: Real-time Webhook Notifications');
  console.log('════════════════════════════════════════\n');

  // Step 1: Use Sequential Thinking to plan
  console.log('📋 Step 1: Plan with Sequential Thinking...\n');
  const thinking = createSequentialThinkingClient();
  thinking.on('error', () => {}); // Suppress noise
  await thinking.connect();

  const plan = await thinking.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Planning webhook notification feature:

1. Requirements:
   - Send alerts to Slack, Discord, email when vulnerabilities detected
   - Support custom HTTP webhooks
   - Retry failed deliveries
   - Log all webhook attempts

2. Tech stack:
   - Celery for async delivery
   - Redis for queue management
   - httpx for HTTP requests
   - Jinja2 for templates

3. Next: Get FastAPI documentation on background tasks`,
      thoughtNumber: 1,
      totalThoughts: 1,
      nextThoughtNeeded: false
    }
  });
  console.log('Plan:', JSON.stringify(plan, null, 2));

  // Step 2: Get documentation from Context7
  console.log('\n📚 Step 2: Get FastAPI docs from Context7...\n');
  const context7 = createContext7Client();
  context7.on('error', () => {}); // Suppress noise
  await context7.connect();

  const fastapiDocs = await context7.callTool({
    name: 'get-library-docs',
    arguments: {
      context7CompatibleLibraryID: '/websites/fastapi_tiangolo_com',
      topic: 'background tasks celery async'
    }
  });
  console.log('FastAPI Docs:', JSON.stringify(fastapiDocs, null, 2));

  // Step 3: Research best practices with Perplexity
  console.log('\n🔬 Step 3: Research webhook best practices...\n');
  const perplexity = createPerplexityClient();
  perplexity.on('error', () => {}); // Suppress noise
  await perplexity.connect();

  const webhookResearch = await perplexity.callTool({
    name: 'perplexity_ask',
    arguments: {
      messages: [
        {
          role: 'user',
          content: 'What are the best practices for implementing webhook delivery systems with retry logic and error handling?'
        }
      ]
    }
  });
  console.log('Research:', JSON.stringify(webhookResearch, null, 2));

  // Cleanup
  thinking.disconnect();
  context7.disconnect();
  perplexity.disconnect();

  console.log('\n✅ Practical workflow complete!\n');
  console.log('📝 Summary:');
  console.log('- Sequential Thinking: Created implementation plan');
  console.log('- Context7: Retrieved FastAPI documentation');
  console.log('- Perplexity: Researched webhook best practices');
  console.log('\nYou now have everything needed to implement the feature! 🚀\n');
}

// ============================================
// MAIN EXECUTION
// ============================================
async function main() {
  console.log('\n╔═══════════════════════════════════════════════╗');
  console.log('║  MCP TOOLS EXPLORATION GUIDE                  ║');
  console.log('║  Context7 + Sequential Thinking + Perplexity  ║');
  console.log('╚═══════════════════════════════════════════════╝\n');

  const choice = process.argv[2] || 'all';

  try {
    switch (choice) {
      case 'context7':
        await exploreContext7();
        break;
      case 'thinking':
        await exploreSequentialThinking();
        break;
      case 'perplexity':
        await explorePerplexity();
        break;
      case 'workflow':
        await practicalWorkflow();
        break;
      case 'all':
      default:
        await exploreContext7();
        await exploreSequentialThinking();
        await explorePerplexity();
        await practicalWorkflow();
        break;
    }

    console.log('\n🎉 All explorations complete!\n');
    console.log('💡 Usage tips:');
    console.log('  - Context7: Get up-to-date library documentation');
    console.log('  - Sequential Thinking: Break down complex problems');
    console.log('  - Perplexity: Research best practices and patterns\n');

  } catch (error) {
    console.error('\n❌ Error during exploration:', error);
    process.exit(1);
  }
}

// Run specific exploration:
// npx tsx mcp-tools/examples/explore-mcp-tools.ts context7
// npx tsx mcp-tools/examples/explore-mcp-tools.ts thinking
// npx tsx mcp-tools/examples/explore-mcp-tools.ts perplexity
// npx tsx mcp-tools/examples/explore-mcp-tools.ts workflow
// npx tsx mcp-tools/examples/explore-mcp-tools.ts all

if (require.main === module) {
  main();
}

export {
  exploreContext7,
  exploreSequentialThinking,
  explorePerplexity,
  practicalWorkflow
};
