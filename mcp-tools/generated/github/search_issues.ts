/**
 * GitHub: search_issues
 * Search for issues in GitHub repositories using issues search syntax
 */

import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "search_issues",
  server: "github",
  description: "Search for issues in GitHub repositories using issues search syntax already scoped to is:issue",
  parameters: [
    { name: "query", type: "string", description: "Search query using GitHub issues search syntax", required: true },
    { name: "owner", type: "string", description: "Optional repository owner", required: false },
    { name: "repo", type: "string", description: "Optional repository name", required: false },
    { name: "sort", type: "string", description: "Sort field", required: false, enum: ["comments", "reactions", "created", "updated"] },
    { name: "order", type: "string", description: "Sort order", required: false, enum: ["asc", "desc"] },
    { name: "page", type: "number", description: "Page number (min 1)", required: false },
    { name: "perPage", type: "number", description: "Results per page (1-100)", required: false },
  ],
  examples: [
    'search_issues({ query: "bug label:critical", owner: "org", repo: "project" })',
    'search_issues({ query: "is:open author:username", sort: "updated", order: "desc" })',
  ]
};

export default definition;
