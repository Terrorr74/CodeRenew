/**
 * MCP Client - Direct connection to MCP servers via JSON-RPC over stdio
 *
 * Bypasses Claude's MCP integration for programmatic tool access.
 */

import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';

export interface MCPRequest {
  jsonrpc: '2.0';
  id: number;
  method: string;
  params?: Record<string, unknown>;
}

export interface MCPResponse {
  jsonrpc: '2.0';
  id: number;
  result?: unknown;
  error?: { code: number; message: string; data?: unknown };
}

export interface MCPToolCall {
  name: string;
  arguments: Record<string, unknown>;
}

export class MCPClient extends EventEmitter {
  private process: ChildProcess | null = null;
  private requestId = 0;
  private pending = new Map<number, { resolve: (v: unknown) => void; reject: (e: Error) => void }>();
  private buffer = '';

  constructor(
    private command: string,
    private args: string[]
  ) {
    super();
  }

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.process = spawn(this.command, this.args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env }
      });

      this.process.stdout?.on('data', (data: Buffer) => {
        this.handleData(data.toString());
      });

      this.process.stderr?.on('data', (data: Buffer) => {
        this.emit('error', data.toString());
      });

      this.process.on('error', reject);
      this.process.on('close', (code) => {
        this.emit('close', code);
        this.pending.forEach(p => p.reject(new Error('Process closed')));
        this.pending.clear();
      });

      // Initialize MCP connection
      setTimeout(async () => {
        try {
          await this.call('initialize', {
            protocolVersion: '2024-11-05',
            capabilities: {},
            clientInfo: { name: 'mcp-tools-client', version: '1.0.0' }
          });
          await this.call('notifications/initialized', {});
          resolve();
        } catch (e) {
          reject(e);
        }
      }, 500);
    });
  }

  private handleData(data: string): void {
    this.buffer += data;
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop() || '';

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const response: MCPResponse = JSON.parse(line);
        const pending = this.pending.get(response.id);
        if (pending) {
          this.pending.delete(response.id);
          if (response.error) {
            pending.reject(new Error(response.error.message));
          } else {
            pending.resolve(response.result);
          }
        }
      } catch {
        // Non-JSON output, emit as log
        this.emit('log', line);
      }
    }
  }

  async call(method: string, params?: Record<string, unknown>): Promise<unknown> {
    if (!this.process?.stdin) {
      throw new Error('Not connected');
    }

    const id = ++this.requestId;
    const request: MCPRequest = { jsonrpc: '2.0', id, method, params };

    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.process!.stdin!.write(JSON.stringify(request) + '\n');

      // Timeout after 30s
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`Request ${id} timed out`));
        }
      }, 30000);
    });
  }

  async listTools(): Promise<unknown> {
    return this.call('tools/list', {});
  }

  async callTool(tool: MCPToolCall): Promise<unknown> {
    return this.call('tools/call', tool);
  }

  disconnect(): void {
    this.process?.kill();
    this.process = null;
  }
}

/**
 * Pre-configured client factories
 */
export function createContext7Client(): MCPClient {
  return new MCPClient('npx', ['-y', '@upstash/context7-mcp']);
}

export function createGitHubClient(token?: string): MCPClient {
  if (token) {
    process.env.GITHUB_PERSONAL_ACCESS_TOKEN = token;
  }
  return new MCPClient('npx', ['-y', '@modelcontextprotocol/server-github']);
}

export function createSequentialThinkingClient(): MCPClient {
  return new MCPClient('npx', ['-y', '@modelcontextprotocol/server-sequential-thinking']);
}

export function createPerplexityClient(apiKey?: string): MCPClient {
  if (apiKey) {
    process.env.PERPLEXITY_API_KEY = apiKey;
  }
  return new MCPClient('npx', ['-y', '@perplexity-ai/mcp-server']);
}

/**
 * Example usage:
 *
 * const client = createContext7Client();
 * await client.connect();
 *
 * const docs = await client.callTool({
 *   name: 'get-library-docs',
 *   arguments: { context7CompatibleLibraryID: '/vercel/next.js', topic: 'routing' }
 * });
 *
 * client.disconnect();
 */
