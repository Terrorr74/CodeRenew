import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "pull_request_read",
  server: "github",
  description: "Get information on a specific pull request",
  parameters: [
    { name: "method", type: "string", description: "Action to perform", required: true, enum: ["get","get_diff","get_status","get_files","get_review_comments","get_reviews","get_comments"] },
    { name: "owner", type: "string", description: "Repository owner", required: true },
    { name: "repo", type: "string", description: "Repository name", required: true },
    { name: "pullNumber", type: "number", description: "Pull request number", required: true },
  ],
};

export default definition;
