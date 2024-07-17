[![CodeFactor](https://www.codefactor.io/repository/github/thisun1997/infant_pose_application_backend/badge)](https://www.codefactor.io/repository/github/thisun1997/infant_pose_application_backend)

<h1>Introduction</h1>

This codebase contains the backend API implementations of the <i>Infant Pose Visualizer</i> application. Flask micro framework with Blueprints are used for the development. The following endpoints are available for consumption:
when running in localhost base url is: `http://127.0.0.1:5000/`

| API method | endpoint                          | Description                                                                  |
|:-----------|:----------------------------------|:-----------------------------------------------------------------------------|
| POST       | users/auth                        | Authenticate the logging user                                                |
| GET        | patients/                         | Fetch registration_id and name of all the patients                           |
| POST       | patients/registration             | Register a new patient                                                       |
| GET        | patients/data                     | Fetch data of a patient using registration_id                                |
| PUT        | patients/update_data              | Update data of a registered patient                                          |
| PUT        | patients/update_data              | Update data of a registered patient                                          |
| GET        | model_loader/                     | Fetch all the available model configurations                                 |
| PUT        | model_loader/update_model         | Change the active model                                                      |
| GET        | model_loader/get_model            | Fetch the active model configurations                                        |
| POST       | visualizations/prediction         | Make the pose prediction and save it in database                             |
| PUT        | visualizations/update             | Update visualization record by adding medical remark                         |
| GET        | visualizations/visualization_data | Fetch a visualization record                                                 |
| GET        | visualizations/history_data       | Fetch visualization records of a specific patient within a given time period |
| GET        | feedback/             | Fetch all feedback data                                                      |
| POST       | feedback/add             | Add a specific or general feedback                                           |
| GET        | feedback/get             | Get the feedback relevant to a given visualization record                    |

The GUIs related to the application are available [here](https://github.com/Thisun1997/infant_pose_estimation_frontend).

<h1>How to get started?</h1>

1. Install the dependencies available in [requirements.txt](requirements.txt).
2. Upload the `.pth` file relevant to the fusion models you hope to use, to the `model` folder. Links for the downloadable `.pth` files of different fusion models are shown in the [models](#models) section below.
3. You have to setup a Mongo database in localhost.
   1. Create a database named `infant_pose_visualizer_system`.
   2. Create a collection `models` and insert data relevant to the fusion models uploaded in the following format.
      ```{"model_type":"HRNet_fusion","status":"Active","fuse_stage":<fusion_stage>,"fuse_type":<fusion_type>>,"model_name":<name_of_model>,"best_model_path":<.pth_file_name_of_model>}```<br>
      `status` should be set to `Active` in only one model and in others just set to an empty string (`""`). 
4. Locate the root folder of the codebase. 
5. Execute `flask run`.

<a id="models"></a><h1>Models</h1>
Below are the links to the .pth files of the fusion models, ranked in order of their performance, starting with the best.

| Fusion stage  | Fusion type   |                                         .pth file                                          |
|:-------------:|:-------------:|:------------------------------------------------------------------------------------------:|
|       2       | iAFF          | [file](https://drive.google.com/file/d/1vD8z0_tQoTiCJpY8uYMBcUoY--j64bnJ/view?usp=sharing) |
|       3       | Addition      | [file](https://drive.google.com/file/d/1u9Eg-dRNWigjiV2no84_UshDPWgL_lFc/view?usp=sharing) |
|       3       | iAFF          | [file](https://drive.google.com/file/d/1-mCN4efgxjbIBoOTZkEWDbXjzqxMGfZA/view?usp=sharing) |
|       2       | Concatenation | [file](https://drive.google.com/file/d/1vD8z0_tQoTiCJpY8uYMBcUoY--j64bnJ/view?usp=sharing) |
