/**
 * EPSS Integration Research Script
 *
 * Uses Context7 and Sequential Thinking MCP servers to:
 * 1. Research best practices for EPSS integration
 * 2. Plan the implementation approach
 * 3. Generate implementation guidance
 */

import { createContext7Client, createSequentialThinkingClient, createPerplexityClient } from '../index';

async function researchEPSSIntegration() {
  console.log('🔍 Starting EPSS Integration Research...\n');

  // Step 1: Use Sequential Thinking to break down the problem
  console.log('📋 Step 1: Using Sequential Thinking to plan approach...');
  const thinking = createSequentialThinkingClient();

  // Handle stderr output (ignore server startup messages)
  thinking.on('error', (msg) => {
    if (!msg.includes('running on stdio')) {
      console.error('Error:', msg);
    }
  });

  await thinking.connect();

  const thought1 = await thinking.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Analyzing EPSS integration requirements for a WordPress security scanner:

1. EPSS API Integration:
   - API endpoint: https://api.first.org/data/v1/epss
   - Need to query CVE identifiers
   - Response includes epss score (0-1), percentile, and date
   - No authentication required

2. Key challenges to address:
   - How to map WordPress vulnerabilities to CVE identifiers
   - Caching strategy (API recommends daily refresh)
   - Handling missing CVE data
   - Database schema changes needed

3. Next: Research FastAPI best practices for external API integration`,
      thoughtNumber: 1,
      totalThoughts: 3,
      nextThoughtNeeded: true
    }
  });
  console.log('💭 Thought 1:', JSON.stringify(thought1, null, 2));

  const thought2 = await thinking.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Planning the technical implementation:

1. Backend Architecture:
   - Create service: backend/app/services/epss/epss_service.py
   - Use httpx for async HTTP requests (FastAPI best practice)
   - Implement batch CVE queries (API supports multiple CVEs)
   - Add retry logic with exponential backoff

2. Database Changes:
   - Add columns: epss_score (Float), epss_percentile (Float), epss_updated_at (DateTime)
   - Create Alembic migration
   - Add index on epss_score for efficient sorting

3. Caching Strategy:
   - Use Redis or database-level caching
   - TTL: 24 hours (EPSS updates daily)
   - Background Celery task for daily refresh

4. Next: Research frontend best practices for displaying risk scores`,
      thoughtNumber: 2,
      totalThoughts: 3,
      nextThoughtNeeded: true
    }
  });
  console.log('💭 Thought 2:', JSON.stringify(thought2, null, 2));

  const thought3 = await thinking.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Final implementation plan:

1. Frontend Display:
   - Update ScanResults component to show EPSS score
   - Color-coded badges: 0.8+ (critical), 0.5-0.8 (high), 0.2-0.5 (medium), <0.2 (low)
   - Add sorting by EPSS score
   - Show percentile in tooltip

2. Testing Requirements:
   - Unit tests for EPSS service (mock API responses)
   - Integration tests for end-to-end flow
   - Test error handling (API down, missing CVEs)

3. Implementation Order:
   a) Create EPSS service with API client
   b) Database migration
   c) Update schemas
   d) Integrate into scan workflow
   e) Frontend updates
   f) Background refresh task

This provides a complete, production-ready implementation plan.`,
      thoughtNumber: 3,
      totalThoughts: 3,
      nextThoughtNeeded: false
    }
  });
  console.log('💭 Thought 3:', JSON.stringify(thought3, null, 2));

  thinking.disconnect();

  // Step 2: Use Context7 to get FastAPI and SQLAlchemy best practices
  console.log('\n📚 Step 2: Researching FastAPI best practices with Context7...');
  const context7 = createContext7Client();
  context7.on('error', (msg) => {
    if (!msg.includes('running on stdio') && !msg.includes('Context7')) {
      console.error('Context7 Error:', msg);
    }
  });
  await context7.connect();

  // Resolve FastAPI library
  const fastapiLibs = await context7.callTool({
    name: 'resolve-library-id',
    arguments: { libraryName: 'fastapi' }
  });
  console.log('📦 FastAPI Libraries:', JSON.stringify(fastapiLibs, null, 2));

  // Get FastAPI docs on external API integration
  const fastapiDocs = await context7.callTool({
    name: 'get-library-docs',
    arguments: {
      context7CompatibleLibraryID: '/websites/fastapi_tiangolo_com',
      topic: 'async HTTP requests httpx dependencies'
    }
  });
  console.log('📖 FastAPI HTTP Client Docs:', JSON.stringify(fastapiDocs, null, 2));

  // Get SQLAlchemy docs on migrations
  const sqlalchemyLibs = await context7.callTool({
    name: 'resolve-library-id',
    arguments: { libraryName: 'sqlalchemy' }
  });
  console.log('📦 SQLAlchemy Libraries:', JSON.stringify(sqlalchemyLibs, null, 2));

  const sqlalchemyDocs = await context7.callTool({
    name: 'get-library-docs',
    arguments: {
      context7CompatibleLibraryID: '/websites/docs_sqlalchemy_org',
      topic: 'adding columns migration alembic'
    }
  });
  console.log('📖 SQLAlchemy Migration Docs:', JSON.stringify(sqlalchemyDocs, null, 2));

  context7.disconnect();

  // Step 3: Use Perplexity to research EPSS integration patterns
  console.log('\n🌐 Step 3: Researching EPSS integration patterns with Perplexity...');
  const perplexity = createPerplexityClient();
  perplexity.on('error', (msg) => {
    if (!msg.includes('running on stdio') && !msg.includes('Perplexity')) {
      console.error('Perplexity Error:', msg);
    }
  });
  await perplexity.connect();

  const epssResearch = await perplexity.callTool({
    name: 'perplexity_ask',
    arguments: {
      messages: [
        {
          role: 'user',
          content: 'What are the best practices for integrating EPSS (Exploit Prediction Scoring System) into a vulnerability scanner? Include caching strategies, error handling, and CVE matching patterns.'
        }
      ]
    }
  });
  console.log('🔬 EPSS Integration Research:', JSON.stringify(epssResearch, null, 2));

  perplexity.disconnect();

  console.log('\n✅ Research Complete!');
  console.log('\n📝 Summary:');
  console.log('- Sequential Thinking: Created 3-step implementation plan');
  console.log('- Context7: Retrieved FastAPI and SQLAlchemy documentation');
  console.log('- Perplexity: Researched EPSS integration best practices');
}

// Run the research
researchEPSSIntegration().catch(console.error);
