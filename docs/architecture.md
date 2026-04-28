# PyFarm Architecture Map

This file maps the current Django MVT structure, main use cases, and database architecture for PyFarm.

## Django MVT Structure

### Model

Models live in `tracker/models.py`.

Current domain models:

- `UserProfile`: extends Django's built-in `User` with a PyFarm role.
- `Field`: stores farm field details.
- `FarmProject`: stores planned farm work linked to a field and manager.
- `FarmTask`: stores project tasks, assignments, progress, optional image evidence, and status.
- `FarmTaskProgressUpdate`: stores timestamped worker progress updates for tasks.
- `FieldRecord`: stores agronomist crop and field advice.

### View

Views live in `tracker/views.py`.

Current views:

- `home`: dashboard showing projects, tasks, field records, and role-based actions.
- `project_detail`: project page showing project tasks and field records.
- `task_detail`: task page showing task details and full timestamped progress history.
- `create_field`: Farm Manager-only field creation.
- `create_project`: Farm Manager-only project creation.
- `create_task`: Farm Manager-only task creation and assignment.
- `update_task_progress`: Field Worker-only task progress update form supporting `In Progress` or `Done`, progress comments, and optional image upload.
- `create_field_record`: Agronomist-only field record creation.

Role helper functions:

- `get_user_role(user)`: reads the logged-in user's profile role.
- `user_has_role(user, *roles)`: checks whether a user has one of the allowed roles.
- `require_role(request, *roles)`: blocks unauthorized role actions and shows a message.

### Template

Templates live in `templates/`.

Current templates:

- `templates/tracker/home.html`: main dashboard.
- `templates/tracker/project_detail.html`: project detail page.
- `templates/tracker/form.html`: shared form page for creation and progress update forms.
- `templates/registration/login.html`: login page used by Django auth.

Templates extend `templates/base.html`, which provides the shared Bootstrap layout, navigation, and message display.

### URL Routing

Project routes live in `pyfarm/urls.py`.

App routes live in `tracker/urls.py`.

Current app routes:

| URL | View | Purpose |
| --- | --- | --- |
| `/` | `home` | Dashboard |
| `/fields/new/` | `create_field` | Create field |
| `/projects/new/` | `create_project` | Create project |
| `/projects/<project_id>/` | `project_detail` | View project |
| `/tasks/<task_id>/` | `task_detail` | View task and progress history |
| `/tasks/new/` | `create_task` | Create task |
| `/tasks/<task_id>/progress/` | `update_task_progress` | Update worker progress |
| `/field-records/new/` | `create_field_record` | Create agronomist field record |

Media uploads are served in development through `pyfarm/urls.py` using `settings.MEDIA_URL` and `settings.MEDIA_ROOT`.

## User Roles And Use Cases

### Farm Manager

Purpose: planning and assigning work.

Can:

- Create fields.
- Create projects.
- Create tasks.
- Assign tasks to Field Workers.
- Upload an optional task image when creating a task.
- View projects, tasks, progress comments, images, and field records.

Main flow:

1. Log in.
2. Create a field.
3. Create a project linked to that field.
4. Create tasks for the project.
5. Assign tasks to Field Workers.
6. Review worker progress on the dashboard or project detail page.

### Field Worker

Purpose: carrying out assigned work.

Can:

- View projects and tasks.
- Update task status to `In Progress` or `Done`.
- Add progress comments.
- Optionally upload an image as evidence or context.

Main flow:

1. Log in.
2. View tasks from the dashboard or project detail page.
3. Open a task detail page to review progress history.
4. Open `Update Progress`.
5. Add a progress comment.
6. Choose `In Progress` or `Done`.
7. Optionally upload an image.
8. Save the update.

### Agronomist

Purpose: crop and field advice.

Can:

- View projects.
- Create field records with crop information.
- Add advice linked to a field and optionally to a project.

Main flow:

1. Log in.
2. Review projects and field context.
3. Open `Create Field Record`.
4. Select a field and optional project.
5. Enter crop, crop stage, and advice.
6. Save the record.

## Database Architecture

### Tables And Fields

#### `auth_user`

Django's built-in user table.

Used by:

- `UserProfile.user`
- `FarmProject.manager`
- `FarmTask.assigned_to`
- `FieldRecord.created_by`

#### `tracker_userprofile`

Stores the user's PyFarm role.

Fields:

