/**
 * MCP Code Execution System
 *
 * Implements Anthropic's "Code execution with MCP" pattern for context efficiency.
 * Reduces token usage from ~30k to ~2k tokens (93% reduction).
 *
 * Usage:
 *   import { toolIndex, searchTools, findTools, getToolFileTree } from './mcp-tools';
 *
 * Instead of loading all 42 MCP tool definitions into context:
 *   1. Browse the lightweight tool index (~2k tokens)
 *   2. Load only the tools you need on-demand
 *   3. Write code that composes tools in a single execution step
 *
 * @see https://www.anthropic.com/engineering/code-execution-with-mcp
 */

// Lightweight index - only names and descriptions
export { toolIndex, searchTools, getToolSummary, getServerTools, printToolTree } from './registry/tool-index';

// On-demand loader
export { loadTool, loadTools, generateMinimalContext, clearCache } from './registry/tool-loader';

// Code executor
export { analyzeToolUsage, generateCodeContext, createExecutionPlan, getToolFileTree, findTools } from './executor/code-executor';

/**
 * Quick Reference - Available Tool Categories:
 *
 * context7/
 *   - resolve-library-id: Resolve package to Context7 ID
 *   - get-library-docs: Fetch library documentation
 *
 * github/
 *   - get_me: Get authenticated user
 *   - search_*: Search code, issues, PRs, repos, users
 *   - list_*: List issues, PRs, branches, commits, releases
 *   - issue_read/write: Read/create/update issues
 *   - pull_request_read: Read PR details, diff, status
 *   - create_pull_request: Create new PR
 *   - get_file_contents: Read files from repo
 *   - push_files: Push multiple files in single commit
 *   - create_branch: Create new branch
 *
 * To get full details for any tool:
 *   const def = await loadTool('github', 'search_issues');
 *
 * To search for tools:
 *   const matches = searchTools('issue');
 */
