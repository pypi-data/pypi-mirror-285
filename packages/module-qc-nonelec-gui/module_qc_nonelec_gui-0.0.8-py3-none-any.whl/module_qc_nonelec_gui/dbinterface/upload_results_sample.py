from __future__ import annotations

import logging

import itkdb

log = logging.getLogger(__name__)

##############
## functions


def upload_results(code1, code2, mod_name, stage, run_num, date, result1, result2):
    u = itkdb.core.User(access_code1=code1, access_code2=code2)
    pd_client = itkdb.Client(user=u)
    # queries = [{"status": "ready"}, {"status": "unmatched"}]
    pdtest_list = ["OPTICAL"]
    module_name = mod_name

    res1 = result1 == "1"
    res2 = result2 == "1"

    ## get the parent information and setting upload parameter
    parent_doc = pd_client.get("getComponent", json={"component": module_name})
    log.info("Module name: " + module_name)
    log.info("Stage:       " + stage)
    if parent_doc["currentStage"]["code"] != stage:
        log.info("Stage is not corresponded to ITk production DB. Please check it")
        # userdb.itkpd.uploader.commit.update_one({"_id":ObjectId(str(commit["_id"]))},{"set":{"status":"unmatched"}} )
    elif parent_doc["currentStage"]["code"] == stage:
        log.info("Stage is matched. Start to uploading test results...\n")
        log.info("There are " + str(len(pdtest_list)) + " test items to upload.")

        #  userdb.itkpd.uploader.commit.update_one({"_id":ObjectId(str(commit["_id"]))},{"set":{"status":"uploading"}} )
        for _i, testType in enumerate(pdtest_list):
            pd_testType = {"code": testType}

            child_doc = pd_client.get("getComponent", json={"component": module_name})
            project = {"project": child_doc["project"]["code"]}
            # subproject = {"subproject": child_doc["project"]["code"]}
            institution = {"institution": child_doc["currentLocation"]["code"]}
            componentType = {"componentType": child_doc["componentType"]["code"]}

            ## make the result page for parent component
            test_template = pd_client.get(
                "generateTestTypeDtoSample",
                json={**project, **componentType, **pd_testType},
            )
            #  new_test_result = pd_client.post('uploadTestRunResults', json={**test_template, 'component': module_name, **institution, 'runNumber':'0000', 'date':'23.04.2020', 'results':{'SCRATCHES':True,'DIRT':True}})
            pd_client.post(
                "uploadTestRunResults",
                json={
                    **test_template,
                    "component": module_name,
                    **institution,
                    "runNumber": run_num,
                    "date": date,
                    "results": {"SCRATCHES": res1, "DIRT": res2},
                },
            )
            log.info("Finished for all results!!\n")
