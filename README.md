<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48245050/182578921-e47cdecb-5726-424d-a1c9-b06dbf692b1f.png"/>

# Copy Project Between Supervisely Instances

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Use">How To Use</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/copy-project-between-instances)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/copy-project-between-instances)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/copy-project-between-instances)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/copy-project-between-instances)](https://supervise.ly)

</div>

## Overview

Illustrative Use Case: Enterprise Customer with private Supervisely Instance would like to share project with labeling provider that also has his own private Supervisely Instance. This app is useful especially when projects are huge (several gigabytes +).

## How To Use

1. Create new team on `source` instance. Copy project to this team. Let's call this project: `project_to_share`.
2. Create and invite user to this team. This new User has access only to projects in special team, all data in other teams is private.
3. Share `id` of `project_to_share` and user's `api_token` with your labeling provider.
4. Labeling provider has to run app and in modal window define `SERVER_ADDRESS`, `id` of project that should be copied and `API_TOKEN`.

<img src="https://i.imgur.com/7hdsoSU.png" width="450px"/>

5. Project (images/annotations/images metadata) is copied to current team/workspace with the same name.  

<img src="https://i.imgur.com/bBqPCZh.png"/>
