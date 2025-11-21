import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "issue_read",
  server: "github",
  description: "Get information about a specific issue in a GitHub repository",
  parameters: [
    { name: "method", type: "string", description: "Read operation: get, get_comments, get_sub_issues, get_labels", required: true, enum: ["get", "get_comments", "get_sub_issues", "get_labels"] },
    { name: "owner", type: "string", description: "Repository owner", required: true },
    { name: "repo", type: "string", description: "Repository name", required: true },
    { name: "issue_number", type: "number", description: "Issue number", required: true },
    { name: "page", type: "number", description: "Page number (min 1)", required: false },
    { name: "perPage", type: "number", description: "Results per page (1-100)", required: false },
  ],
  examples: [
    'issue_read({ method: "get", owner: "org", repo: "project", issue_number: 123 })',
    'issue_read({ method: "get_comments", owner: "org", repo: "project", issue_number: 123 })',
  ]
};

export default definition;
