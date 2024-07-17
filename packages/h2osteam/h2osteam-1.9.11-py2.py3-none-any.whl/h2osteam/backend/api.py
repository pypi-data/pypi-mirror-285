# -*- coding: utf-8 -*-
# ------------------------------
# --- This is generated code ---
# ---      DO NOT EDIT       ---
# ------------------------------
from __future__ import absolute_import, division, print_function, unicode_literals


class SteamApi:
    
    def priority_list(self):
        """
        Dummy method to discover structs in a correct order for Python API

        Parameters:

        Returns:
        a: No description available (ProfileValue)
        b: No description available (ProfileH2o)
        c: No description available (ProfileSparklingInternal)
        d: No description available (ProfileSparklingExternal)
        e: No description available (ProfileH2oKubernetes)
        f: No description available (ProfileDriverlessKubernetes)
        g: No description available (Permission)
        h: No description available (Event)
        i: No description available (KubernetesVolumeHostPath)
        j: No description available (KubernetesVolumeSecret)
        k: No description available (KubernetesVolumeConfigMap)
        l: No description available (KubernetesVolumePvc)
        m: No description available (KubernetesVolumeNfs)
        n: No description available (KubernetesVolumeCsi)
        """
        request = {
        }
        response = self.call("PriorityList", request)
        return response['a'], response['b'], response['c'], response['d'], response['e'], response['f'], response['g'], response['h'], response['i'], response['j'], response['k'], response['l'], response['m'], response['n']
    
    def ping_server(self, input):
        """
        Ping the Enterprise Steam server

        Parameters:
        input: Message to send (string)

        Returns:
        output: Version of the Python/R API (string)
        """
        request = {
            'input': input
        }
        response = self.call("PingServer", request)
        return response['output']
    
    def get_config(self):
        """
        Get Enterprise Steam start up configurations

        Parameters:

        Returns:
        config: An object containing Enterprise Steam startup configurations (Config)
        """
        request = {
        }
        response = self.call("GetConfig", request)
        return response['config']
    
    def set_authentication(self, enabled_type, ldap, saml, pam, oidc):
        """
        Set authentication config

        Parameters:
        enabled_type: No description available (string)
        ldap: No description available (LdapConfig)
        saml: No description available (SamlConfig)
        pam: No description available (PamConfig)
        oidc: No description available (OidcConfig)

        Returns:None
        """
        request = {
            'enabled_type': enabled_type,
            'ldap': ldap,
            'saml': saml,
            'pam': pam,
            'oidc': oidc
        }
        response = self.call("SetAuthentication", request)
        return 
    
    def get_authentication(self):
        """
        Get authentication config

        Parameters:

        Returns:
        enabled_type: No description available (string)
        ldap: No description available (LdapConfig)
        saml: No description available (SamlConfig)
        pam: No description available (PamConfig)
        oidc: No description available (OidcConfig)
        """
        request = {
        }
        response = self.call("GetAuthentication", request)
        return response['enabled_type'], response['ldap'], response['saml'], response['pam'], response['oidc']
    
    def create_ldap_connection(self, ldap):
        """
        Create new Ldap connection

        Parameters:
        ldap: No description available (LdapConnection)

        Returns:
        id: No description available (int64)
        """
        request = {
            'ldap': ldap
        }
        response = self.call("CreateLdapConnection", request)
        return response['id']
    
    def get_ldap_connections(self):
        """
        Get existing ldap connections

        Parameters:

        Returns:
        connections: No description available (LdapConnection)
        """
        request = {
        }
        response = self.call("GetLdapConnections", request)
        return response['connections']
    
    def update_ldap_connection(self, ldap):
        """
        Update existing ldap connection

        Parameters:
        ldap: No description available (LdapConnection)

        Returns:None
        """
        request = {
            'ldap': ldap
        }
        response = self.call("UpdateLdapConnection", request)
        return 
    
    def delete_ldap_connection(self, id):
        """
        Delete existing ldap connection

        Parameters:
        id: No description available (int64)

        Returns:None
        """
        request = {
            'id': id
        }
        response = self.call("DeleteLdapConnection", request)
        return 
    
    def swap_ldap_connection_priorities(self, id_a, id_b):
        """
        Swap priorities between two ldap connections

        Parameters:
        id_a: No description available (int64)
        id_b: No description available (int64)

        Returns:None
        """
        request = {
            'id_a': id_a,
            'id_b': id_b
        }
        response = self.call("SwapLdapConnectionPriorities", request)
        return 
    
    def test_ldap_config(self, config):
        """
        Test LDAP security configurations

        Parameters:
        config: No description available (LdapConfig)

        Returns:
        count: No description available (int)
        groups: No description available (LdapGroup)
        """
        request = {
            'config': config
        }
        response = self.call("TestLdapConfig", request)
        return response['count'], response['groups']
    
    def get_roles_config(self):
        """
        Get roles config

        Parameters:

        Returns:
        config: No description available (RolesConfig)
        """
        request = {
        }
        response = self.call("GetRolesConfig", request)
        return response['config']
    
    def set_roles_config(self, config):
        """
        Set roles config

        Parameters:
        config: No description available (RolesConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetRolesConfig", request)
        return 
    
    def get_auth_type(self):
        """
        Get enabled auth type

        Parameters:

        Returns:
        enabled_type: No description available (string)
        """
        request = {
        }
        response = self.call("GetAuthType", request)
        return response['enabled_type']
    
    def set_hadoop_config(self, config):
        """
        Set configuration for YARN deployment backend

        Parameters:
        config: No description available (HadoopConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetHadoopConfig", request)
        return 
    
    def get_hadoop_config(self):
        """
        Get configuration for YARN deployment backend

        Parameters:

        Returns:
        config: No description available (HadoopConfig)
        hadoop_info: No description available (HadoopInfo)
        """
        request = {
        }
        response = self.call("GetHadoopConfig", request)
        return response['config'], response['hadoop_info']
    
    def test_generate_hive_token(self, username):
        """
        Test generation of Hive token

        Parameters:
        username: No description available (string)

        Returns:None
        """
        request = {
            'username': username
        }
        response = self.call("TestGenerateHiveToken", request)
        return 
    
    def set_kubernetes_config(self, config):
        """
        Set configuration for Kubernetes deployment backend

        Parameters:
        config: No description available (KubernetesConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetKubernetesConfig", request)
        return 
    
    def get_kubernetes_config(self):
        """
        Get configuration for Kubernetes deployment backend

        Parameters:

        Returns:
        config: No description available (KubernetesConfig)
        kubernetes_info: No description available (KubernetesInfo)
        """
        request = {
        }
        response = self.call("GetKubernetesConfig", request)
        return response['config'], response['kubernetes_info']
    
    def set_kubernetes_hdfs_config(self, config):
        """
        Set configuration for HDFS on Kubernetes

        Parameters:
        config: No description available (KubernetesHdfsConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetKubernetesHdfsConfig", request)
        return 
    
    def get_kubernetes_hdfs_config(self):
        """
        Get configuration for HDFS on Kubernetes

        Parameters:

        Returns:
        config: No description available (KubernetesHdfsConfig)
        """
        request = {
        }
        response = self.call("GetKubernetesHdfsConfig", request)
        return response['config']
    
    def create_h2o_startup_parameter(self, parameter):
        """
        Create a global startup parameter for launching H2O clusters

        Parameters:
        parameter: No description available (NewH2oStartupParameter)

        Returns:None
        """
        request = {
            'parameter': parameter
        }
        response = self.call("CreateH2oStartupParameter", request)
        return 
    
    def get_h2o_startup_parameters(self):
        """
        Get a global startup parameter for launching H2O clusters

        Parameters:

        Returns:
        parameter: No description available (H2oStartupParameter)
        """
        request = {
        }
        response = self.call("GetH2oStartupParameters", request)
        return response['parameter']
    
    def update_h2o_startup_parameter(self, id, parameter):
        """
        Update a global startup parameter for launching H2O clusters

        Parameters:
        id: No description available (int64)
        parameter: No description available (NewH2oStartupParameter)

        Returns:None
        """
        request = {
            'id': id,
            'parameter': parameter
        }
        response = self.call("UpdateH2oStartupParameter", request)
        return 
    
    def remove_h2o_startup_parameter(self, id):
        """
        Delete a global startup parameter for launching H2O clusters

        Parameters:
        id: No description available (int64)

        Returns:None
        """
        request = {
            'id': id
        }
        response = self.call("RemoveH2oStartupParameter", request)
        return 
    
    def launch_h2o_cluster(self, parameters):
        """
        Launch H2O cluster

        Parameters:
        parameters: No description available (LaunchH2oClusterParameters)

        Returns:
        id: No description available (int64)
        """
        request = {
            'parameters': parameters
        }
        response = self.call("LaunchH2oCluster", request)
        return response['id']
    
    def start_h2o_cluster(self, id, parameters):
        """
        Start stopped H2O cluster

        Parameters:
        id: No description available (int64)
        parameters: No description available (LaunchH2oClusterParameters)

        Returns:None
        """
        request = {
            'id': id,
            'parameters': parameters
        }
        response = self.call("StartH2oCluster", request)
        return 
    
    def get_h2o_clusters(self):
        """
        Get all my H2O clusters

        Parameters:

        Returns:
        clusters: No description available (H2oCluster)
        """
        request = {
        }
        response = self.call("GetH2oClusters", request)
        return response['clusters']
    
    def get_h2o_cluster(self, cluster_id):
        """
        Get H2O cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        cluster: No description available (H2oCluster)
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("GetH2oCluster", request)
        return response['cluster']
    
    def get_h2o_cluster_by_name(self, name):
        """
        Get H2O cluster by name

        Parameters:
        name: No description available (string)

        Returns:
        cluster: No description available (H2oCluster)
        """
        request = {
            'name': name
        }
        response = self.call("GetH2oClusterByName", request)
        return response['cluster']
    
    def stop_h2o_cluster(self, cluster_id, should_save):
        """
        Stop H2O cluster

        Parameters:
        cluster_id: No description available (int64)
        should_save: No description available (bool)

        Returns:None
        """
        request = {
            'cluster_id': cluster_id,
            'should_save': should_save
        }
        response = self.call("StopH2oCluster", request)
        return 
    
    def fail_h2o_cluster(self, cluster_id):
        """
        Mark H2O cluster as failed

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("FailH2oCluster", request)
        return 
    
    def delete_h2o_cluster(self, cluster_id):
        """
        Delete H2O cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("DeleteH2oCluster", request)
        return 
    
    def get_h2o_cluster_logs(self, cluster_id):
        """
        Get H2O cluster logs

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        logs: No description available (H2oClusterLogs)
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("GetH2oClusterLogs", request)
        return response['logs']
    
    def get_h2o_config(self):
        """
        Get H2O configuration

        Parameters:

        Returns:
        config: No description available (H2oConfig)
        """
        request = {
        }
        response = self.call("GetH2oConfig", request)
        return response['config']
    
    def set_h2o_config(self, config):
        """
        Set H2O configuration

        Parameters:
        config: No description available (H2oConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetH2oConfig", request)
        return 
    
    def import_h2o_engine(self, path):
        """
        Import engine from server path

        Parameters:
        path: No description available (string)

        Returns:None
        """
        request = {
            'path': path
        }
        response = self.call("ImportH2oEngine", request)
        return 
    
    def get_h2o_engine(self, engine_id):
        """
        Get H2O engine details

        Parameters:
        engine_id: No description available (int64)

        Returns:
        engine: No description available (H2oEngine)
        """
        request = {
            'engine_id': engine_id
        }
        response = self.call("GetH2oEngine", request)
        return response['engine']
    
    def get_h2o_engine_by_version(self, version):
        """
        Get an H2O engine by a version substring

        Parameters:
        version: No description available (string)

        Returns:
        engine: No description available (H2oEngine)
        """
        request = {
            'version': version
        }
        response = self.call("GetH2oEngineByVersion", request)
        return response['engine']
    
    def get_h2o_engines(self):
        """
        List H2O engines

        Parameters:

        Returns:
        engines: No description available (H2oEngine)
        """
        request = {
        }
        response = self.call("GetH2oEngines", request)
        return response['engines']
    
    def delete_h2o_engine(self, engine_id):
        """
        Delete an H2O engine

        Parameters:
        engine_id: No description available (int64)

        Returns:None
        """
        request = {
            'engine_id': engine_id
        }
        response = self.call("DeleteH2oEngine", request)
        return 
    
    def get_all_entity_types(self):
        """
        List all entity types

        Parameters:

        Returns:
        entity_types: A list of Enterprise Steam entity types. (EntityType)
        """
        request = {
        }
        response = self.call("GetAllEntityTypes", request)
        return response['entity_types']
    
    def get_all_permissions(self):
        """
        List all permissions

        Parameters:

        Returns:
        permissions: A list of Enterprise Steam permissions. (Permission)
        """
        request = {
        }
        response = self.call("GetAllPermissions", request)
        return response['permissions']
    
    def get_permissions_for_role(self, role_id):
        """
        List permissions for a role

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:
        permissions: A list of Enterprise Steam permissions. (Permission)
        """
        request = {
            'role_id': role_id
        }
        response = self.call("GetPermissionsForRole", request)
        return response['permissions']
    
    def get_permissions_for_identity(self, identity_id):
        """
        List permissions for an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:
        permissions: A list of Enterprise Steam permissions. (Permission)
        """
        request = {
            'identity_id': identity_id
        }
        response = self.call("GetPermissionsForIdentity", request)
        return response['permissions']
    
    def get_estimated_cluster_memory(self, parameters):
        """
        Get estimated cluster memory

        Parameters:
        parameters: No description available (DatasetParameters)

        Returns:
        cluster_memory: No description available (EstimatedClusterMemory)
        """
        request = {
            'parameters': parameters
        }
        response = self.call("GetEstimatedClusterMemory", request)
        return response['cluster_memory']
    
    def create_role(self, name, description):
        """
        Create a role

        Parameters:
        name: A string name. (string)
        description: A string description (string)

        Returns:
        role_id: Integer ID of the role in Enterprise Steam. (int64)
        """
        request = {
            'name': name,
            'description': description
        }
        response = self.call("CreateRole", request)
        return response['role_id']
    
    def get_roles(self, offset, limit):
        """
        List roles

        Parameters:
        offset: An offset uint start the search on. (uint)
        limit: The maximum uint objects. (uint)

        Returns:
        roles: A list of Enterprise Steam roles. (Role)
        """
        request = {
            'offset': offset,
            'limit': limit
        }
        response = self.call("GetRoles", request)
        return response['roles']
    
    def get_roles_for_identity(self, identity_id):
        """
        List roles for an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:
        roles: A list of Enterprise Steam roles. (Role)
        """
        request = {
            'identity_id': identity_id
        }
        response = self.call("GetRolesForIdentity", request)
        return response['roles']
    
    def get_role(self, role_id):
        """
        Get role details

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:
        role: A Enterprise Steam role. (Role)
        """
        request = {
            'role_id': role_id
        }
        response = self.call("GetRole", request)
        return response['role']
    
    def get_role_by_name(self, name):
        """
        Get role details by name

        Parameters:
        name: A role name. (string)

        Returns:
        role: A Enterprise Steam role. (Role)
        """
        request = {
            'name': name
        }
        response = self.call("GetRoleByName", request)
        return response['role']
    
    def update_role(self, role_id, name, description):
        """
        Update a role

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)
        name: A string name. (string)
        description: A string description (string)

        Returns:None
        """
        request = {
            'role_id': role_id,
            'name': name,
            'description': description
        }
        response = self.call("UpdateRole", request)
        return 
    
    def delete_role(self, role_id):
        """
        Delete a role

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'role_id': role_id
        }
        response = self.call("DeleteRole", request)
        return 
    
    def link_role_with_permissions(self, role_id, permission_ids):
        """
        Link a role with permissions

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)
        permission_ids: A list of Integer IDs for permissions in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'role_id': role_id,
            'permission_ids': permission_ids
        }
        response = self.call("LinkRoleWithPermissions", request)
        return 
    
    def link_role_with_permission(self, role_id, permission_id):
        """
        Link a role with a permission

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)
        permission_id: Integer ID of a permission in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'role_id': role_id,
            'permission_id': permission_id
        }
        response = self.call("LinkRoleWithPermission", request)
        return 
    
    def unlink_role_from_permission(self, role_id, permission_id):
        """
        Unlink a role from a permission

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)
        permission_id: Integer ID of a permission in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'role_id': role_id,
            'permission_id': permission_id
        }
        response = self.call("UnlinkRoleFromPermission", request)
        return 
    
    def create_workgroup(self, name, description):
        """
        Create a workgroup

        Parameters:
        name: A string name. (string)
        description: A string description (string)

        Returns:
        workgroup_id: Integer ID of the workgroup in Enterprise Steam. (int64)
        """
        request = {
            'name': name,
            'description': description
        }
        response = self.call("CreateWorkgroup", request)
        return response['workgroup_id']
    
    def get_workgroups(self, offset, limit):
        """
        List workgroups

        Parameters:
        offset: An offset uint start the search on. (uint)
        limit: The maximum uint objects. (uint)

        Returns:
        workgroups: A list of workgroups in Enterprise Steam. (Workgroup)
        """
        request = {
            'offset': offset,
            'limit': limit
        }
        response = self.call("GetWorkgroups", request)
        return response['workgroups']
    
    def get_workgroups_for_identity(self, identity_id):
        """
        List workgroups for an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:
        workgroups: A list of workgroups in Enterprise Steam. (Workgroup)
        """
        request = {
            'identity_id': identity_id
        }
        response = self.call("GetWorkgroupsForIdentity", request)
        return response['workgroups']
    
    def get_workgroup(self, workgroup_id):
        """
        Get workgroup details

        Parameters:
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:
        workgroup: A workgroup in Enterprise Steam. (Workgroup)
        """
        request = {
            'workgroup_id': workgroup_id
        }
        response = self.call("GetWorkgroup", request)
        return response['workgroup']
    
    def get_workgroup_by_name(self, name):
        """
        Get workgroup details by name

        Parameters:
        name: A string name. (string)

        Returns:
        workgroup: A workgroup in Enterprise Steam. (Workgroup)
        """
        request = {
            'name': name
        }
        response = self.call("GetWorkgroupByName", request)
        return response['workgroup']
    
    def update_workgroup(self, workgroup_id, name, description):
        """
        Update a workgroup

        Parameters:
        workgroup_id: Integer ID of a workgrou in Enterprise Steam. (int64)
        name: A string name. (string)
        description: A string description (string)

        Returns:None
        """
        request = {
            'workgroup_id': workgroup_id,
            'name': name,
            'description': description
        }
        response = self.call("UpdateWorkgroup", request)
        return 
    
    def delete_workgroup(self, workgroup_id):
        """
        Delete a workgroup

        Parameters:
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'workgroup_id': workgroup_id
        }
        response = self.call("DeleteWorkgroup", request)
        return 
    
    def create_identity(self, name, password, yarn_queue):
        """
        Create an identity

        Parameters:
        name: A string name. (string)
        password: A string password (string)
        yarn_queue: No description available (string)

        Returns:
        identity_id: Integer ID of the identity in Enterprise Steam. (int64)
        """
        request = {
            'name': name,
            'password': password,
            'yarn_queue': yarn_queue
        }
        response = self.call("CreateIdentity", request)
        return response['identity_id']
    
    def get_identities(self, offset, limit):
        """
        List identities

        Parameters:
        offset: An offset uint start the search on. (uint)
        limit: The maximum uint objects. (uint)

        Returns:
        identities: A list of identities in Enterprise Steam. (Identity)
        """
        request = {
            'offset': offset,
            'limit': limit
        }
        response = self.call("GetIdentities", request)
        return response['identities']
    
    def get_identities_for_workgroup(self, workgroup_id):
        """
        List identities for a workgroup

        Parameters:
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:
        identities: A list of identities in Enterprise Steam. (Identity)
        """
        request = {
            'workgroup_id': workgroup_id
        }
        response = self.call("GetIdentitiesForWorkgroup", request)
        return response['identities']
    
    def get_identities_for_role(self, role_id):
        """
        List identities for a role

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:
        identities: A list of identities in Enterprise Steam. (Identity)
        """
        request = {
            'role_id': role_id
        }
        response = self.call("GetIdentitiesForRole", request)
        return response['identities']
    
    def get_identities_for_entity(self, entity_type, entity_id):
        """
        Get a list of identities and roles with access to an entity

        Parameters:
        entity_type: An entity type ID. (int64)
        entity_id: An entity ID. (int64)

        Returns:
        users: A list of identites and roles (UserRole)
        """
        request = {
            'entity_type': entity_type,
            'entity_id': entity_id
        }
        response = self.call("GetIdentitiesForEntity", request)
        return response['users']
    
    def get_identity(self, identity_id):
        """
        Get identity details

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:
        identity: An identity in Enterprise Steam. (Identity)
        """
        request = {
            'identity_id': identity_id
        }
        response = self.call("GetIdentity", request)
        return response['identity']
    
    def get_identity_by_name(self, name):
        """
        Get identity details by name

        Parameters:
        name: An identity name. (string)

        Returns:
        identity: An identity in Enterprise Steam. (Identity)
        """
        request = {
            'name': name
        }
        response = self.call("GetIdentityByName", request)
        return response['identity']
    
    def update_identity(self, identity_id, password):
        """
        Update an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        password: Password for identity (string)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'password': password
        }
        response = self.call("UpdateIdentity", request)
        return 
    
    def update_identity_auth(self, identity_id, auth_type):
        """
        Update an identity login type

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        auth_type: The auth type to use for login (string)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'auth_type': auth_type
        }
        response = self.call("UpdateIdentityAuth", request)
        return 
    
    def update_identity_yarn(self, identity_id, yarn_queue):
        """
        Update yarn queues of the idenity

        Parameters:
        identity_id: No description available (int64)
        yarn_queue: No description available (string)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'yarn_queue': yarn_queue
        }
        response = self.call("UpdateIdentityYarn", request)
        return 
    
    def update_identity_uid_gid(self, identity_id, uid, gid):
        """
        Update UID and GID of identity

        Parameters:
        identity_id: No description available (int64)
        uid: No description available (int64)
        gid: No description available (int64)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'uid': uid,
            'gid': gid
        }
        response = self.call("UpdateIdentityUidGid", request)
        return 
    
    def activate_identity(self, identity_id):
        """
        Activate an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': identity_id
        }
        response = self.call("ActivateIdentity", request)
        return 
    
    def deactivate_identity(self, identity_id):
        """
        Deactivate an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': identity_id
        }
        response = self.call("DeactivateIdentity", request)
        return 
    
    def link_identity_with_workgroup(self, identity_id, workgroup_id):
        """
        Link an identity with a workgroup

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'workgroup_id': workgroup_id
        }
        response = self.call("LinkIdentityWithWorkgroup", request)
        return 
    
    def unlink_identity_from_workgroup(self, identity_id, workgroup_id):
        """
        Unlink an identity from a workgroup

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'workgroup_id': workgroup_id
        }
        response = self.call("UnlinkIdentityFromWorkgroup", request)
        return 
    
    def link_identity_with_role(self, identity_id, role_id):
        """
        Link an identity with a role

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'role_id': role_id
        }
        response = self.call("LinkIdentityWithRole", request)
        return 
    
    def unlink_identity_from_role(self, identity_id, role_id):
        """
        Unlink an identity from a role

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'role_id': role_id
        }
        response = self.call("UnlinkIdentityFromRole", request)
        return 
    
    def share_entity(self, kind, workgroup_id, entity_type_id, entity_id):
        """
        Share an entity with a workgroup

        Parameters:
        kind: Type of permission. Can be view, edit, or own. (string)
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)
        entity_type_id: Integer ID for the type of entity. (int64)
        entity_id: Integer ID for an entity in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'kind': kind,
            'workgroup_id': workgroup_id,
            'entity_type_id': entity_type_id,
            'entity_id': entity_id
        }
        response = self.call("ShareEntity", request)
        return 
    
    def get_privileges(self, entity_type_id, entity_id):
        """
        List privileges for an entity

        Parameters:
        entity_type_id: Integer ID for the type of entity. (int64)
        entity_id: Integer ID for an entity in Enterprise Steam. (int64)

        Returns:
        privileges: A list of entity privileges (EntityPrivilege)
        """
        request = {
            'entity_type_id': entity_type_id,
            'entity_id': entity_id
        }
        response = self.call("GetPrivileges", request)
        return response['privileges']
    
    def unshare_entity(self, kind, workgroup_id, entity_type_id, entity_id):
        """
        Unshare an entity

        Parameters:
        kind: Type of permission. Can be view, edit, or own. (string)
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)
        entity_type_id: Integer ID for the type of entity. (int64)
        entity_id: Integer ID for an entity in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'kind': kind,
            'workgroup_id': workgroup_id,
            'entity_type_id': entity_type_id,
            'entity_id': entity_id
        }
        response = self.call("UnshareEntity", request)
        return 
    
    def get_history(self, entity_type_id, entity_id, offset, limit):
        """
        List audit trail records for an entity

        Parameters:
        entity_type_id: Integer ID for the type of entity. (int64)
        entity_id: Integer ID for an entity in Enterprise Steam. (int64)
        offset: An offset uint start the search on. (uint)
        limit: The maximum uint objects. (uint)

        Returns:
        history: A list of actions performed on the entity. (EntityHistory)
        """
        request = {
            'entity_type_id': entity_type_id,
            'entity_id': entity_id,
            'offset': offset,
            'limit': limit
        }
        response = self.call("GetHistory", request)
        return response['history']
    
    def set_license(self, license):
        """
        Set license from license text

        Parameters:
        license: No description available (string)

        Returns:None
        """
        request = {
            'license': license
        }
        response = self.call("SetLicense", request)
        return 
    
    def get_license(self):
        """
        Get the current provided license

        Parameters:

        Returns:
        license: No description available (License)
        """
        request = {
        }
        response = self.call("GetLicense", request)
        return response['license']
    
    def delete_license(self):
        """
        Delete the current license

        Parameters:

        Returns:None
        """
        request = {
        }
        response = self.call("DeleteLicense", request)
        return 
    
    def invalidate_ldap_cache(self):
        """
        Invalidate LDAP cache

        Parameters:

        Returns:None
        """
        request = {
        }
        response = self.call("InvalidateLdapCache", request)
        return 
    
    def change_my_password(self, password):
        """
        Change my password

        Parameters:
        password: No description available (string)

        Returns:None
        """
        request = {
            'password': password
        }
        response = self.call("ChangeMyPassword", request)
        return 
    
    def reset_password_for_identity(self, identity_id):
        """
        Reset user's password and get a new one'

        Parameters:
        identity_id: No description available (int64)

        Returns:
        password: No description available (string)
        """
        request = {
            'identity_id': identity_id
        }
        response = self.call("ResetPasswordForIdentity", request)
        return response['password']
    
    def generate_identity_token(self):
        """
        Generate new login token for identity

        Parameters:

        Returns:
        token: No description available (string)
        """
        request = {
        }
        response = self.call("GenerateIdentityToken", request)
        return response['token']
    
    def set_identity_admin_override(self, identity_id, is_admin):
        """
        Set identity as admin overriding roles

        Parameters:
        identity_id: No description available (int64)
        is_admin: No description available (bool)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'is_admin': is_admin
        }
        response = self.call("SetIdentityAdminOverride", request)
        return 
    
    def terminate_identity_resources(self, username):
        """
        Terminates all clusters and instances owned by the user

        Parameters:
        username: No description available (string)

        Returns:None
        """
        request = {
            'username': username
        }
        response = self.call("TerminateIdentityResources", request)
        return 
    
    def get_sparkling_clusters(self):
        """
        Get Sparkling Water clusters

        Parameters:

        Returns:
        clusters: No description available (SparklingCluster)
        """
        request = {
        }
        response = self.call("GetSparklingClusters", request)
        return response['clusters']
    
    def get_sparkling_cluster(self, cluster_id):
        """
        Get Sparkling Water cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        cluster: No description available (SparklingCluster)
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("GetSparklingCluster", request)
        return response['cluster']
    
    def get_sparkling_cluster_by_name(self, name):
        """
        Get Sparkling Water cluster by name

        Parameters:
        name: No description available (string)

        Returns:
        cluster: No description available (SparklingCluster)
        """
        request = {
            'name': name
        }
        response = self.call("GetSparklingClusterByName", request)
        return response['cluster']
    
    def get_sparkling_cluster_logs(self, cluster_id):
        """
        Get Sparkling cluster logs

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        logs: No description available (SparklingClusterLogs)
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("GetSparklingClusterLogs", request)
        return response['logs']
    
    def launch_sparkling_cluster(self, parameters):
        """
        Launch Sparkling Water cluster

        Parameters:
        parameters: No description available (LaunchSparklingClusterParameters)

        Returns:
        cluster_id: No description available (int64)
        """
        request = {
            'parameters': parameters
        }
        response = self.call("LaunchSparklingCluster", request)
        return response['cluster_id']
    
    def start_sparkling_cluster(self, id, parameters):
        """
        Start stopped Sparkling Water cluster

        Parameters:
        id: No description available (int64)
        parameters: No description available (LaunchSparklingClusterParameters)

        Returns:None
        """
        request = {
            'id': id,
            'parameters': parameters
        }
        response = self.call("StartSparklingCluster", request)
        return 
    
    def stop_sparkling_cluster(self, cluster_id, should_save):
        """
        Stop Sparkling Water cluster

        Parameters:
        cluster_id: No description available (int64)
        should_save: No description available (bool)

        Returns:None
        """
        request = {
            'cluster_id': cluster_id,
            'should_save': should_save
        }
        response = self.call("StopSparklingCluster", request)
        return 
    
    def fail_sparkling_cluster(self, cluster_id):
        """
        Mark cluster as failed

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("FailSparklingCluster", request)
        return 
    
    def delete_sparkling_cluster(self, cluster_id):
        """
        Delete Sparkling Water cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("DeleteSparklingCluster", request)
        return 
    
    def send_sparkling_statement(self, cluster_id, statement, statement_kind):
        """
        Send statement to Sparkling Water cluster

        Parameters:
        cluster_id: No description available (int64)
        statement: No description available (string)
        statement_kind: No description available (string)

        Returns:
        response: No description available (string)
        """
        request = {
            'cluster_id': cluster_id,
            'statement': statement,
            'statement_kind': statement_kind
        }
        response = self.call("SendSparklingStatement", request)
        return response['response']
    
    def get_sparkling_config(self):
        """
        Get Sparkling Water configuration

        Parameters:

        Returns:
        config: No description available (SparklingConfig)
        """
        request = {
        }
        response = self.call("GetSparklingConfig", request)
        return response['config']
    
    def set_sparkling_config(self, config):
        """
        Set Sparkling Water configuration

        Parameters:
        config: No description available (SparklingConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetSparklingConfig", request)
        return 
    
    def get_sparkling_engines(self):
        """
        List sparkling engines

        Parameters:

        Returns:
        engines: No description available (SparklingEngine)
        """
        request = {
        }
        response = self.call("GetSparklingEngines", request)
        return response['engines']
    
    def import_sparkling_engine(self, path):
        """
        Import sparkling engine from server path

        Parameters:
        path: No description available (string)

        Returns:None
        """
        request = {
            'path': path
        }
        response = self.call("ImportSparklingEngine", request)
        return 
    
    def get_sparkling_engine(self, engine_id):
        """
        Get sparkling engine details

        Parameters:
        engine_id: No description available (int64)

        Returns:
        engine: No description available (SparklingEngine)
        """
        request = {
            'engine_id': engine_id
        }
        response = self.call("GetSparklingEngine", request)
        return response['engine']
    
    def get_sparkling_engine_by_version(self, version):
        """
        Get a sparkling engine by a version substring

        Parameters:
        version: No description available (string)

        Returns:
        sparkling_engine_id: No description available (int64)
        h2o_engine_id: No description available (int64)
        """
        request = {
            'version': version
        }
        response = self.call("GetSparklingEngineByVersion", request)
        return response['sparkling_engine_id'], response['h2o_engine_id']
    
    def delete_sparkling_engine(self, engine_id):
        """
        Delete a sparkling engine

        Parameters:
        engine_id: No description available (int64)

        Returns:None
        """
        request = {
            'engine_id': engine_id
        }
        response = self.call("DeleteSparklingEngine", request)
        return 
    
    def get_python_environment(self, environment_id):
        """
        Get python environment details

        Parameters:
        environment_id: No description available (int64)

        Returns:
        environment: No description available (PythonEnvironment)
        """
        request = {
            'environment_id': environment_id
        }
        response = self.call("GetPythonEnvironment", request)
        return response['environment']
    
    def get_python_environment_by_name(self, environment_name):
        """
        Get python environment details by environment name

        Parameters:
        environment_name: No description available (string)

        Returns:
        environment: No description available (PythonEnvironment)
        """
        request = {
            'environment_name': environment_name
        }
        response = self.call("GetPythonEnvironmentByName", request)
        return response['environment']
    
    def get_python_environments(self):
        """
        Get python environments available to current user

        Parameters:

        Returns:
        environments: No description available (PythonEnvironment)
        """
        request = {
        }
        response = self.call("GetPythonEnvironments", request)
        return response['environments']
    
    def create_python_environment(self, name, conda_pack_archive_name, pyspark_python_path, profile_ids):
        """
        Create new python environment

        Parameters:
        name: No description available (string)
        conda_pack_archive_name: No description available (string)
        pyspark_python_path: No description available (string)
        profile_ids: No description available (int64)

        Returns:
        environment_id: No description available (int64)
        """
        request = {
            'name': name,
            'conda_pack_archive_name': conda_pack_archive_name,
            'pyspark_python_path': pyspark_python_path,
            'profile_ids': profile_ids
        }
        response = self.call("CreatePythonEnvironment", request)
        return response['environment_id']
    
    def delete_python_environment(self, environment_id):
        """
        Delete python environment

        Parameters:
        environment_id: No description available (int64)

        Returns:None
        """
        request = {
            'environment_id': environment_id
        }
        response = self.call("DeletePythonEnvironment", request)
        return 
    
    def create_profile(self, profile):
        """
        Create new profile

        Parameters:
        profile: No description available (Profile)

        Returns:
        profile_id: No description available (int64)
        """
        request = {
            'profile': profile
        }
        response = self.call("CreateProfile", request)
        return response['profile_id']
    
    def get_profile(self, profile_id):
        """
        Get existing profile by ID

        Parameters:
        profile_id: No description available (int64)

        Returns:
        profile: No description available (Profile)
        """
        request = {
            'profile_id': profile_id
        }
        response = self.call("GetProfile", request)
        return response['profile']
    
    def get_profile_by_name(self, name):
        """
        Get existing profile by name

        Parameters:
        name: No description available (string)

        Returns:
        profile: No description available (Profile)
        """
        request = {
            'name': name
        }
        response = self.call("GetProfileByName", request)
        return response['profile']
    
    def get_profiles(self):
        """
        Get existing profiles by ID

        Parameters:

        Returns:
        profiles: No description available (Profile)
        """
        request = {
        }
        response = self.call("GetProfiles", request)
        return response['profiles']
    
    def get_profiles_for_identity(self, identity_id):
        """
        Get profiles for an identity

        Parameters:
        identity_id: No description available (int64)

        Returns:
        profiles: No description available (Profile)
        """
        request = {
            'identity_id': identity_id
        }
        response = self.call("GetProfilesForIdentity", request)
        return response['profiles']
    
    def update_profile(self, profile):
        """
        Update existing profile by ID

        Parameters:
        profile: No description available (Profile)

        Returns:None
        """
        request = {
            'profile': profile
        }
        response = self.call("UpdateProfile", request)
        return 
    
    def delete_profile(self, profile_id):
        """
        Delete existing profile by ID

        Parameters:
        profile_id: No description available (int64)

        Returns:None
        """
        request = {
            'profile_id': profile_id
        }
        response = self.call("DeleteProfile", request)
        return 
    
    def link_identity_with_profile(self, identity_id, profile_id):
        """
        Link an identity with a profile

        Parameters:
        identity_id: No description available (int64)
        profile_id: No description available (int64)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'profile_id': profile_id
        }
        response = self.call("LinkIdentityWithProfile", request)
        return 
    
    def unlink_identity_from_profile(self, identity_id, profile_id):
        """
        Unlink an identity from a profile

        Parameters:
        identity_id: No description available (int64)
        profile_id: No description available (int64)

        Returns:None
        """
        request = {
            'identity_id': identity_id,
            'profile_id': profile_id
        }
        response = self.call("UnlinkIdentityFromProfile", request)
        return 
    
    def get_profile_usage(self, profile_id):
        """
        Get profile usage statistics

        Parameters:
        profile_id: No description available (int64)

        Returns:
        profile_usage: No description available (ProfileUsage)
        """
        request = {
            'profile_id': profile_id
        }
        response = self.call("GetProfileUsage", request)
        return response['profile_usage']
    
    def get_driverless_instances(self):
        """
        Get my Driverless AI instances

        Parameters:

        Returns:
        instances: No description available (DriverlessInstance)
        """
        request = {
        }
        response = self.call("GetDriverlessInstances", request)
        return response['instances']
    
    def get_driverless_instance(self, name):
        """
        Get Driverless AI instance by name

        Parameters:
        name: No description available (string)

        Returns:
        instance: No description available (DriverlessInstance)
        """
        request = {
            'name': name
        }
        response = self.call("GetDriverlessInstance", request)
        return response['instance']
    
    def get_driverless_instance_created_by(self, name, created_by):
        """
        Get Driverless AI instance by name and user

        Parameters:
        name: No description available (string)
        created_by: No description available (string)

        Returns:
        instance: No description available (DriverlessInstance)
        """
        request = {
            'name': name,
            'created_by': created_by
        }
        response = self.call("GetDriverlessInstanceCreatedBy", request)
        return response['instance']
    
    def get_driverless_instance_by_id(self, id):
        """
        Get Driverless AI instance by ID

        Parameters:
        id: No description available (int64)

        Returns:
        instance: No description available (DriverlessInstance)
        """
        request = {
            'id': id
        }
        response = self.call("GetDriverlessInstanceByID", request)
        return response['instance']
    
    def launch_driverless_instance(self, parameters):
        """
        Launch Driverless AI instance

        Parameters:
        parameters: No description available (LaunchDriverlessInstanceParameters)

        Returns:
        instance_id: No description available (int64)
        """
        request = {
            'parameters': parameters
        }
        response = self.call("LaunchDriverlessInstance", request)
        return response['instance_id']
    
    def start_driverless_instance(self, instance_id, parameters):
        """
        Start Driverless AI instance

        Parameters:
        instance_id: No description available (int64)
        parameters: No description available (LaunchDriverlessInstanceParameters)

        Returns:None
        """
        request = {
            'instance_id': instance_id,
            'parameters': parameters
        }
        response = self.call("StartDriverlessInstance", request)
        return 
    
    def stop_driverless_instance(self, instance_id):
        """
        Stop Driverless AI instance

        Parameters:
        instance_id: No description available (int64)

        Returns:None
        """
        request = {
            'instance_id': instance_id
        }
        response = self.call("StopDriverlessInstance", request)
        return 
    
    def terminate_driverless_instance(self, instance_id):
        """
        Terminate Driverless AI instance

        Parameters:
        instance_id: No description available (int64)

        Returns:None
        """
        request = {
            'instance_id': instance_id
        }
        response = self.call("TerminateDriverlessInstance", request)
        return 
    
    def fail_driverless_instance(self, instance_id):
        """
        Mark Driverless AI instance as failed

        Parameters:
        instance_id: No description available (int64)

        Returns:None
        """
        request = {
            'instance_id': instance_id
        }
        response = self.call("FailDriverlessInstance", request)
        return 
    
    def upgrade_driverless_instance(self, instance_id, version):
        """
        Upgrade Driverless AI instance

        Parameters:
        instance_id: No description available (int64)
        version: No description available (string)

        Returns:None
        """
        request = {
            'instance_id': instance_id,
            'version': version
        }
        response = self.call("UpgradeDriverlessInstance", request)
        return 
    
    def get_driverless_instance_logs(self, instance_id):
        """
        Get Driverless AI instance logs

        Parameters:
        instance_id: No description available (int64)

        Returns:
        logs: No description available (DriverlessInstanceLogs)
        """
        request = {
            'instance_id': instance_id
        }
        response = self.call("GetDriverlessInstanceLogs", request)
        return response['logs']
    
    def get_driverless_engines(self):
        """
        Get Driverless AI engines

        Parameters:

        Returns:
        engines: No description available (DriverlessEngine)
        """
        request = {
        }
        response = self.call("GetDriverlessEngines", request)
        return response['engines']
    
    def set_driverless_config(self, config):
        """
        Set Driverless AI config

        Parameters:
        config: No description available (DriverlessConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetDriverlessConfig", request)
        return 
    
    def get_driverless_config(self):
        """
        Get Driverless AI config

        Parameters:

        Returns:
        config: No description available (DriverlessConfig)
        """
        request = {
        }
        response = self.call("GetDriverlessConfig", request)
        return response['config']
    
    def get_driverless_client(self):
        """
        Get Driverless AI Python client info

        Parameters:

        Returns:
        client: No description available (DriverlessClient)
        """
        request = {
        }
        response = self.call("GetDriverlessClient", request)
        return response['client']
    
    def set_driverless_instance_name(self, instance_id, name):
        """
        Change the name of a Driverless AI Instance

        Parameters:
        instance_id: No description available (int64)
        name: No description available (string)

        Returns:None
        """
        request = {
            'instance_id': instance_id,
            'name': name
        }
        response = self.call("SetDriverlessInstanceName", request)
        return 
    
    def set_driverless_instance_owner(self, instance_id, name):
        """
        Change the owner of a Driverless AI Instance

        Parameters:
        instance_id: No description available (int64)
        name: No description available (string)

        Returns:None
        """
        request = {
            'instance_id': instance_id,
            'name': name
        }
        response = self.call("SetDriverlessInstanceOwner", request)
        return 
    
    def get_driverless_kubernetes_engines(self):
        """
        Get engines for Driverless AI on Kubernetes

        Parameters:

        Returns:
        engines: No description available (DriverlessKubernetesEngine)
        """
        request = {
        }
        response = self.call("GetDriverlessKubernetesEngines", request)
        return response['engines']
    
    def add_driverless_kubernetes_engine(self, engine):
        """
        Add engine for Driverless AI on Kubernetes

        Parameters:
        engine: No description available (DriverlessKubernetesEngine)

        Returns:None
        """
        request = {
            'engine': engine
        }
        response = self.call("AddDriverlessKubernetesEngine", request)
        return 
    
    def remove_driverless_kubernetes_engine(self, version):
        """
        Remove engine for Driverless AI on Kubernetes

        Parameters:
        version: No description available (string)

        Returns:None
        """
        request = {
            'version': version
        }
        response = self.call("RemoveDriverlessKubernetesEngine", request)
        return 
    
    def launch_driverless_multinode(self, parameters):
        """
        Launch Driverless AI multinode cluster

        Parameters:
        parameters: No description available (LaunchDriverlessMultinodeParameters)

        Returns:
        instance_id: No description available (int64)
        """
        request = {
            'parameters': parameters
        }
        response = self.call("LaunchDriverlessMultinode", request)
        return response['instance_id']
    
    def get_driverless_multinode(self, name):
        """
        Get Driverless AI multinode cluster by name

        Parameters:
        name: No description available (string)

        Returns:
        cluster: No description available (DriverlessMultinode)
        """
        request = {
            'name': name
        }
        response = self.call("GetDriverlessMultinode", request)
        return response['cluster']
    
    def get_driverless_multinodes(self):
        """
        Get all Driverless AI multinode clusters

        Parameters:

        Returns:
        cluster: No description available (DriverlessMultinode)
        """
        request = {
        }
        response = self.call("GetDriverlessMultinodes", request)
        return response['cluster']
    
    def terminate_driverless_multinode(self, name):
        """
        Terminate Driverless AI multinode cluster

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': name
        }
        response = self.call("TerminateDriverlessMultinode", request)
        return 
    
    def restart_driverless_multinode(self, name):
        """
        Restart failed Driverless AI multinode cluster

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': name
        }
        response = self.call("RestartDriverlessMultinode", request)
        return 
    
    def set_security_config(self, config):
        """
        Set security configuration

        Parameters:
        config: No description available (SecurityConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetSecurityConfig", request)
        return 
    
    def get_security_config(self):
        """
        Set security configuration

        Parameters:

        Returns:
        config: No description available (SecurityConfig)
        """
        request = {
        }
        response = self.call("GetSecurityConfig", request)
        return response['config']
    
    def set_logging_config(self, config):
        """
        Set logging configuration

        Parameters:
        config: No description available (LoggingConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetLoggingConfig", request)
        return 
    
    def get_logging_config(self):
        """
        Get logging configuration

        Parameters:

        Returns:
        config: No description available (LoggingConfig)
        """
        request = {
        }
        response = self.call("GetLoggingConfig", request)
        return response['config']
    
    def get_config_meta(self):
        """
        Get config metadata

        Parameters:

        Returns:
        meta: No description available (ConfigMeta)
        """
        request = {
        }
        response = self.call("GetConfigMeta", request)
        return response['meta']
    
    def set_licensing_config(self, config):
        """
        Get Licensing configuration

        Parameters:
        config: No description available (LicensingConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetLicensingConfig", request)
        return 
    
    def get_licensing_config(self):
        """
        Get Licensing configuration

        Parameters:

        Returns:
        config: No description available (LicensingConfig)
        """
        request = {
        }
        response = self.call("GetLicensingConfig", request)
        return response['config']
    
    def get_events(self, entity_type, entity_id):
        """
        Get events associated with given entity

        Parameters:
        entity_type: No description available (string)
        entity_id: No description available (int64)

        Returns:
        events: No description available (Event)
        """
        request = {
            'entity_type': entity_type,
            'entity_id': entity_id
        }
        response = self.call("GetEvents", request)
        return response['events']
    
    def get_documentation(self):
        """
        Get all documentation

        Parameters:

        Returns:
        documentation: No description available (Documentation)
        """
        request = {
        }
        response = self.call("GetDocumentation", request)
        return response['documentation']
    
    def delete_documentation(self, item_id):
        """
        Delete a single documentation piece

        Parameters:
        item_id: No description available (int64)

        Returns:None
        """
        request = {
            'item_id': item_id
        }
        response = self.call("DeleteDocumentation", request)
        return 
    
    def create_kubernetes_volume(self, volume):
        """
        Create Kubernetes volume

        Parameters:
        volume: No description available (KubernetesVolume)

        Returns:None
        """
        request = {
            'volume': volume
        }
        response = self.call("CreateKubernetesVolume", request)
        return 
    
    def get_kubernetes_volumes(self):
        """
        Get all created Kubernetes volumes

        Parameters:

        Returns:
        volumes: No description available (KubernetesVolume)
        """
        request = {
        }
        response = self.call("GetKubernetesVolumes", request)
        return response['volumes']
    
    def get_profile_kubernetes_volumes(self):
        """
        Get all profile-specific Kubernetes volumes

        Parameters:

        Returns:
        volumes: No description available (KubernetesVolume)
        """
        request = {
        }
        response = self.call("GetProfileKubernetesVolumes", request)
        return response['volumes']
    
    def delete_kubernetes_volume(self, id):
        """
        Delete Kubernetes volume

        Parameters:
        id: No description available (int64)

        Returns:None
        """
        request = {
            'id': id
        }
        response = self.call("DeleteKubernetesVolume", request)
        return 
    
    def set_minio_config(self, config):
        """
        Set global Minio configuration

        Parameters:
        config: No description available (MinioConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetMinioConfig", request)
        return 
    
    def get_minio_config(self):
        """
        Get global Minio configuration

        Parameters:

        Returns:
        config: No description available (MinioConfig)
        """
        request = {
        }
        response = self.call("GetMinioConfig", request)
        return response['config']
    
    def set_personal_minio_credentials(self, credentials):
        """
        Set personal Minio credentials

        Parameters:
        credentials: No description available (PersonalMinioCredentials)

        Returns:None
        """
        request = {
            'credentials': credentials
        }
        response = self.call("SetPersonalMinioCredentials", request)
        return 
    
    def get_personal_minio_credentials(self):
        """
        Get personal Minio credentials

        Parameters:

        Returns:
        credentials: No description available (PersonalMinioCredentials)
        """
        request = {
        }
        response = self.call("GetPersonalMinioCredentials", request)
        return response['credentials']
    
    def set_storage_config(self, config):
        """
        Set global H2O.ai Storage configuration

        Parameters:
        config: No description available (StorageConfig)

        Returns:None
        """
        request = {
            'config': config
        }
        response = self.call("SetStorageConfig", request)
        return 
    
    def get_storage_config(self):
        """
        Get global H2O.ai Storage configuration

        Parameters:

        Returns:
        config: No description available (StorageConfig)
        """
        request = {
        }
        response = self.call("GetStorageConfig", request)
        return response['config']
    
    def get_oidc_token_provider(self):
        """
        Get details to establish personal Open ID token provider

        Parameters:

        Returns:
        provider: No description available (OidcTokenProvider)
        """
        request = {
        }
        response = self.call("GetOidcTokenProvider", request)
        return response['provider']
    
    def get_h2o_kubernetes_clusters(self):
        """
        Get my H2O cluster

        Parameters:

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
        }
        response = self.call("GetH2oKubernetesClusters", request)
        return response['cluster']
    
    def get_h2o_kubernetes_cluster_by_id(self, cluster_id):
        """
        Get H2O cluster by id

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("GetH2oKubernetesClusterById", request)
        return response['cluster']
    
    def stop_h2o_kubernetes_cluster_by_id(self, cluster_id):
        """
        Stop H2O cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("StopH2oKubernetesClusterById", request)
        return 
    
    def fail_h2o_kubernetes_cluster_by_id(self, cluster_id):
        """
        Mark H2O cluster as failed

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("FailH2oKubernetesClusterById", request)
        return 
    
    def delete_h2o_kubernetes_cluster_by_id(self, cluster_id):
        """
        Terminate H2O cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': cluster_id
        }
        response = self.call("DeleteH2oKubernetesClusterById", request)
        return 
    
    def get_h2o_kubernetes_cluster_by_name(self, cluster_name):
        """
        Get H2O cluster by name

        Parameters:
        cluster_name: No description available (string)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'cluster_name': cluster_name
        }
        response = self.call("GetH2oKubernetesClusterByName", request)
        return response['cluster']
    
    def get_h2o_kubernetes_cluster_by_name_created_by(self, cluster_name, created_by):
        """
        Get H2o cluster by name created by specified user

        Parameters:
        cluster_name: No description available (string)
        created_by: No description available (string)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'cluster_name': cluster_name,
            'created_by': created_by
        }
        response = self.call("GetH2oKubernetesClusterByNameCreatedBy", request)
        return response['cluster']
    
    def launch_h2o_kubernetes_cluster(self, parameters):
        """
        Launch H2O cluster

        Parameters:
        parameters: No description available (LaunchH2oKubernetesClusterParameters)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'parameters': parameters
        }
        response = self.call("LaunchH2oKubernetesCluster", request)
        return response['cluster']
    
    def get_h2o_kubernetes_cluster_logs(self, instance_id):
        """
        Get H2O cluster logs

        Parameters:
        instance_id: No description available (int64)

        Returns:
        logs: No description available (H2oK8sLogs)
        """
        request = {
            'instance_id': instance_id
        }
        response = self.call("GetH2oKubernetesClusterLogs", request)
        return response['logs']
    
    def get_h2o_kubernetes_engines(self):
        """
        Get engines for H2O on Kubernetes

        Parameters:

        Returns:
        engines: No description available (H2oKubernetesEngine)
        """
        request = {
        }
        response = self.call("GetH2oKubernetesEngines", request)
        return response['engines']
    
    def add_h2o_kubernetes_engine(self, engine):
        """
        Add engine for H2O on Kubernetes

        Parameters:
        engine: No description available (H2oKubernetesEngine)

        Returns:None
        """
        request = {
            'engine': engine
        }
        response = self.call("AddH2oKubernetesEngine", request)
        return 
    
    def remove_h2o_kubernetes_engine(self, version):
        """
        Remove engine for H2O on Kubernetes

        Parameters:
        version: No description available (string)

        Returns:None
        """
        request = {
            'version': version
        }
        response = self.call("RemoveH2oKubernetesEngine", request)
        return 
    
    def get_h2o_kubernetes_cluster(self, name):
        """
        Get H2O cluster by name

        Parameters:
        name: No description available (string)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'name': name
        }
        response = self.call("GetH2oKubernetesCluster", request)
        return response['cluster']
    
    def stop_h2o_kubernetes_cluster(self, name):
        """
        Stop H2O cluster

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': name
        }
        response = self.call("StopH2oKubernetesCluster", request)
        return 
    
    def fail_h2o_kubernetes_cluster(self, name):
        """
        Mark H2O cluster as failed

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': name
        }
        response = self.call("FailH2oKubernetesCluster", request)
        return 
    
    def delete_h2o_kubernetes_cluster(self, name):
        """
        Terminate H2O cluster

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': name
        }
        response = self.call("DeleteH2oKubernetesCluster", request)
        return 
    
    def dummy(self, a, b, c, d, f, g, h, i, j, k, l, m, n):
        """
        Does nothing

        Parameters:
        a: No description available (ProfileValue)
        b: No description available (ProfileSparklingInternal)
        c: No description available (ProfileSparklingExternal)
        d: No description available (ProfileH2o)
        f: No description available (ProfileDriverlessKubernetes)
        g: No description available (H2oClusterConnectParams)
        h: No description available (KubernetesVolumeHostPath)
        i: No description available (KubernetesVolumeSecret)
        j: No description available (KubernetesVolumeConfigMap)
        k: No description available (KubernetesVolumePvc)
        l: No description available (KubernetesVolumeNfs)
        m: No description available (KubernetesVolumeCsi)
        n: No description available (ProfileH2oKubernetes)

        Returns:None
        """
        request = {
            'a': a,
            'b': b,
            'c': c,
            'd': d,
            'f': f,
            'g': g,
            'h': h,
            'i': i,
            'j': j,
            'k': k,
            'l': l,
            'm': m,
            'n': n
        }
        response = self.call("Dummy", request)
        return 
    

