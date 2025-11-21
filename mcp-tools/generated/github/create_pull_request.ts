import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "create_pull_request",
  server: "github",
  description: "Create a new pull request in a GitHub repository",
  parameters: [
    { name: "owner", type: "string", description: "Repository owner", required: true },
    { name: "repo", type: "string", description: "Repository name", required: true },
    { name: "title", type: "string", description: "PR title", required: true },
    { name: "head", type: "string", description: "Branch containing changes", required: true },
    { name: "base", type: "string", description: "Branch to merge into", required: true },
    { name: "body", type: "string", description: "PR description", required: false },
    { name: "draft", type: "boolean", description: "Create as draft PR", required: false },
  ],
};

export default definition;
