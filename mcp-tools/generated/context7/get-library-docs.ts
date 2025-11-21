import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "get-library-docs",
  server: "context7",
  description: "Fetch up-to-date documentation for a library",
  parameters: [
    { name: "context7CompatibleLibraryID", type: "string", description: "Context7 library ID (e.g., '/mongodb/docs')", required: true },
    { name: "topic", type: "string", description: "Topic to focus on (e.g., 'hooks', 'routing')", required: false },
    { name: "page", type: "number", description: "Page number for pagination", required: false },
  ],
};

export default definition;
