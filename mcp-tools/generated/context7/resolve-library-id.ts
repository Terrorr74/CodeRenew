import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "resolve-library-id",
  server: "context7",
  description: "Resolve a package name to a Context7-compatible library ID",
  parameters: [
    { name: "libraryName", type: "string", description: "Library name to search for", required: true },
  ],
};

export default definition;
