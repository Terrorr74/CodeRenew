# MCP Tools Guide - Context7, Sequential Thinking & Perplexity

## Overview

This guide shows you how to explore and use the MCP (Model Context Protocol) tools available in the CodeRenew project for AI-assisted development.

## Available MCP Servers

### 1. **Context7** - Library Documentation
- **Purpose:** Get up-to-date documentation for any library/framework
- **Provider:** [@upstash/context7-mcp](https://www.npmjs.com/package/@upstash/context7-mcp)
- **Use Cases:**
  - Get FastAPI documentation
  - Look up React/Next.js patterns
  - Find SQLAlchemy migration guides
  - Research any npm/PyPI package

### 2. **Sequential Thinking** - Problem Breakdown
- **Purpose:** Break down complex problems into step-by-step thoughts
- **Provider:** [@modelcontextprotocol/server-sequential-thinking](https://www.npmjs.com/package/@modelcontextprotocol/server-sequential-thinking)
- **Use Cases:**
  - Plan implementation approach
  - Analyze architecture decisions
  - Debug complex issues
  - Design system workflows

### 3. **Perplexity** - Web Research
- **Purpose:** Real-time web search and AI-powered research
- **Provider:** [@perplexity-ai/mcp-server](https://www.npmjs.com/package/@perplexity-ai/mcp-server)
- **Requires:** `PERPLEXITY_API_KEY` environment variable
- **Use Cases:**
  - Research best practices
  - Find latest security patterns
  - Compare technology choices
  - Deep technical research

---

## Quick Start

### Run the Exploration Script

```bash
# Explore all MCP tools
npx tsx mcp-tools/examples/explore-mcp-tools.ts all

# Explore specific tool
npx tsx mcp-tools/examples/explore-mcp-tools.ts context7
npx tsx mcp-tools/examples/explore-mcp-tools.ts thinking
npx tsx mcp-tools/examples/explore-mcp-tools.ts perplexity
npx tsx mcp-tools/examples/explore-mcp-tools.ts workflow
```

---

## Tool Deep Dive

### 1. Context7 - Library Documentation

#### Available Tools

```typescript
// Tool 1: resolve-library-id
// Purpose: Find Context7 library IDs for a package

const client = createContext7Client();
await client.connect();

const result = await client.callTool({
  name: 'resolve-library-id',
  arguments: { libraryName: 'fastapi' }
});

// Returns:
// {
//   "libraries": [
//     { "id": "/websites/fastapi_tiangolo_com", "name": "FastAPI Official Docs" },
//     { "id": "/pypi/fastapi", "name": "FastAPI PyPI" }
//   ]
// }
```

```typescript
// Tool 2: get-library-docs
// Purpose: Fetch documentation for a specific topic

const docs = await client.callTool({
  name: 'get-library-docs',
  arguments: {
    context7CompatibleLibraryID: '/websites/fastapi_tiangolo_com',
    topic: 'async HTTP requests dependencies'
  }
});

// Returns relevant documentation chunks
```

#### Common Library IDs

| Library | Context7 ID |
|---------|-------------|
| FastAPI | `/websites/fastapi_tiangolo_com` |
| SQLAlchemy | `/websites/docs_sqlalchemy_org` |
| React | `/websites/react_dev` |
| Next.js | `/vercel/next.js` |
| Celery | `/pypi/celery` |
| httpx | `/pypi/httpx` |

#### Example: Get FastAPI Documentation

```typescript
import { createContext7Client } from './mcp-tools';

async function getFastAPIHelp() {
  const client = createContext7Client();
  await client.connect();

  // Find library
  const libs = await client.callTool({
    name: 'resolve-library-id',
    arguments: { libraryName: 'fastapi' }
  });
  console.log('Available FastAPI libraries:', libs);

  // Get docs
  const docs = await client.callTool({
    name: 'get-library-docs',
    arguments: {
      context7CompatibleLibraryID: '/websites/fastapi_tiangolo_com',
      topic: 'background tasks celery integration'
    }
  });
  console.log('Documentation:', docs);

  client.disconnect();
}
```

---

### 2. Sequential Thinking - Problem Breakdown

#### Available Tools

```typescript
// Tool: sequentialthinking
// Purpose: Multi-step reasoning and problem solving

const client = createSequentialThinkingClient();
await client.connect();

const thought = await client.callTool({
  name: 'sequentialthinking',
  arguments: {
    thought: 'Your reasoning or analysis here...',
    thoughtNumber: 1,           // Current thought number (1-based)
    totalThoughts: 3,           // Total thoughts planned
    nextThoughtNeeded: true     // Whether to continue thinking
  }
});
```

#### Example: Plan a Feature Implementation

```typescript
import { createSequentialThinkingClient } from './mcp-tools';

async function planWebhookFeature() {
  const client = createSequentialThinkingClient();
  await client.connect();

  // Thought 1: Analyze requirements
  const step1 = await client.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Analyzing webhook notification requirements:

1. Need to support: Slack, Discord, Email, Custom HTTP
2. Reliability: Retry failed deliveries
3. Observability: Log all attempts
4. Performance: Async delivery (don't block scan)

Next: Consider implementation approach`,
      thoughtNumber: 1,
      totalThoughts: 3,
      nextThoughtNeeded: true
    }
  });

  // Thought 2: Design architecture
  const step2 = await client.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Architecture design:

