"""
MCP (Model Context Protocol) Server Implementation
Enables scalable agent-based knowledge workflows
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import websockets
from datetime import datetime

from .orchestrator import MultiModelAgentOrchestrator

logger = logging.getLogger(__name__)

class MCPServer:
    """
    Model Context Protocol Server for agent communication
    Handles inter-agent communication and workflow coordination
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connected_clients = set()
        self.orchestrator = None
        self.server = None
        
    async def initialize(self, azure_config: Dict[str, str]):
        """Initialize MCP server with agent orchestrator"""
        try:
            self.orchestrator = MultiModelAgentOrchestrator(azure_config)
            logger.info("MCP Server initialized with multi-model agents")
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}")
            raise
    
    async def start_server(self):
        """Start the MCP server"""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port
        )
        
        logger.info("MCP server started successfully")
    
    async def handle_client(self, websocket, path):
        """Handle client connections and messages"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.connected_clients.add(websocket)
        logger.info(f"Client {client_id} connected")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            self.connected_clients.discard(websocket)
    
    async def process_message(self, websocket, message: str):
        """Process incoming messages from clients"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "legal_query":
                await self.handle_legal_query(websocket, data)
            elif message_type == "health_check":
                await self.handle_health_check(websocket)
            elif message_type == "agent_status":
                await self.handle_agent_status(websocket)
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON format")
        except Exception as e:
            await self.send_error(websocket, f"Error processing message: {e}")
    
    async def handle_legal_query(self, websocket, data: Dict[str, Any]):
        """Handle legal query through agent orchestrator"""
        query = data.get("query")
        if not query:
            await self.send_error(websocket, "Missing query in request")
            return
        
        try:
            # Send processing acknowledgment
            await self.send_message(websocket, {
                "type": "processing_started",
                "query_id": data.get("query_id"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Process query through multi-model agents
            result = await self.orchestrator.process_legal_query(query)
            
            # Send response
            response = {
                "type": "legal_response",
                "query_id": data.get("query_id"),
                "answer": result.answer,
                "sources": result.sources,
                "confidence_score": result.confidence_score,
                "processing_time": result.processing_time,
                "agent_metrics": result.agent_metrics,
                "optimization_applied": result.optimization_applied,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.send_message(websocket, response)
            
        except Exception as e:
            await self.send_error(websocket, f"Query processing failed: {e}")
    
    async def handle_health_check(self, websocket):
        """Handle health check requests"""
        try:
            health_status = await self.orchestrator.get_system_health()
            
            response = {
                "type": "health_status",
                "status": "healthy",
                "details": health_status,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.send_message(websocket, response)
            
        except Exception as e:
            await self.send_error(websocket, f"Health check failed: {e}")
    
    async def handle_agent_status(self, websocket):
        """Handle agent status requests"""
        try:
            agent_status = {
                "agents_active": len(self.orchestrator.agents),
                "embedding_optimizer_status": "active",
                "last_optimization": datetime.now().isoformat(),
                "performance_metrics": self.orchestrator.performance_metrics
            }
            
            response = {
                "type": "agent_status",
                "status": agent_status,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.send_message(websocket, response)
            
        except Exception as e:
            await self.send_error(websocket, f"Agent status check failed: {e}")
    
    async def send_message(self, websocket, message: Dict[str, Any]):
        """Send message to client"""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def send_error(self, websocket, error_message: str):
        """Send error message to client"""
        error_response = {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_message(websocket, error_response)
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if self.connected_clients:
            await asyncio.gather(
                *[self.send_message(client, message) for client in self.connected_clients],
                return_exceptions=True
            )
    
    async def stop_server(self):
        """Stop the MCP server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("MCP server stopped")

# MCP Client for external integrations
class MCPClient:
    """Client for connecting to MCP server"""
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.websocket = None
    
    async def connect(self):
        """Connect to MCP server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            logger.info(f"Connected to MCP server at {self.server_url}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    async def send_legal_query(self, query: str, query_id: Optional[str] = None) -> Dict[str, Any]:
        """Send legal query to MCP server"""
        if not self.websocket:
            await self.connect()
        
        message = {
            "type": "legal_query",
            "query": query,
            "query_id": query_id or f"query_{datetime.now().timestamp()}"
        }
        
        await self.websocket.send(json.dumps(message))
        
        # Wait for response
        response = await self.websocket.recv()
        return json.loads(response)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get server health status"""
        if not self.websocket:
            await self.connect()
        
        message = {"type": "health_check"}
        await self.websocket.send(json.dumps(message))
        
        response = await self.websocket.recv()
        return json.loads(response)
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from MCP server")
