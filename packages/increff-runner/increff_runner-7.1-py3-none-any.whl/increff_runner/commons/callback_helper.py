from logging_increff.function import *
from .mse_helper import create_events_for_next_blocks, mark_dependant_as_failed
from .constants import *
import requests
import json
from .db_service import update_job
from .db_helper import get_interim_tasks
from .graphdb_helper import *


def send_success_callback(url, output, error_data, job):
    if error_data != {}:
        send_failure_callback(url, "Script Failed", output, error_data, job)
        return
    output["caas_job_id"] = job["id"]
    add_info_logs(job["id"], "Hitting Success Callback")
    body = {
        "StatusCode": "200",
        "Output": {"output_data": output, "error_data": error_data},
    }
    add_info_logs(job["id"], f"Success message -> {str(body)}")
    job["callback_status"] = "200"
    update_job(job)
    response = requests.post(url, data=json.dumps(body))


def send_success_webhook(url, master_url, output, error_data, job):
    if error_data != {}:
        if('is_warning' not in error_data or ('is_warning' in error_data and error_data['is_warning'] == 0)):
            send_failure_webhook(master_url, job["data"]["task_id"], error_data, job)
            return
    
    output["caas_job_id"] = job["id"]
    add_info_logs(job["id"], "Hitting Success WebHook Callback")
    create_events_for_next_blocks(url, master_url, output, error_data, job)


def send_failure_callback(url, error, output_data, error_data, job):
    add_info_logs(job["id"], "Hitting Failure Callback")
    output_data["caas_job_id"] = job["id"]
    body = {
        "Output": {"output_data": output_data, "error_data": error_data},
        "Error": {"ErrorCode": "400", "Message": str(error)},
        "StatusCode": "400",
    }
    add_info_logs(job["id"], f" failure message -> {str(body)}")
    job["callback_status"] = 400
    update_job(job)
    response = requests.post(url, data=json.dumps(body))


def send_failure_webhook(url, task_id, error, job):
    node = get_task_node(job["data"]["algo_name"],task_id,job["data"]["level"])
    add_error_logs(job["id"], "Hitting Failure WebHook Callback with error -> "+str(error)) 
    data = {"taskId": task_id, "subtaskName":  node['parent_task']}
    body = {"reason":json.dumps(error),"status": "FAILED"}
    if(error=={}):
        body['reason']=json.dumps({"reason":"Script Failed","reason_details":"Script Failed"})
    headers = {
        "Content-Type": "application/json",
        "authUsername":"caas-user@increff.com",
        "authPassword":"caasuser@123",
        "authdomainname": job["data"]["client"],
        "Conection":"keep-alive"
    }
    add_info_logs(job["id"], f" failure message -> {str(data)}")
    job["webhook_status"] = 400
    update_job(job)

    change_status_of_task_node(job["data"]["algo_name"], job["data"]["task_id"], job["data"]["level"], FAILED)
    mark_dependant_as_failed(task_id,job["data"]["webHookUri"])
    response = requests.put(url, params=data,headers=headers,data=json.dumps(body))
    add_info_logs(job["id"], f"Failure Webhook Response -> {response.status_code}")