1. Use Celery for async delivery
2. Redis for queue + retry logic
3. Template system for Slack/Discord formats
4. Database for webhook configs (encrypted)

Next: Identify risks and mitigations`,
      thoughtNumber: 2,
      totalThoughts: 3,
      nextThoughtNeeded: true
    }
  });

  // Thought 3: Risk analysis
  const step3 = await client.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Risks and mitigations:

1. Risk: Webhook URL leaks
   Mitigation: Encrypt in DB, mask in logs

2. Risk: Infinite retry loops
   Mitigation: Max 3 retries, exponential backoff

3. Risk: Slow webhooks block queue
   Mitigation: 10s timeout per request

Ready to implement!`,
      thoughtNumber: 3,
      totalThoughts: 3,
      nextThoughtNeeded: false
    }
  });

  console.log('Step 1:', step1);
  console.log('Step 2:', step2);
  console.log('Step 3:', step3);

  client.disconnect();
}
```

#### Use Cases

✅ **Plan implementations** - Break down features into steps
✅ **Debug issues** - Step-by-step problem analysis
✅ **Architecture decisions** - Compare approaches systematically
✅ **Code reviews** - Analyze changes methodically
✅ **Refactoring** - Plan safe refactoring steps

---

### 3. Perplexity - Web Research

#### Available Tools

```typescript
// Tool 1: perplexity_search
// Quick web search with ranked results
const results = await client.callTool({
  name: 'perplexity_search',
  arguments: {
    query: 'FastAPI async best practices 2025',
    max_results: 5
  }
});

// Tool 2: perplexity_ask
// Conversational AI with web search (sonar-pro)
const answer = await client.callTool({
  name: 'perplexity_ask',
  arguments: {
    messages: [
      { role: 'user', content: 'What are EPSS best practices?' }
    ]
  }
});

// Tool 3: perplexity_research
// Deep research with citations (sonar-deep-research)
const research = await client.callTool({
  name: 'perplexity_research',
  arguments: {
    messages: [
      { role: 'user', content: 'Research webhook retry patterns' }
    ],
    strip_thinking: true  // Remove internal reasoning, show only results
  }
});

// Tool 4: perplexity_reason
// Advanced reasoning (sonar-reasoning-pro)
const reasoning = await client.callTool({
  name: 'perplexity_reason',
  arguments: {
    messages: [
      { role: 'user', content: 'Compare Redis vs RabbitMQ for job queues' }
    ]
  }
});
```

#### Example: Research Best Practices

```typescript
import { createPerplexityClient } from './mcp-tools';

