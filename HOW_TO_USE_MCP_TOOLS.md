# How to Use MCP Tools - Quick Start

## What are MCP Tools?

MCP (Model Context Protocol) tools let you connect AI assistants to external data sources and APIs. CodeRenew has three powerful MCP servers integrated:

1. **Context7** 📚 - Get up-to-date library documentation (FastAPI, React, SQLAlchemy, etc.)
2. **Sequential Thinking** 🧠 - Break down complex problems into step-by-step analysis
3. **Perplexity** 🔬 - AI-powered web research with real-time data

---

## 🚀 Quick Start (3 Ways)

### Option 1: Interactive Shell Script (Easiest)

```bash
./scripts/explore-mcp.sh
```

This launches an interactive menu where you can:
- Search library docs (Context7)
- Analyze problems step-by-step (Sequential Thinking)
- Research topics (Perplexity)
- See practical workflows

### Option 2: Run Exploration Script

```bash
# Explore all tools
npx tsx mcp-tools/examples/explore-mcp-tools.ts all

# Explore specific tool
npx tsx mcp-tools/examples/explore-mcp-tools.ts context7
npx tsx mcp-tools/examples/explore-mcp-tools.ts thinking
npx tsx mcp-tools/examples/explore-mcp-tools.ts perplexity
npx tsx mcp-tools/examples/explore-mcp-tools.ts workflow
```

### Option 3: Use Programmatically

```typescript
import { createContext7Client } from './mcp-tools';

const client = createContext7Client();
await client.connect();

const docs = await client.callTool({
  name: 'get-library-docs',
  arguments: {
    context7CompatibleLibraryID: '/websites/fastapi_tiangolo_com',
    topic: 'async HTTP requests'
  }
});

console.log(docs);
client.disconnect();
```

---

## 📚 Real-World Examples

### Example 1: Get FastAPI Documentation

```bash
# Interactive
./scripts/explore-mcp.sh
# Choose: 1) Context7
# Library: fastapi
# Topic: background tasks celery

# Programmatic
npx tsx -e "
import { createContext7Client } from './mcp-tools';
const client = createContext7Client();
client.on('error', () => {});
await client.connect();
const docs = await client.callTool({
  name: 'get-library-docs',
  arguments: {
    context7CompatibleLibraryID: '/websites/fastapi_tiangolo_com',
    topic: 'background tasks celery'
  }
});
console.log(docs);
client.disconnect();
"
```

### Example 2: Plan a Feature with Sequential Thinking

```bash
# Interactive
./scripts/explore-mcp.sh
# Choose: 2) Sequential Thinking
# Problem: How to implement webhook notifications?

# Programmatic
npx tsx -e "
import { createSequentialThinkingClient } from './mcp-tools';
const client = createSequentialThinkingClient();
client.on('error', () => {});
await client.connect();
const thought = await client.callTool({
  name: 'sequentialthinking',
  arguments: {
    thought: 'Planning webhook notifications: 1) Requirements, 2) Architecture, 3) Implementation',
    thoughtNumber: 1,
    totalThoughts: 1,
    nextThoughtNeeded: false
  }
});
console.log(thought);
client.disconnect();
"
```

### Example 3: Research Best Practices with Perplexity

```bash
# Set API key first
export PERPLEXITY_API_KEY=your_key_here

# Interactive
./scripts/explore-mcp.sh
# Choose: 3) Perplexity
# Question: What are EPSS best practices?

# Programmatic
npx tsx -e "
import { createPerplexityClient } from './mcp-tools';
const client = createPerplexityClient();
client.on('error', () => {});
await client.connect();
const answer = await client.callTool({
  name: 'perplexity_ask',
  arguments: {
    messages: [{
      role: 'user',
      content: 'What are best practices for EPSS integration?'
    }]
  }
});
console.log(answer);
client.disconnect();
"
```

---

## 🎯 Common Use Cases

### Use Case 1: Implementing a New Feature

**Workflow:** Sequential Thinking → Context7 → Perplexity

```bash
# Step 1: Plan with Sequential Thinking
npx tsx mcp-tools/examples/explore-mcp-tools.ts thinking

# Step 2: Get library docs with Context7
npx tsx mcp-tools/examples/explore-mcp-tools.ts context7

# Step 3: Research best practices with Perplexity
npx tsx mcp-tools/examples/explore-mcp-tools.ts perplexity

# Or run the complete workflow:
npx tsx mcp-tools/examples/explore-mcp-tools.ts workflow
```

