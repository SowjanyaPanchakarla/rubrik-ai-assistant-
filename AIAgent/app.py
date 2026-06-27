import os

from flask import Flask, jsonify, request

from rubrik_client import RubrikClient
from queries import PROTECTED_VMS_QUERY, LATEST_RECOVERY_POINT_QUERY

app = Flask(__name__)


def get_client():
    client_id = os.getenv("RUBRIK_CLIENT_ID", "")
    client_secret = os.getenv("RUBRIK_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        raise ValueError("RUBRIK_CLIENT_ID and RUBRIK_CLIENT_SECRET must be set.")

    return RubrikClient(
        client_id=client_id,
        client_secret=client_secret,
    )


def get_vm_data():
    client = get_client()
    result = client.execute_query(PROTECTED_VMS_QUERY)
    return result["data"]["vSphereVmNewConnection"]["nodes"]


def get_protected_vms():
    vms = get_vm_data()
    response = []

    for vm in vms:
        sla = vm["effectiveSlaDomain"]["name"]
        if sla not in ["UNPROTECTED", "DO_NOT_PROTECT"]:
            response.append({
                "name": vm["name"],
                "sla": sla,
            })

    return response


def check_vm_protection(vm_name):
    vms = get_vm_data()

    for vm in vms:
        if vm_name.lower() in vm["name"].lower():
            sla = vm["effectiveSlaDomain"]["name"]

            return {
                "name": vm["name"],
                "sla": sla,
                "protected": sla not in ["UNPROTECTED", "DO_NOT_PROTECT"],
            }

    return None


def get_protection_summary():
    vms = get_vm_data()

    total = len(vms)
    protected = 0
    unprotected = 0
    do_not_protect = 0

    for vm in vms:
        sla = vm["effectiveSlaDomain"]["name"]

        if sla == "UNPROTECTED":
            unprotected += 1
        elif sla == "DO_NOT_PROTECT":
            do_not_protect += 1
        else:
            protected += 1

    return {
        "total_vms": total,
        "protected": protected,
        "unprotected": unprotected,
        "do_not_protect": do_not_protect,
    }


def get_latest_recovery_points():
    client = get_client()
    result = client.execute_query(LATEST_RECOVERY_POINT_QUERY)
    vms = result["data"]["vSphereVmNewConnection"]["nodes"]

    response = []

    for vm in vms:
        snapshot = vm["newestSnapshot"]

        response.append({
            "name": vm["name"],
            "recovery_point": None if snapshot is None else snapshot["date"],
        })

    return response


def get_vm_recovery_point(vm_name):
    client = get_client()
    result = client.execute_query(LATEST_RECOVERY_POINT_QUERY)
    vms = result["data"]["vSphereVmNewConnection"]["nodes"]

    for vm in vms:
        if vm_name.lower() in vm["name"].lower():
            snapshot = vm["newestSnapshot"]

            return {
                "name": vm["name"],
                "recovery_point": None if snapshot is None else snapshot["date"],
            }

    return None


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/protected-vms")
def protected_vms():
    return jsonify(get_protected_vms())


@app.get("/protection-summary")
def protection_summary():
    return jsonify(get_protection_summary())


@app.get("/recovery-points")
def recovery_points():
    return jsonify(get_latest_recovery_points())


@app.get("/vm-protection")
def vm_protection():
    vm_name = request.args.get("name", "").strip()

    if not vm_name:
        return jsonify({"error": "Query parameter 'name' is required."}), 400

    result = check_vm_protection(vm_name)

    if result is None:
        return jsonify({"error": "VM not found."}), 404

    return jsonify(result)


@app.get("/vm-recovery-point")
def vm_recovery_point():
    vm_name = request.args.get("name", "").strip()

    if not vm_name:
        return jsonify({"error": "Query parameter 'name' is required."}), 400

    result = get_vm_recovery_point(vm_name)

    if result is None:
        return jsonify({"error": "VM not found."}), 404

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)