async function researchEPSS() {
  const client = createPerplexityClient();
  await client.connect();

  // Quick search
  const search = await client.callTool({
    name: 'perplexity_search',
    arguments: {
      query: 'EPSS vulnerability scoring system best practices',
      max_results: 5
    }
  });
  console.log('Search results:', search);

  // Conversational AI
  const answer = await client.callTool({
    name: 'perplexity_ask',
    arguments: {
      messages: [
        {
          role: 'user',
          content: 'Explain the benefits of EPSS over traditional CVSS scoring'
        }
      ]
    }
  });
  console.log('AI Answer:', answer);

  // Deep research
  const research = await client.callTool({
    name: 'perplexity_research',
    arguments: {
      messages: [
        {
          role: 'user',
          content: 'Research how to integrate EPSS API into a Python FastAPI application'
        }
      ],
      strip_thinking: true
    }
  });
  console.log('Research findings:', research);

  client.disconnect();
}
```

---

## Practical Workflows

### Workflow 1: Plan and Implement a New Feature

```typescript
async function planAndImplementFeature() {
  // Step 1: Plan with Sequential Thinking
  const thinking = createSequentialThinkingClient();
  await thinking.connect();

  const plan = await thinking.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: 'Planning real-time notifications feature...',
      thoughtNumber: 1,
      totalThoughts: 1,
      nextThoughtNeeded: false
    }
  });

  // Step 2: Get documentation from Context7
  const context7 = createContext7Client();
  await context7.connect();

  const docs = await context7.callTool({
    name: 'get-library-docs',
    arguments: {
      context7CompatibleLibraryID: '/websites/fastapi_tiangolo_com',
      topic: 'background tasks'
    }
  });

  // Step 3: Research with Perplexity
  const perplexity = createPerplexityClient();
  await perplexity.connect();

  const bestPractices = await perplexity.callTool({
    name: 'perplexity_ask',
    arguments: {
      messages: [{
        role: 'user',
        content: 'Webhook delivery best practices'
      }]
    }
  });

  // Cleanup
  thinking.disconnect();
  context7.disconnect();
  perplexity.disconnect();

  return { plan, docs, bestPractices };
}
```

### Workflow 2: Debug Complex Issue

```typescript
async function debugIssue(errorDescription: string) {
  const thinking = createSequentialThinkingClient();
  await thinking.connect();

  // Analyze the error step by step
  const analysis1 = await thinking.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: `Analyzing error: ${errorDescription}

1. What could cause this?
2. What are the symptoms?
3. Next: Check documentation`,
      thoughtNumber: 1,
      totalThoughts: 3,
      nextThoughtNeeded: true
    }
  });

  // ... continue analysis

  thinking.disconnect();
}
```

---

## Environment Setup

### Required Environment Variables

```bash
# Optional: Perplexity API key (for web research)
export PERPLEXITY_API_KEY=your_api_key_here