- `user`: one-to-one link to `auth_user`.
- `role`: one of `FARM_MANAGER`, `FIELD_WORKER`, or `AGRONOMIST`.

Relationships:

- One `User` has one `UserProfile`.

#### `tracker_field`

Stores a physical field.

Fields:

- `name`
- `crop_type`
- `size_acres`
- `location`

Relationships:

- One `Field` can have many `FarmProject` records.
- One `Field` can have many `FieldRecord` records.

#### `tracker_farmproject`

Stores a farm project.

Fields:

- `title`
- `description`
- `field`: foreign key to `Field`.
- `manager`: foreign key to `User`.
- `start_date`
- `end_date`
- `status`: `PLANNED`, `IN_PROGRESS`, or `COMPLETED`.

Relationships:

- One `FarmProject` belongs to one `Field`.
- One `FarmProject` has one manager.
- One `FarmProject` can have many `FarmTask` records through `tasks`.
- One `FarmProject` can have many `FieldRecord` records through `field_records`.

#### `tracker_farmtask`

Stores a task inside a project.

Fields:

- `project`: foreign key to `FarmProject`.
- `title`
- `description`
- `image`: optional upload stored under `task_images/`.
- `assigned_to`: optional foreign key to `User`.
- `due_date`
- `status`: `TODO`, `IN_PROGRESS`, or `DONE`.
- `priority`: `LOW`, `MEDIUM`, or `HIGH`.
- `progress_comment`: optional worker progress note.

Relationships:

- One `FarmTask` belongs to one `FarmProject`.
- One `FarmTask` can be assigned to one `User`.
- One `FarmTask` can have many `FarmTaskProgressUpdate` records.

#### `tracker_farmtaskprogressupdate`

Stores timestamped progress history for a task.

Fields:

- `task`: foreign key to `FarmTask`.
- `updated_by`: foreign key to `User`.
- `status`: `TODO`, `IN_PROGRESS`, or `DONE`.
- `comment`: optional worker progress note.
- `image`: optional progress image stored under `task_progress_images/`.
- `created_at`: timestamp created automatically when the update is saved.

Relationships:

- One `FarmTaskProgressUpdate` belongs to one `FarmTask`.
- One `FarmTaskProgressUpdate` is created by one `User`.

#### `tracker_fieldrecord`

Stores crop and field advice from an Agronomist.

Fields:

- `field`: foreign key to `Field`.
- `project`: optional foreign key to `FarmProject`.
- `created_by`: foreign key to `User`.
- `crop`
- `crop_stage`
- `advice`
- `recorded_on`

Relationships:

- One `FieldRecord` belongs to one `Field`.
- One `FieldRecord` may be linked to one `FarmProject`.
- One `FieldRecord` is created by one `User`.

### Relationship Summary

```text
User
  |-- one UserProfile
  |-- many FarmProject as manager
  |-- many FarmTask as assigned_to
  |-- many FieldRecord as created_by

Field
  |-- many FarmProject
  |-- many FieldRecord

FarmProject
  |-- many FarmTask
  |-- many FieldRecord

FarmTask
  |-- optional image upload
  |-- optional progress comment
  |-- many FarmTaskProgressUpdate
```

## Current Data Flow Examples

### Manager Creates Task

```text
Browser -> create_task view -> FarmTaskForm -> FarmTask table -> redirect home
```

The `FarmTaskForm` limits `assigned_to` choices to users whose `UserProfile.role` is `FIELD_WORKER`.

### Worker Updates Progress

```text
Browser -> update_task_progress view -> FarmTaskCompletionForm -> FarmTaskProgressUpdate table -> FarmTask latest summary -> redirect home
```

The view only allows a Field Worker to update tasks assigned to their own user account.

The worker can save:

- `status`
- `comment`
- optional `image`

Each worker update is stored as a timestamped `FarmTaskProgressUpdate`. The latest status/comment/image are also copied onto `FarmTask` so the dashboard can show the current task state quickly.

### Agronomist Creates Field Record

```text
Browser -> create_field_record view -> FieldRecordForm -> FieldRecord table -> redirect home
```

The view sets `created_by` to the logged-in Agronomist before saving.

## Notes For Future Improvements

- Add production environment details, such as configured environment variables and
  database provider, if the deployment setup changes.

## Deployment

The live PyFarm deployment is hosted on Render:

- Production URL: https://pyfarm.onrender.com
