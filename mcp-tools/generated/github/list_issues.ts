import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "list_issues",
  server: "github",
  description: "List issues in a GitHub repository",
  parameters: [
    { name: "owner", type: "string", description: "Repository owner", required: true },
    { name: "repo", type: "string", description: "Repository name", required: true },
    { name: "state", type: "string", description: "Filter by state", required: false, enum: ["OPEN","CLOSED"] },
    { name: "labels", type: "array", description: "Filter by labels", required: false },
    { name: "perPage", type: "number", description: "Results per page", required: false },
  ],
};

export default definition;