# Optional: GitHub token (for GitHub MCP tools)
export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here
```

### Get API Keys

**Perplexity API:**
1. Visit [https://www.perplexity.ai/](https://www.perplexity.ai/)
2. Sign up for API access
3. Generate API key
4. Add to `.env` file

---

## Tips and Best Practices

### Context7 Tips

✅ **Be specific with topics** - "async HTTP requests" > "HTTP"
✅ **Use official docs IDs** - `/websites/*` are usually most up-to-date
✅ **Check multiple sources** - Try both `/websites/*` and `/pypi/*`
❌ **Don't use generic queries** - "python" won't help, "fastapi dependencies" will

### Sequential Thinking Tips

✅ **Plan totalThoughts upfront** - Know how many steps you need
✅ **Each thought should progress** - Build on previous thoughts
✅ **Be specific in reasoning** - More detail = better results
✅ **Set nextThoughtNeeded correctly** - `false` on final thought
❌ **Don't make thoughts too long** - Keep under 500 words each

### Perplexity Tips

✅ **Use perplexity_search for quick lookups** - Fast, focused results
✅ **Use perplexity_ask for explanations** - Conversational, detailed
✅ **Use perplexity_research for deep dives** - Citations, comprehensive
✅ **Use perplexity_reason for comparisons** - Trade-off analysis
❌ **Don't mix multiple questions** - One query per call

---

## Common Patterns

### Pattern 1: Research → Plan → Implement

```typescript
// 1. Research the topic
const research = await perplexity.callTool({
  name: 'perplexity_research',
  arguments: { messages: [{ role: 'user', content: 'Topic...' }] }
});

// 2. Plan the implementation
const plan = await thinking.callTool({
  name: 'sequentialthinking',
  arguments: { thought: 'Planning based on research...', ... }
});

// 3. Get library docs
const docs = await context7.callTool({
  name: 'get-library-docs',
  arguments: { context7CompatibleLibraryID: '...', topic: '...' }
});

// 4. Implement with knowledge from all three
```

### Pattern 2: Debug → Research → Fix

```typescript
// 1. Analyze error with Sequential Thinking
const analysis = await thinking.callTool({ ... });

// 2. Research the error with Perplexity
const solutions = await perplexity.callTool({ ... });

// 3. Get official docs from Context7
const correctAPI = await context7.callTool({ ... });

// 4. Apply fix based on combined knowledge
```

---

## Troubleshooting

### Error: "Request timed out"

**Cause:** MCP server took too long to respond (>30s)
**Solution:** Reduce query complexity or check network connection

### Error: "Process closed"

**Cause:** MCP server crashed or was killed
**Solution:** Check if `npx` can run the MCP package, try manual install:
```bash
npm install -g @upstash/context7-mcp
npm install -g @modelcontextprotocol/server-sequential-thinking
```

### Error: "PERPLEXITY_API_KEY not found"

**Cause:** Perplexity API key not set
**Solution:** Add to environment:
```bash
export PERPLEXITY_API_KEY=your_key
```

### Stderr Noise: "Server running on stdio"

**Cause:** MCP servers log startup messages to stderr
**Solution:** This is normal, suppress with error handler:
```typescript
client.on('error', (msg) => {
  if (!msg.includes('running on stdio')) {
    console.error(msg);
  }
});
```

---

## Real Example: EPSS Integration

This is exactly how we used MCP tools to implement EPSS integration:

### Step 1: Research with Perplexity

```typescript
const epssResearch = await perplexity.callTool({
  name: 'perplexity_ask',
  arguments: {
    messages: [{
      role: 'user',
      content: 'What are best practices for integrating EPSS into a vulnerability scanner?'
    }]
  }
});
```

### Step 2: Plan with Sequential Thinking

```typescript
const thought1 = await thinking.callTool({
  name: 'sequentialthinking',
  arguments: {
    thought: `Analyzing EPSS integration:
    1. API: https://api.first.org/data/v1/epss
    2. Need: Batch queries, caching, error handling
    3. Next: Check FastAPI best practices`,
    thoughtNumber: 1,
    totalThoughts: 3,
    nextThoughtNeeded: true
  }
});
```

### Step 3: Get Docs from Context7

```typescript
const fastapiDocs = await context7.callTool({
  name: 'get-library-docs',
  arguments: {
    context7CompatibleLibraryID: '/websites/fastapi_tiangolo_com',
    topic: 'async HTTP requests httpx'
  }
});

const sqlalchemyDocs = await context7.callTool({
  name: 'get-library-docs',
  arguments: {
    context7CompatibleLibraryID: '/websites/docs_sqlalchemy_org',
    topic: 'migrations alembic adding columns'
  }
});
```

**Result:** Complete EPSS integration implemented in 3-5 days! ✅

---

## Next Steps

1. **Try the exploration script:**
   ```bash
   npx tsx mcp-tools/examples/explore-mcp-tools.ts
   ```

2. **Use in your own features:**
   - Copy patterns from `explore-mcp-tools.ts`
   - Integrate into your development workflow
   - Combine all three tools for best results

3. **Experiment:**
   - Try different Context7 libraries
   - Practice multi-step thinking
   - Research your tech stack

**Happy exploring! 🚀**
