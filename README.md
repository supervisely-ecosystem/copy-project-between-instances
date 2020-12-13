<div align="center" markdown>
<img src="https://i.imgur.com/xmuBeht.png"/>

# Copy Project Between Supervisely Instances

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Use">How To Use</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/copy-project-between-instances)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/copy-project-between-instances)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/copy-project-between-instances&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/copy-project-between-instances&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/copy-project-between-instances&counter=runs&label=runs)](https://supervise.ly)

</div>

## Overview

Illustrative Use Case: Enterprise Customer with private Supervisely Instance would like to share project with labeling provider that also has his own private Supervisely Instance. This app is useful especially when projects are huge (in gigabytes).

## How To Use

1. Create new team on `source` instance. Copy project to this team.
2. Create and invite user to this team. This new User has access only to projects in special team, all data in other teams is private.
3. Share `project_id` and user's `api_token` with your labeling provider.
