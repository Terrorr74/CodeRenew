/**
 * On-Demand MCP Tool Loader
 *
 * Loads full tool definitions only when needed, keeping context minimal.
 * Caches loaded tools to avoid repeated file reads.
 */

import { getToolSummary, ToolSummary } from './tool-index';

export interface ToolParameter {
  name: string;
  type: string;
  description: string;
  required: boolean;
  enum?: string[];
}

export interface ToolDefinition {
  name: string;
  server: string;
  description: string;
  parameters: ToolParameter[];
  examples?: string[];
}

// Cache for loaded tool definitions
const toolCache = new Map<string, ToolDefinition>();

/**
 * Load a tool definition on-demand
 * Only reads the full definition when actually needed
 */
export async function loadTool(server: string, name: string): Promise<ToolDefinition | null> {
  const key = `${server}__${name}`;

  // Return cached if available
  if (toolCache.has(key)) {
    return toolCache.get(key)!;
  }

  const summary = getToolSummary(server, name);
  if (!summary) {
    return null;
  }

  try {
    // Dynamic import of the tool definition
    const module = await import(summary.path);
    const def = module.default as ToolDefinition;
    toolCache.set(key, def);
    return def;
  } catch {
    console.error(`Failed to load tool: ${key}`);
    return null;
  }
}

/**
 * Load multiple tools at once
 */
export async function loadTools(tools: Array<{ server: string; name: string }>): Promise<ToolDefinition[]> {
  const results = await Promise.all(
    tools.map(t => loadTool(t.server, t.name))
  );
  return results.filter((t): t is ToolDefinition => t !== null);
}

/**
 * Generate a minimal context string for a set of tools
 * Much smaller than full MCP tool definitions
 */
export function generateMinimalContext(tools: ToolDefinition[]): string {
  return tools.map(t => {
    const params = t.parameters
      .map(p => `  - ${p.name}${p.required ? '*' : ''}: ${p.type} - ${p.description}`)
      .join('\n');
    return `${t.server}.${t.name}: ${t.description}\nParams:\n${params}`;
  }).join('\n\n');
}

/**
 * Clear the tool cache
 */
export function clearCache(): void {
  toolCache.clear();
}
