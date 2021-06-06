import os
from pybfe.client.session import Session
from intentionet.bfe.proto import api_gateway_pb2 as api
from intentionet.bfe.proto import policies_api_pb2 as policies_api
import my_policies

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
os.environ['BFE_SSL_CERT'] = SCRIPT_DIR+'/../cert/test.crt'

BFE_HOST = "batfish.nexariacloud.com"
BFE_PORT = 443
bf = Session(host=BFE_HOST, port=BFE_PORT)
if bf:
    print()
    print("***********************************************")
    print("Created BFE session on host {}".format(BFE_HOST))
    print("***********************************************")
    print()

REF_SNAPSHOT = ''
NEW_SNAPSHOT = ''
NETWORK_NAME="bgp_test_lab"
bf.set_network(NETWORK_NAME)
print()
print("***********************************************")
print("Network is set as {}".format(NETWORK_NAME))
print("***********************************************")
print()

snapshots = bf.list_snapshots()
if len(snapshots) == 2:
    for snapshot in snapshots:
        if snapshot.startswith('baseline'):
            REF_SNAPSHOT = snapshot
        else: NEW_SNAPSHOT = snapshot
else:
    for snapshot in snapshots:
        if snapshot.startswith('baseline'):
            REF_SNAPSHOT = snapshot
            break
    NEW_SNAPSHOT = snapshots[0]

bf._experimental_create_policy(my_policies.devices_have_routes)
bf._experimental_create_policy(my_policies.filter_behavior_denied)
bf._experimental_create_policy(my_policies.filter_behavior_allowed)

def policy_status_to_string(status):
    if status == policies_api.POLICY_STATUS_UNKNOWN:
        return "UNKNOWN"
    elif status == policies_api.POLICY_STATUS_FAIL:
        return "FAIL"
    elif status == policies_api.POLICY_STATUS_PASS:
        return "PASS"
    elif status == policies_api.POLICY_STATUS_PASS_WARN:
        return "WARN"
    else:
        raise RuntimeError("Unknown policy status {}".format(status))

def get_policy_results(bf: Session):
    """
    Get policy evaluation results for a snapshot.
    
    Returns a map from policy title to status
    """
    response = bf._api_gw.ListPolicyResultsMetadata(
        api.ListPolicyResultsMetadataRequest(
            network_name=bf.network, snapshot_name=bf.snapshot
        )
    )
    status = {}
    for result in response.metadata:
        policy_response = bf._api_gw.GetPolicy(
            api.GetPolicyRequest(
                network_name=bf.network, policy_id=result.policy_id
            )
        )
        status[policy_response.policy.input.title] = policy_status_to_string(result.status)

    return status

print()
print("***********************************************")
print("Snapshot against which policies are checked: %s", NEW_SNAPSHOT)
print("***********************************************")
print()

bf.set_snapshot(NEW_SNAPSHOT)
status = get_policy_results(bf)
print(status)