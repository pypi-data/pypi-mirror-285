import os
import time
import json
from computenestcli.service.image import ImageService
from computenestcli.common.util import Util
from computenestcli.common import constant
from computenestcli.service.credentials import CredentialsService

IMAGEID = 'imageId'
RUNNING = 'Running'
WAITING = 'Waiting'
QUEUED = 'Queued'
FAILED = 'Failed'
SUCCESS = 'Success'
RESPONSE = 'Response'
INVOCATIONS = 'Invocations'
INVOCATION = 'Invocation'
INVOKEINSTANCES = 'InvokeInstances'
INVOKEINSTANCE = 'InvokeInstance'
INVOCATIONRESULTS = 'InvocationResults'
INVOCATIONRESULT = 'InvocationResult'
OUTPUT = 'Output'
ACS_ECS_RUNCOMMAND = 'ACS::ECS::RunCommand'
MAX_RETRIES = 3
MAX_WAIT_TIME_SECOND = 1


class ImageProcessor:

    def __init__(self, context):
        self.context = context

    def get_execution_logs(self, execution_id):
        response = ImageService.list_task_executions(self.context, execution_id).body.task_executions
        for task_execution in response:
            if task_execution.task_action == ACS_ECS_RUNCOMMAND and (task_execution.status == FAILED or task_execution.status == SUCCESS):
                child_execution_id = task_execution.task_execution_id
                execution_logs = json.loads(ImageService.list_execution_logs(self.context, child_execution_id).body.execution_logs[2].message)
                if task_execution.status == FAILED:
                    execution_log = execution_logs[RESPONSE][INVOCATIONS][INVOCATION][0][INVOKEINSTANCES][INVOKEINSTANCE][0][OUTPUT]
                elif task_execution.status == SUCCESS:
                    execution_log = execution_logs[RESPONSE][INVOCATION][INVOCATIONRESULTS][INVOCATIONRESULT][0][OUTPUT]
                message = Util.decode_base64(execution_log)
            elif task_execution.status == FAILED:
                message = task_execution.status_message
        return message

    @Util.measure_time
    def process_image(self, image_data):
        retry_times = 0
        execution_id = ImageService.start_update_Image_execution(self.context, image_data)
        current_time = Util.get_current_time()
        print("===========================")
        print("The task to create an image has started executing")
        print("The execution id: ", execution_id)
        print("Start time: ", current_time)
        print("===========================")
        while True:
            image_data = ImageService.list_execution(self.context, execution_id)
            execution = image_data.body.executions[0]
            status = execution.status
            if status == RUNNING or status == WAITING or status == QUEUED:
                current_tasks = execution.current_tasks
                if current_tasks is None or len(current_tasks) == 0:
                    if retry_times < MAX_RETRIES:
                        retry_times += 1
                        time.sleep(MAX_WAIT_TIME_SECOND)
                        continue
                    if retry_times >= MAX_RETRIES:
                        raise Exception("Build image failed, error message: ", execution.status_message)
                current_task = current_tasks[0].task_name
                print('Executing...The current task is :', current_task)
            elif status == FAILED:
                raise Exception("Execution failed, Error message: ", execution.status_message)
                # try:
                #     execution_log = self.get_execution_logs(execution_id)
                #     print("The detailed execution log: \n", execution_log)
                # except Exception as e:
                #     print('get execution log failed', e)
            elif status == SUCCESS:
                image_data = ImageService.list_execution(self.context, execution_id)
                outputs = json.loads(image_data.body.executions[0].outputs)
                image_id = outputs[IMAGEID]
                current_time = Util.get_current_time()
                try:
                    execution_log = ImageService.get_execution_logs(self.context, execution_id)
                    # print("The detailed execution log: \n", execution_log)
                except Exception as e:
                    print('get execution log failed', e)
                print("===========================")
                print("Successfully created a new image!")
                print("The image id: ", image_id)
                print("Completion time: ", current_time)
                print("===========================")
                break
            time.sleep(100)

        return image_id

    @Util.measure_time
    def process_acr_image(self, acr_image_name, acr_image_tag, file_path):
        response = CredentialsService.get_artifact_repository_credentials(self.context, constant.ACR_IMAGE)
        username = response.body.credentials.username
        password = response.body.credentials.password
        repository_name = response.body.available_resources[0].repository_name
        docker_path = os.path.dirname(response.body.available_resources[0].path)
        file_path = os.path.dirname(file_path)
        commands = [
            f"docker build -t {acr_image_name}:{acr_image_tag} .",
            f"docker login {repository_name} --username={username} --password={password}",
            f"docker tag {acr_image_name}:{acr_image_tag} {docker_path}/{acr_image_name}:{acr_image_tag}",
            f"docker push {docker_path}/{acr_image_name}:{acr_image_tag}"
        ]
        for command in commands:
            try:
                output, error = Util.run_cli_command(command, file_path)
                print(output.decode())
                print(error.decode())
            except Exception as e:
                print(f"Error occurred: {e}")
                raise e

    @Util.measure_time
    def process_helm_chart(self, file_path):
        response = CredentialsService.get_artifact_repository_credentials(self.context, constant.HELM_CHART)
        username = response.body.credentials.username
        password = response.body.credentials.password
        repository_name = response.body.available_resources[0].repository_name
        chart_path = os.path.dirname(response.body.available_resources[0].path)
        file_name = file_path.split("/")[-1]
        file_path = os.path.dirname(file_path)
        commands = [
            f"helm registry login -u {username} {repository_name} -p {password}",
            f"helm push {file_name} oci://{chart_path}"
        ]
        for command in commands:
            try:
                output, error = Util.run_cli_command(command, file_path)
                print(output.decode())
                print(error.decode())
            except Exception as e:
                print(f"Error occurred: {e}")
                raise e
