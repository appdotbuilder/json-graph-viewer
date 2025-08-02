from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


# Persistent models (stored in database)
class Graph(SQLModel, table=True):
    """A network graph containing nodes and edges"""

    __tablename__ = "graphs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # JSON properties for graph-level data
    properties: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    nodes: List["Node"] = Relationship(back_populates="graph", cascade_delete=True)
    edges: List["Edge"] = Relationship(back_populates="graph", cascade_delete=True)


class Node(SQLModel, table=True):
    """A node in the network graph"""

    __tablename__ = "nodes"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    graph_id: int = Field(foreign_key="graphs.id")

    # Node identifier (unique within a graph)
    node_id: str = Field(max_length=100, index=True)

    # Display properties
    label: str = Field(default="", max_length=200)

    # Position coordinates
    x: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=12)
    y: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=12)

    # Visual properties stored as JSON
    style: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Additional node data
    data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    graph: Graph = Relationship(back_populates="nodes")
    outgoing_edges: List["Edge"] = Relationship(
        back_populates="source_node", sa_relationship_kwargs={"foreign_keys": "[Edge.source_node_id]"}
    )
    incoming_edges: List["Edge"] = Relationship(
        back_populates="target_node", sa_relationship_kwargs={"foreign_keys": "[Edge.target_node_id]"}
    )


class Edge(SQLModel, table=True):
    """An edge connecting two nodes in the network graph"""

    __tablename__ = "edges"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    graph_id: int = Field(foreign_key="graphs.id")

    # Edge identifier (unique within a graph)
    edge_id: Optional[str] = Field(default=None, max_length=100, index=True)

    # Source and target nodes
    source_node_id: int = Field(foreign_key="nodes.id")
    target_node_id: int = Field(foreign_key="nodes.id")

    # Display properties
    label: str = Field(default="", max_length=200)
    weight: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=12)

    # Visual properties stored as JSON
    style: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Additional edge data
    data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    graph: Graph = Relationship(back_populates="edges")
    source_node: Node = Relationship(
        back_populates="outgoing_edges", sa_relationship_kwargs={"foreign_keys": "[Edge.source_node_id]"}
    )
    target_node: Node = Relationship(
        back_populates="incoming_edges", sa_relationship_kwargs={"foreign_keys": "[Edge.target_node_id]"}
    )


# Non-persistent schemas (for validation, forms, API requests/responses)
class NodeData(SQLModel, table=False):
    """Schema for node data in JSON input"""

    id: str = Field(max_length=100)
    label: Optional[str] = Field(default=None, max_length=200)
    x: Optional[float] = Field(default=None)
    y: Optional[float] = Field(default=None)
    style: Optional[Dict[str, Any]] = Field(default=None)
    data: Optional[Dict[str, Any]] = Field(default=None)


class EdgeData(SQLModel, table=False):
    """Schema for edge data in JSON input"""

    id: Optional[str] = Field(default=None, max_length=100)
    source: str = Field(max_length=100)
    target: str = Field(max_length=100)
    label: Optional[str] = Field(default=None, max_length=200)
    weight: Optional[float] = Field(default=None)
    style: Optional[Dict[str, Any]] = Field(default=None)
    data: Optional[Dict[str, Any]] = Field(default=None)


class GraphInput(SQLModel, table=False):
    """Schema for complete graph JSON input"""

    name: Optional[str] = Field(default="Untitled Graph", max_length=200)
    description: Optional[str] = Field(default="", max_length=1000)
    nodes: List[NodeData] = Field(default=[])
    edges: List[EdgeData] = Field(default=[])
    properties: Optional[Dict[str, Any]] = Field(default=None)


class GraphCreate(SQLModel, table=False):
    """Schema for creating a new graph"""

    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    properties: Dict[str, Any] = Field(default={})


class GraphUpdate(SQLModel, table=False):
    """Schema for updating an existing graph"""

    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default=None)


class NodeCreate(SQLModel, table=False):
    """Schema for creating a new node"""

    graph_id: int
    node_id: str = Field(max_length=100)
    label: str = Field(default="", max_length=200)
    x: Optional[float] = Field(default=None)
    y: Optional[float] = Field(default=None)
    style: Dict[str, Any] = Field(default={})
    data: Dict[str, Any] = Field(default={})


class NodeUpdate(SQLModel, table=False):
    """Schema for updating an existing node"""

    label: Optional[str] = Field(default=None, max_length=200)
    x: Optional[float] = Field(default=None)
    y: Optional[float] = Field(default=None)
    style: Optional[Dict[str, Any]] = Field(default=None)
    data: Optional[Dict[str, Any]] = Field(default=None)


class EdgeCreate(SQLModel, table=False):
    """Schema for creating a new edge"""

    graph_id: int
    edge_id: Optional[str] = Field(default=None, max_length=100)
    source_node_id: int
    target_node_id: int
    label: str = Field(default="", max_length=200)
    weight: Optional[float] = Field(default=None)
    style: Dict[str, Any] = Field(default={})
    data: Dict[str, Any] = Field(default={})


class EdgeUpdate(SQLModel, table=False):
    """Schema for updating an existing edge"""

    label: Optional[str] = Field(default=None, max_length=200)
    weight: Optional[float] = Field(default=None)
    style: Optional[Dict[str, Any]] = Field(default=None)
    data: Optional[Dict[str, Any]] = Field(default=None)


class GraphResponse(SQLModel, table=False):
    """Schema for graph data output"""

    id: int
    name: str
    description: str
    created_at: str
    updated_at: str
    properties: Dict[str, Any]
    node_count: int
    edge_count: int


class NodeResponse(SQLModel, table=False):
    """Schema for node data output"""

    id: int
    node_id: str
    label: str
    x: Optional[float]
    y: Optional[float]
    style: Dict[str, Any]
    data: Dict[str, Any]
    created_at: str


class EdgeResponse(SQLModel, table=False):
    """Schema for edge data output"""

    id: int
    edge_id: Optional[str]
    source_node_id: int
    target_node_id: int
    label: str
    weight: Optional[float]
    style: Dict[str, Any]
    data: Dict[str, Any]
    created_at: str


class GraphExport(SQLModel, table=False):
    """Schema for exporting complete graph data"""

    name: str
    description: str
    properties: Dict[str, Any]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
