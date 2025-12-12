import os
import supervisely_lib as sly

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])

SERVER_ADDRESS2 = os.environ["modal.state.serverAddress"]
if SERVER_ADDRESS2 == "":
    raise ValueError("Remote server address is not defined")
API_TOKEN2 = os.environ["modal.state.apiToken"]
if API_TOKEN2 == "":
    raise ValueError("Remote API token is not defined")

my_app = sly.AppService()
api2 = sly.Api(SERVER_ADDRESS2, API_TOKEN2)
PROJECT_ID2 = int(os.environ['modal.state.projectId'])


def is_video_linked(video_info):
    """Check if a video was uploaded via link rather than as a file."""
    return video_info.link is not None and video_info.link != ""


def copy_images_project(api, api2, project, project2, progress):
    """Copy an images project from one instance to another."""
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

            for p in paths:
                sly.fs.silent_remove(p)

            progress.iters_done_report(len(batch2))


def copy_videos_project(api, api2, project, project2, progress):
    """Copy a videos project from one instance to another."""
    meta2 = sly.ProjectMeta.from_json(api2.project.get_meta(project2.id))
    
    for dataset2 in api2.dataset.get_list(project2.id):
        dataset = api.dataset.create(project.id, dataset2.name, dataset2.description)
        videos2 = api2.video.get_list(dataset2.id)
        
        for batch2 in sly.batched(videos2, batch_size=10):
            # Separate linked and regular videos
            linked_videos = []
            regular_videos = []
            
            for video_info2 in batch2:
                if is_video_linked(video_info2):
                    linked_videos.append(video_info2)
                else:
                    regular_videos.append(video_info2)
            
            # Process linked videos
            if linked_videos:
                links = []
                names = []
                metas = []
                
                for video_info2 in linked_videos:
                    links.append(video_info2.link)
                    names.append(video_info2.name)
                    metas.append(video_info2.meta)
                
                # Upload linked videos
                uploaded_videos = api.video.upload_links(dataset.id, links, names, metas=metas)
                
                # Download and upload annotations
                for video_info2, uploaded_video in zip(linked_videos, uploaded_videos):
                    ann2 = api2.video.annotation.download(video_info2.id)
                    ann_path = os.path.join(my_app.data_dir, f"{video_info2.name}.json")
                    sly.json.dump_json_file(ann2, ann_path)
                    api.video.annotation.upload_paths([uploaded_video.id], [ann_path], meta2)
                    sly.fs.silent_remove(ann_path)
            
            # Process regular videos
            if regular_videos:
                ids2 = []
                names = []
                paths = []
                metas = []
                
                for video_info2 in regular_videos:
                    ids2.append(video_info2.id)
                    names.append(video_info2.name)
                    paths.append(os.path.join(my_app.data_dir, video_info2.name))
                    metas.append(video_info2.meta)
                
                # Download videos
                for video_id, path in zip(ids2, paths):
                    api2.video.download_path(video_id, path)
                
                # Upload videos
                uploaded_videos = api.video.upload_paths(dataset.id, names, paths, metas=metas)
                
                # Download and upload annotations
                ann_paths = [os.path.join(my_app.data_dir, f"{v.name}.json") for v in regular_videos]
                for video_info2, uploaded_video, ann_path in zip(regular_videos, uploaded_videos, ann_paths):
                    ann2 = api2.video.annotation.download(video_info2.id)
                    sly.json.dump_json_file(ann2, ann_path)
                    api.video.annotation.upload_paths([uploaded_video.id], [ann_path], meta2)
                    sly.fs.silent_remove(ann_path)
                
                # Clean up video files
                for p in paths:
                    sly.fs.silent_remove(p)
            
            progress.iters_done_report(len(batch2))


@my_app.callback("copy_project")
@sly.timeit
def copy_project(api: sly.Api, task_id, context, state, app_logger):
    project2 = api2.project.get_info_by_id(PROJECT_ID2)
    if project2 is None:
        raise RuntimeError(f"Project with id={PROJECT_ID2} not found on remote Supervisely instance")
    
    # Support both images and videos projects
    if project2.type not in [str(sly.ProjectType.IMAGES), str(sly.ProjectType.VIDEOS)]:
        raise TypeError(f"This version supports only images and videos projects. "
                        f"Project type '{project2.type}' is not supported. "
                        f"Please, submit a feature request to Supervisely dev team to add support of other types.")

    meta2_json = api2.project.get_meta(project2.id)

    project = api.project.create(WORKSPACE_ID,
                                 project2.name,
                                 project2.type,
                                 project2.description,
                                 change_name_if_conflict=True)
    api.project.update_meta(project.id, meta2_json)

    # Use items_count for universal support (works for both images and videos)
    progress = sly.Progress("Import", project2.items_count)
    
    if project2.type == str(sly.ProjectType.IMAGES):
        copy_images_project(api, api2, project, project2, progress)
    elif project2.type == str(sly.ProjectType.VIDEOS):
        copy_videos_project(api, api2, project, project2, progress)

    api.task.set_output_project(task_id, project.id, project.name)
    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
        "PROJECT_ID2": PROJECT_ID2
    })
    my_app.run(initial_events=[{"command": "copy_project"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)