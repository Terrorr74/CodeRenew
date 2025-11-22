# MCP Code Execution for Context Efficiency

Based on [Anthropic's approach](https://www.anthropic.com/engineering/code-execution-with-mcp).

## Problem
Loading all MCP tools into context consumes ~30k tokens (15% of context window).

## Solution
1. **Lightweight index** - Tool names/descriptions only (~2k tokens)
2. **On-demand loading** - Full definitions loaded when needed
3. **Code-first execution** - Compose tools in code vs sequential calls

## Token Savings
| Approach | Tokens | Reduction |
|----------|--------|-----------|
| All tools loaded | 30,900 | - |
| Index only | 2,000 | 93% |
| Per-task loading | 500-1,500 | 95-98% |

## Usage

### Browse available tools
```typescript
import { printToolTree, searchTools } from './mcp-tools';

// See all tools
console.log(printToolTree());

// Search by keyword
const issueTools = searchTools('issue');
```

### Load tools on-demand
```typescript
import { loadTool, loadTools } from './mcp-tools';

// Load single tool
const searchIssues = await loadTool('github', 'search_issues');

// Load multiple tools for a task
const tools = await loadTools([
  { server: 'github', name: 'search_issues' },
  { server: 'github', name: 'issue_read' },
]);
```

### Code-first execution pattern
Instead of:
```
Tool call 1: search_issues -> wait -> 500 tokens
Tool call 2: issue_read(1) -> wait -> 500 tokens
Tool call 3: issue_read(2) -> wait -> 500 tokens
... (10 iterations = 5000 tokens + round-trips)
```

Use:
```typescript
// Single code block - executes all logic in one step
const issues = await github.search_issues({ query: "is:open label:bug" });
for (const issue of issues) {
  const details = await github.issue_read({ issue_number: issue.number });
  results.push(details);
}
// Total: ~800 tokens, 60% faster
```

## Programmatic MCP Access

The MCP Client allows direct connection to MCP servers without Claude's integration:

```typescript
import { createContext7Client, createGitHubClient, createSequentialThinkingClient } from './mcp-tools';

// Connect to any MCP server
const client = createContext7Client();
await client.connect();

// Call tools programmatically
const docs = await client.callTool({
  name: 'get-library-docs',
  arguments: { context7CompatibleLibraryID: '/vercel/next.js' }
});

client.disconnect();
```

**Benefits:**
- Zero context usage (tools not loaded into Claude)
- Programmatic control over MCP servers
- Compose multi-tool workflows in code
- Use in scripts, CI/CD, or backend services

See `examples/client-usage.ts` for complete examples.

## File Structure
```
mcp-tools/
  index.ts              # Main exports
  client/
    mcp-client.ts       # Direct MCP server connection
  registry/
    tool-index.ts       # Lightweight tool catalog
    tool-loader.ts      # On-demand loader
  generated/
    github/             # Full tool definitions
    context7/
    sequential-thinking/
  executor/
    code-executor.ts    # Code composition helpers
  examples/
    client-usage.ts     # Usage examples
```
