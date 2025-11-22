/**
 * MCP Tool Registry - Lightweight Index
 *
 * This file provides a minimal file tree of available MCP tools.
 * Instead of loading all tool definitions into context (~30k tokens),
 * agents can browse this index and load only needed tools on-demand.
 *
 * Based on Anthropic's "Code execution with MCP" approach:
 * https://www.anthropic.com/engineering/code-execution-with-mcp
 */

export interface ToolSummary {
  name: string;
  description: string;
  server: string;
  path: string;
}

export interface ToolCategory {
  name: string;
  tools: ToolSummary[];
}

/**
 * Minimal tool index - only names and descriptions (~2k tokens vs 30k)
 * Load full tool definitions on-demand from ./generated/{server}/{tool}.ts
 */
export const toolIndex: ToolCategory[] = [
  {
    name: "context7",
    tools: [
      { name: "resolve-library-id", description: "Resolve package name to Context7 library ID", server: "context7", path: "./generated/context7/resolve-library-id.ts" },
      { name: "get-library-docs", description: "Fetch up-to-date library documentation", server: "context7", path: "./generated/context7/get-library-docs.ts" },
    ]
  },
  {
    name: "perplexity",
    tools: [
      { name: "perplexity_search", description: "Web search with ranked results and metadata", server: "perplexity", path: "./generated/perplexity/perplexity_search.ts" },
      { name: "perplexity_ask", description: "Conversational AI with real-time web search (sonar-pro)", server: "perplexity", path: "./generated/perplexity/perplexity_ask.ts" },
      { name: "perplexity_research", description: "Deep research with citations (sonar-deep-research)", server: "perplexity", path: "./generated/perplexity/perplexity_research.ts" },
      { name: "perplexity_reason", description: "Advanced reasoning (sonar-reasoning-pro)", server: "perplexity", path: "./generated/perplexity/perplexity_reason.ts" },
    ]
  },
  {
    name: "github",
    tools: [
      { name: "get_me", description: "Get authenticated user info", server: "github", path: "./generated/github/get_me.ts" },
      { name: "search_code", description: "Search code across repositories", server: "github", path: "./generated/github/search_code.ts" },
      { name: "search_issues", description: "Search issues in repositories", server: "github", path: "./generated/github/search_issues.ts" },
      { name: "search_pull_requests", description: "Search pull requests", server: "github", path: "./generated/github/search_pull_requests.ts" },
      { name: "list_issues", description: "List issues in a repository", server: "github", path: "./generated/github/list_issues.ts" },
      { name: "list_pull_requests", description: "List PRs in a repository", server: "github", path: "./generated/github/list_pull_requests.ts" },
      { name: "issue_read", description: "Read issue details", server: "github", path: "./generated/github/issue_read.ts" },
      { name: "issue_write", description: "Create/update issues", server: "github", path: "./generated/github/issue_write.ts" },
      { name: "pull_request_read", description: "Read PR details, diff, status", server: "github", path: "./generated/github/pull_request_read.ts" },
      { name: "create_pull_request", description: "Create new pull request", server: "github", path: "./generated/github/create_pull_request.ts" },
      { name: "get_file_contents", description: "Get file/directory contents", server: "github", path: "./generated/github/get_file_contents.ts" },
      { name: "create_or_update_file", description: "Create/update file in repo", server: "github", path: "./generated/github/create_or_update_file.ts" },
      { name: "push_files", description: "Push multiple files in single commit", server: "github", path: "./generated/github/push_files.ts" },
      { name: "create_branch", description: "Create new branch", server: "github", path: "./generated/github/create_branch.ts" },
      { name: "list_branches", description: "List repository branches", server: "github", path: "./generated/github/list_branches.ts" },
      { name: "list_commits", description: "List branch commits", server: "github", path: "./generated/github/list_commits.ts" },
      { name: "get_commit", description: "Get commit details", server: "github", path: "./generated/github/get_commit.ts" },
    ]
  }
];

/**
 * Get tool summary by name - O(1) lookup
 */
const toolMap = new Map<string, ToolSummary>();
toolIndex.forEach(cat => cat.tools.forEach(t => toolMap.set(`${t.server}__${t.name}`, t)));

export function getToolSummary(server: string, name: string): ToolSummary | undefined {
  return toolMap.get(`${server}__${name}`);
}

/**
 * Search tools by keyword in name or description
 */
export function searchTools(query: string): ToolSummary[] {
  const q = query.toLowerCase();
  return toolIndex.flatMap(cat =>
    cat.tools.filter(t =>
      t.name.toLowerCase().includes(q) ||
      t.description.toLowerCase().includes(q)
    )
  );
}

/**
 * Get all tools for a server
 */
export function getServerTools(server: string): ToolSummary[] {
  return toolIndex.find(cat => cat.name === server)?.tools ?? [];
}

/**
 * Print file tree (for agent context)
 */
export function printToolTree(): string {
  let tree = "mcp-tools/\n";
  for (const cat of toolIndex) {
    tree += `  ${cat.name}/\n`;
    for (const tool of cat.tools) {
      tree += `    ${tool.name}.ts - ${tool.description}\n`;
    }
  }
  return tree;
}
