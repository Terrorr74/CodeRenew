import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "get_file_contents",
  server: "github",
  description: "Get the contents of a file or directory from a GitHub repository",
  parameters: [
    { name: "owner", type: "string", description: "Repository owner", required: true },
    { name: "repo", type: "string", description: "Repository name", required: true },
    { name: "path", type: "string", description: "Path to file/directory", required: false },
    { name: "ref", type: "string", description: "Git ref (branch, tag, commit)", required: false },
  ],
};

export default definition;