### Use Case 2: Debugging an Issue

```typescript
// 1. Analyze with Sequential Thinking
const analysis = await thinkingClient.callTool({
  name: 'sequentialthinking',
  arguments: {
    thought: 'Analyzing error: Database connection timeout...',
    thoughtNumber: 1,
    totalThoughts: 3,
    nextThoughtNeeded: true
  }
});

// 2. Get SQLAlchemy docs
const docs = await context7Client.callTool({
  name: 'get-library-docs',
  arguments: {
    context7CompatibleLibraryID: '/websites/docs_sqlalchemy_org',
    topic: 'connection pooling timeout'
  }
});

// 3. Research solutions
const solutions = await perplexityClient.callTool({
  name: 'perplexity_ask',
  arguments: {
    messages: [{
      role: 'user',
      content: 'How to fix SQLAlchemy connection pool timeouts?'
    }]
  }
});
```

### Use Case 3: Learning a New Library

```bash
# Example: Learning Celery

# 1. Get library ID
npx tsx -e "
import { createContext7Client } from './mcp-tools';
const client = createContext7Client();
await client.connect();
const libs = await client.callTool({
  name: 'resolve-library-id',
  arguments: { libraryName: 'celery' }
});
console.log(libs);
"

# 2. Get documentation on specific topics
# - Retry logic
# - Task scheduling
# - Error handling
```

---

## 🛠️ Setup & Configuration

### Required

```bash
# Install Node.js (includes npx)
# Already installed if you can run npm

# No additional setup needed for Context7 and Sequential Thinking!
```

### Optional: Perplexity API

```bash
# Get API key from https://www.perplexity.ai/
export PERPLEXITY_API_KEY=your_api_key_here

# Or add to .env file
echo "PERPLEXITY_API_KEY=your_api_key_here" >> .env
```

---

## 📖 Full Documentation

For detailed documentation, see:

- **[MCP_TOOLS_GUIDE.md](./MCP_TOOLS_GUIDE.md)** - Complete guide with all tools, parameters, and examples
- **[mcp-tools/USAGE.md](./mcp-tools/USAGE.md)** - Technical usage documentation
- **[mcp-tools/examples/](./mcp-tools/examples/)** - Code examples

---

## 💡 Tips

### Context7 Tips

✅ **Be specific:** "async HTTP requests" > "HTTP"
✅ **Try multiple library IDs:** `/websites/*` and `/pypi/*`
❌ **Avoid generic queries:** "python" won't help

### Sequential Thinking Tips

✅ **Plan totalThoughts upfront:** Know your steps
✅ **Build on previous thoughts:** Each step progresses
✅ **Be detailed:** More context = better analysis

### Perplexity Tips

✅ **Use `perplexity_search` for quick lookups**
✅ **Use `perplexity_ask` for explanations**
✅ **Use `perplexity_research` for deep dives**

---

## 🎉 Real Success Story: EPSS Integration

We used all three MCP tools to implement EPSS integration:

1. **Perplexity:** Researched EPSS best practices
2. **Sequential Thinking:** Planned implementation approach (3 steps)
3. **Context7:** Got FastAPI and SQLAlchemy documentation

**Result:** Complete feature implemented in 3-5 days! ✅

See [EPSS_IMPLEMENTATION_SUMMARY.md](./EPSS_IMPLEMENTATION_SUMMARY.md) for details.

---

## 🆘 Troubleshooting

### "npx not found"
```bash
# Install Node.js from https://nodejs.org/
```

### "Request timed out"
```bash
# Reduce query complexity or check network
```

### "PERPLEXITY_API_KEY not found"
```bash
# Set environment variable
export PERPLEXITY_API_KEY=your_key
```

### Stderr noise: "Server running on stdio"
```typescript
// This is normal, suppress with:
client.on('error', (msg) => {
  if (!msg.includes('running on stdio')) {
    console.error(msg);
  }
});
```

---

## 🚀 Get Started Now!

```bash
# Easiest way - interactive menu
./scripts/explore-mcp.sh

# Or run exploration script
npx tsx mcp-tools/examples/explore-mcp-tools.ts all

# Or read the full guide
cat MCP_TOOLS_GUIDE.md
```

**Happy exploring! 🎊**
