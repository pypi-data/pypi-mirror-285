#
# Copyright (C) 2013 - 2024 Oracle and/or its affiliates. All rights reserved.
#

from pypgx.api._graph_config import GraphConfig
from pypgx.api._graph_config_interfaces import DbConnectionConfig
from typing import List, Optional
from pypgx._utils.error_handling import java_handler
from pypgx._utils import conversion


class PgGraphConfig(GraphConfig):
    """A class for representing PG graph configurations"""

    _java_class = "oracle.pgx.config.AbstractPgGraphConfig"

    def get_db_engine(self) -> str:
        """Get the target database engine of this configuration.

        :returns: the target database engine
        """
        e_type = java_handler(self._graph_config.getDbEngine, [])
        return conversion.enum_to_python_str(e_type)

    def get_max_num_connections(self) -> int:
        """Get the maximum number of connections of this configuration.

        :returns: the maximum number of connections
        """
        return java_handler(self._graph_config.getMaxNumConnections, [])


class PgHbaseGraphConfig(PgGraphConfig):
    """A class for representing Pg HBase graph configurations"""

    _java_class = "oracle.pgx.config.PgHbaseGraphConfig"

    def get_zk_quorum(self) -> str:
        """Get the ZooKeeper Quorum.

        :returns: the ZooKeeper Quorum
        """
        return java_handler(self._graph_config.getZkQuorum, [])

    def get_splits_per_region(self) -> int:
        """Get the splits per region.

        :returns: the splits per region
        """
        return java_handler(self._graph_config.getSplitsPerRegion, [])

    def get_zk_session_timeout(self) -> int:
        """Get the ZooKeeper session timeout.

        :returns: the ZooKeeper session timeout
        """
        return java_handler(self._graph_config.getZkSessionTimeout, [])

    def get_zk_client_port(self) -> int:
        """Get the ZooKeeper client port.

        :returns: the ZooKeeper client port
        """
        return java_handler(self._graph_config.getZkClientPort, [])

    def get_zk_node_parent(self) -> str:
        """Get the ZooKeeper parent node.

        :returns: the ZooKeeper parent node
        """
        return java_handler(self._graph_config.getZkNodeParent, [])

    def get_block_cache_size(self) -> int:
        """Get the block cache size.

        :returns: the block cache size
        """
        return java_handler(self._graph_config.getBlockCacheSize, [])

    def get_compression(self) -> str:
        """Get the HBase compression algorithm to use.

        :returns: the HBase compression algorithm to use.
        """
        return java_handler(self._graph_config.getCompression, [])

    def get_data_block_encoding(self) -> str:
        """Get the datablock encoding algorithm to use.

        :returns: the datablock encoding algorithm to use
        """
        return java_handler(self._graph_config.getDataBlockEncoding, [])

    def get_hadoop_sec_auth(self) -> str:
        """Get the hadoop authentication string.

        :returns: the Hadoop authentication string
        """
        return java_handler(self._graph_config.getHadoopSecAuth, [])

    def get_hbase_sec_auth(self) -> str:
        """Get the HBase authentication string.

        :returns: the HBase authentication string
        """
        return java_handler(self._graph_config.getHbaseSecAuth, [])

    def get_hm_kerberos_principal(self) -> str:
        """Get the HM Kerberos principal.

        :returns: the HM Kerberos principal
        """
        return java_handler(self._graph_config.getHmKerberosPrincipal, [])

    def get_initial_edge_num_regions(self) -> int:
        """Get the number of initial edge regions defined for the HBase tables.

        :returns: the number of initial edge regions defined for the HBase tables
        """
        return java_handler(self._graph_config.getInitialEdgeNumRegions, [])

    def get_initial_vertex_num_regions(self) -> int:
        """Get the number of initial vertex regions defined for the HBase tables.

        :returns: the number of initial vertex regions defined for the HBase tables
        """
        return java_handler(self._graph_config.getInitialVertexNumRegions, [])

    def get_keytab(self) -> str:
        """Get the path to keytab file.

        :returns: path to keytab file
        """
        return java_handler(self._graph_config.getKeytab, [])

    def get_rs_kerberos_principal(self) -> str:
        """Get the RS Kerberos principal.

        :returns: the RS Kerberos principal
        """
        return java_handler(self._graph_config.getRsKerberosPrincipal, [])

    def get_user_principal(self) -> str:
        """Get the user principal.

        :returns: the user principal
        """
        return java_handler(self._graph_config.getUserPrincipal, [])


class PgNosqlGraphConfig(PgGraphConfig):
    """A class for representing Pg No SQL graph configurations"""

    _java_class = "oracle.pgx.config.PgNosqlGraphConfig"

    def get_hosts(self) -> List[str]:
        """Get the list of hosts.

        :returns: the hosts
        """
        hosts = java_handler(self._graph_config.getHosts, [])
        return conversion.collection_to_python_list(hosts)

    def get_store_name(self) -> str:
        """Get the store name.

        :returns: the store name
        """
        return java_handler(self._graph_config.getStoreName, [])

    def get_request_timeout_ms(self) -> int:
        """Get the NoSQL request timeout in milliseconds

        :returns: the NoSQL request timeout in milliseconds
        """
        return java_handler(self._graph_config.getRequestTimeoutMs, [])

    def get_username(self) -> Optional[str]:
        """Get the name of a NoSQL user.

        :returns: the name of a NoSQL user
        """
        return java_handler(self._graph_config.getUsername, [])


class PgRdbmsGraphConfig(PgGraphConfig, DbConnectionConfig):
    """A class for representing PG RDBMS graph configurations"""

    _java_class = "oracle.pgx.config.PgRdbmsGraphConfig"

    def get_vertices_view_name(self) -> Optional[str]:
        """Get the name of view for vertices

        :returns: the name of view for vertices
        """
        return java_handler(self._graph_config.getVerticesViewName, [])

    def get_edges_view_name(self) -> Optional[str]:
        """Get the name of view for edges.

        :returns: the name of view for edges
        """
        return java_handler(self._graph_config.getEdgesViewName, [])

    def get_label(self) -> Optional[str]:
        """Get the label.

        :returns: the label
        """
        return java_handler(self._graph_config.getLabel, [])

    def get_security_policy(self) -> Optional[str]:
        """Get the security policy for the label or row label.

        :returns: the policy
        """
        return java_handler(self._graph_config.getSecurityPolicy, [])

    def get_owner(self) -> Optional[str]:
        """Get the owner.

        :returns: the owner
        """
        return java_handler(self._graph_config.getOwner, [])

    def get_row_label(self) -> Optional[str]:
        """Get the row label.

        :returns: the row label
        """
        return java_handler(self._graph_config.getRowLabel, [])

    def get_options(self) -> Optional[str]:
        """Get the parameter that is used by the data access layer (and the underlying database)
        to change default behaviors of graph instance creation or initialization.

        :returns: the parameter
        """
        return java_handler(self._graph_config.getOptions, [])

    def get_view_parallel_hint_degree(self) -> int:
        """If view names are given, the resulting query will be hinted to run in parallel with
        the given degree.

        :returns: the view parallel hint degree
        """
        return java_handler(self._graph_config.getViewParallelHintDegree, [])
