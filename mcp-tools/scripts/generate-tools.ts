#!/usr/bin/env node
/**
 * MCP Tool Definition Generator
 *
 * Generates TypeScript tool definition files from MCP server schemas.
 * Run: node mcp-tools/scripts/generate-tools.ts
 */

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface MCPToolSchema {
  name: string;
  description: string;
  parameters: {
    properties?: Record<string, {
      type: string;
      description?: string;
      enum?: string[];
    }>;
    required?: string[];
  };
}

const GENERATED_DIR = path.join(__dirname, '../generated');

function generateToolFile(server: string, tool: MCPToolSchema): string {
  const params = tool.parameters.properties || {};
  const required = new Set(tool.parameters.required || []);

  const paramDefs = Object.entries(params).map(([name, schema]) => {
    const enumStr = schema.enum ? `, enum: ${JSON.stringify(schema.enum)}` : '';
    return `    { name: "${name}", type: "${schema.type}", description: "${schema.description || ''}", required: ${required.has(name)}${enumStr} },`;
  }).join('\n');

  return `import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "${tool.name}",
  server: "${server}",
  description: "${tool.description}",
  parameters: [
${paramDefs}
  ],
};

export default definition;
`;
}

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

// Core GitHub tools to generate
const githubTools: MCPToolSchema[] = [
  {
    name: "search_code",
    description: "Fast code search across GitHub repositories",
    parameters: {
      properties: {
        query: { type: "string", description: "Search query using GitHub code search syntax" },
        page: { type: "number", description: "Page number" },
        perPage: { type: "number", description: "Results per page (1-100)" },
      },
      required: ["query"]
    }
  },
  {
    name: "list_issues",
    description: "List issues in a GitHub repository",
    parameters: {
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        state: { type: "string", description: "Filter by state", enum: ["OPEN", "CLOSED"] },
        labels: { type: "array", description: "Filter by labels" },
        perPage: { type: "number", description: "Results per page" },
      },
      required: ["owner", "repo"]
    }
  },
  {
    name: "pull_request_read",
    description: "Get information on a specific pull request",
    parameters: {
      properties: {
        method: { type: "string", description: "Action to perform", enum: ["get", "get_diff", "get_status", "get_files", "get_review_comments", "get_reviews", "get_comments"] },
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        pullNumber: { type: "number", description: "Pull request number" },
      },
      required: ["method", "owner", "repo", "pullNumber"]
    }
  },
  {
    name: "create_pull_request",
    description: "Create a new pull request in a GitHub repository",
    parameters: {
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        title: { type: "string", description: "PR title" },
        head: { type: "string", description: "Branch containing changes" },
        base: { type: "string", description: "Branch to merge into" },
        body: { type: "string", description: "PR description" },
        draft: { type: "boolean", description: "Create as draft PR" },
      },
      required: ["owner", "repo", "title", "head", "base"]
    }
  },
  {
    name: "push_files",
    description: "Push multiple files to a GitHub repository in a single commit",
    parameters: {
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        branch: { type: "string", description: "Branch to push to" },
        files: { type: "array", description: "Array of {path, content} objects" },
        message: { type: "string", description: "Commit message" },
      },
      required: ["owner", "repo", "branch", "files", "message"]
    }
  },
  {
    name: "get_file_contents",
    description: "Get the contents of a file or directory from a GitHub repository",
    parameters: {
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        path: { type: "string", description: "Path to file/directory" },
        ref: { type: "string", description: "Git ref (branch, tag, commit)" },
      },
      required: ["owner", "repo"]
    }
  },
];

// Context7 tools
const context7Tools: MCPToolSchema[] = [
  {
    name: "resolve-library-id",
    description: "Resolve a package name to a Context7-compatible library ID",
    parameters: {
      properties: {
        libraryName: { type: "string", description: "Library name to search for" },
      },
      required: ["libraryName"]
    }
  },
  {
    name: "get-library-docs",
    description: "Fetch up-to-date documentation for a library",
    parameters: {
      properties: {
        context7CompatibleLibraryID: { type: "string", description: "Context7 library ID (e.g., '/mongodb/docs')" },
        topic: { type: "string", description: "Topic to focus on (e.g., 'hooks', 'routing')" },
        page: { type: "number", description: "Page number for pagination" },
      },
      required: ["context7CompatibleLibraryID"]
    }
  },
];

// Generate files
function generate() {
  console.log('Generating MCP tool definitions...\n');

  // GitHub tools
  const githubDir = path.join(GENERATED_DIR, 'github');
  ensureDir(githubDir);
  for (const tool of githubTools) {
    const content = generateToolFile('github', tool);
    const filePath = path.join(githubDir, `${tool.name}.ts`);
    fs.writeFileSync(filePath, content);
    console.log(`  ✓ github/${tool.name}.ts`);
  }

  // Context7 tools
  const context7Dir = path.join(GENERATED_DIR, 'context7');
  ensureDir(context7Dir);
  for (const tool of context7Tools) {
    const content = generateToolFile('context7', tool);
    const filePath = path.join(context7Dir, `${tool.name}.ts`);
    fs.writeFileSync(filePath, content);
    console.log(`  ✓ context7/${tool.name}.ts`);
  }

  console.log('\nDone! Generated', githubTools.length + context7Tools.length, 'tool definitions.');
}

generate();
