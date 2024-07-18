from __future__ import annotations


def module_retriever(localdb, serialNumber):
    return localdb.component.find_one({"and": [{"serialNumber": serialNumber}]})


def moduleid_retriever(localdb, serialNumber):
    try:
        module = localdb.component.find_one(
            {"and": [{"serialNumber": serialNumber}, {"componentType": "module"}]}
        )
        return str(module["_id"])
    except TypeError:
        try:
            module = localdb.component.find_one(
                {
                    "and": [
                        {"serialNumber": serialNumber},
                        {"componentType": "bare_module"},
                    ]
                }
            )
            return str(module["_id"])
        except TypeError:
            module = localdb.component.find_one(
                {
                    "and": [
                        {"serialNumber": serialNumber},
                        {"componentType": "module_pcb"},
                    ]
                }
            )
            return str(module["_id"])


def stage_retriever(localdb, serialNumber):
    mod_id = moduleid_retriever(localdb, serialNumber)
    qc_mod_status = localdb.QC.module.status.find_one({"component": mod_id})
    return qc_mod_status["currentStage"]


def userinfo_retriever(localdbtools, username):
    return localdbtools.viewer.user.find_one({"username": username})


def status_check(localdb, serialNumber, testname, isProperty):
    mod_id = moduleid_retriever(localdb, serialNumber)
    stage = stage_retriever(localdb, serialNumber)
    if isProperty:
        doc = localdb.QC.module.prop.find(
            {
                "and": [
                    {"component": mod_id},
                    {"currentStage": stage},
                    {"testType": testname},
                ]
            }
        )
    else:
        doc = localdb.QC.result.find(
            {
                "and": [
                    {"component": mod_id},
                    {"currentStage": stage},
                    {"testType": testname},
                ]
            }
        )
    ndoc = doc.count()
    user = doc.sort([("natural", -1)])[0]["user"]
    address = doc.sort([("natural", -1)])[0]["address"]
    date = doc.sort([("natural", -1)])[0]["sys"]["cts"]
    return {"ndoc": ndoc, "user": user, "address": address, "date": date}
