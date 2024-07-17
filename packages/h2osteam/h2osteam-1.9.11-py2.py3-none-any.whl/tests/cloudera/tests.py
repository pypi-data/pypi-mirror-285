import os
import h2osteam
from h2osteam.clients import H2oClient
from h2osteam.clients import SparklingClient

# Configure script with env variables
STEAM_PORT = os.environ.get("STEAM_PORT", "9521")
STEAM_URL = "https://localhost:" + STEAM_PORT  # No tailing slash

# Log in
h2osteam.login(STEAM_URL, username="admin", password="adminadmin", verify_ssl=False)

# Create a hadoop user
identity_id = h2osteam.api().create_identity("h2o", "0xdata", "")
for profile in h2osteam.api().get_profiles():
    h2osteam.api().link_identity_with_profile(identity_id, profile["id"])
# 1 -> standard user
h2osteam.api().link_identity_with_role(identity_id, 1)
h2osteam.login(STEAM_URL, username="h2o", password="0xdata", verify_ssl=False)

# Launch H2O cluster
c = H2oClient.launch_cluster(name="CICD-test", version=h2osteam.api().get_h2o_engines()[0]["h2o_version"])
c.stop()

# Launch Sparkling Water cluster
c = SparklingClient.launch_sparkling_cluster(name="CICD-test", version=h2osteam.api().get_sparkling_engines()[0]["h2o_version"])
c.stop()