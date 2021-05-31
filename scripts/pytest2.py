import os
from pybfe.client.session import Session
from intentionet.bfe.proto import api_gateway_pb2 as api
from intentionet.bfe.proto import policies_api_pb2 as policies_api

os.environ['BFE_SSL_CERT'] = "../cert/nexbfe.crt"
BFE_HOST = "batfish.nexariacloud.com"
BFE_PORT = 443
bf = Session(host=BFE_HOST, port=BFE_PORT)

NETWORK_NAME="AcmeCorp"
SNAPSHOT_NAME="baseline"
SNAPSHOT_DIR="../bgp_configs/reference_bgp/"

networks = bf.list_networks()
if NETWORK_NAME in networks:
    bf.delete_network(NETWORK_NAME)

bf.set_network(NETWORK_NAME)

devices_have_routes = {
  "description": "CE1 networks on CE2",
  "title": "CE2 - Received routes",
  "devices_have_routes": {
    "vrfs": {
      "devices": {
        "hostname": {
          "regex": "ce2"
        }
      },
      "name": {
        "regex": ".*"
      }
    },
    "routes": {
      "all": {
        "of": [
          {
            "network": {
              "equals": "100.1.0.1/32"
            },
            "bgp": {}
          },
          {
            "network": {
              "equals": "100.1.1.1/32"
            },
            "bgp": {}
          },
          {
            "network": {
              "equals": "100.1.2.1/32"
            },
            "bgp": {}
          },
          {
            "network": {
              "equals": "100.1.3.1/32"
            },
            "bgp": {}
          }
        ]
      }
    }
  }
}

filter_behavior_denied = {
  "description": "100.1.1.1 denied",
  "title": "ce2 to ce1",
  "filter_behavior": {
    "devices": {
      "hostname": {
        "regex": "pe3"
      }
    },
    "filters": {
      "name": {
        "regex": "100"
      }
    },
    "flows": {
      "include": [
        {
          "src_ips": [
            {
              "exact_match": "200.1.1.1"
            }
          ],
          "dst_ips": [
            {
              "exact_match": "100.1.1.1"
            }
          ],
          "apps": [
            "tcp"
          ]
        },
        {
          "src_ips": [
            {
              "exact_match": "200.1.1.1"
            }
          ],
          "dst_ips": [
            {
              "exact_match": "100.1.2.1"
            }
          ],
          "apps": [
            "tcp"
          ]
        }
      ]
    },
    "expect": {
      "action": "DENY"
    }
  }
}

filter_behavior_allowed = {
  "description": "allowed on ce1",
  "title": "ce2 permitted",
  "filter_behavior": {
    "devices": {
      "hostname": {
        "regex": "pe3"
      }
    },
    "filters": {
      "name": {
        "regex": "100"
      }
    },
    "flows": {
      "include": [
        {
          "src_ips": [
            {
              "exact_match": "200.1.1.1"
            }
          ],
          "dst_ips": [
            {
              "exact_match": "100.1.1.1"
            }
          ],
          "apps": [
            "tcp"
          ]
        }
      ]
    },
    "expect": {
      "action": "PERMIT"
    }
  }
}

bf._experimental_create_policy(devices_have_routes)
bf._experimental_create_policy(filter_behavior_denied)
bf._experimental_create_policy(filter_behavior_allowed)

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

status = get_policy_results(bf)
print(status)