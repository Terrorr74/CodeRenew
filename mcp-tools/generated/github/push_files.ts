import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "push_files",
  server: "github",
  description: "Push multiple files to a GitHub repository in a single commit",
  parameters: [
    { name: "owner", type: "string", description: "Repository owner", required: true },
    { name: "repo", type: "string", description: "Repository name", required: true },
    { name: "branch", type: "string", description: "Branch to push to", required: true },
    { name: "files", type: "array", description: "Array of {path, content} objects", required: true },
    { name: "message", type: "string", description: "Commit message", required: true },
  ],
};

export default definition;
