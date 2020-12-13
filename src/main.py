import os
import supervisely_lib as sly

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])

my_app = sly.AppService()

api2 = sly.Api(os.environ["SERVER_ADDRESS2"], os.environ["API_TOKEN2"])
PROJECT_ID2 = int(os.environ['modal.state.projectId'])


@my_app.callback("copy_project")
@sly.timeit
def copy_project(api: sly.Api, task_id, context, state, app_logger):
    project2 = api2.project.get_info_by_id(PROJECT_ID2)
    if project2 is None:
        raise RuntimeError(f"Project with id={PROJECT_ID2} not found on remote Supervisely instance")
    meta2 = sly.ProjectMeta(api2.project.get_meta(project2.id))

    project = api.project.create(WORKSPACE_ID,
                                 project2.name,
                                 project2.type,
                                 project2.description,
                                 change_name_if_conflict=True)
    api.project.update_meta(project.id, meta2)

    progress = sly.Progress("Import", project2.items_count)
    for dataset2 in api2.dataset.get_list(project2.id):
        dataset = api.dataset.create(project.id, dataset2.name, dataset2.description)
        images2 = api2.image.get_list(dataset2.id)
        for batch2 in sly.batched(images2, batch_size=10):
            ids2 = []
            names = []
            paths = []
            metas = []
            for image_info2 in batch2:
                ids2.append(image_info2.id)
                names.append(image_info2.name)
                paths.append(os.path.join(my_app.data_dir, image_info2.name))
                metas.append(image_info2.meta)

            api2.image.download_paths(dataset2.id, ids2, paths)
            anns2 = api2.annotation.download_batch(dataset2.id, ids2)
            anns2 = [ann2.annotation for ann2 in anns2]

            batch = api.image.upload_paths(dataset.id, names, paths, metas=metas)
            ids = [image_info.id for image_info in batch]
            api.annotation.upload_jsons(ids, anns2)
        progress.iters_done_report(len(batch2))

    api.task.set_output_project(task_id, project.id, project.name)
    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
        "SERVER_ADDRESS2": SERVER_ADDRESS2,
        "PROJECT_ID2": PROJECT_ID2
    })
    my_app.run(initial_events=[{"command": "copy_project"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)