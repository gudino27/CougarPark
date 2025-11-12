<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="https://github.com/gudino27/CougarPark/blob/30a8ab5afc85e5e37b9ed666cac9f71b3c31b6c7/cougarpark.png" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# COUGARPARK

<em>Transforming parking with intelligent, real-time solutions</em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/gudino27/CougarPark?style=flat&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
<img src="https://img.shields.io/github/last-commit/gudino27/CougarPark?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/gudino27/CougarPark?style=flat&color=0080ff" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/gudino27/CougarPark?style=flat&color=0080ff" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Flask-000000.svg?style=flat&logo=Flask&logoColor=white" alt="Flask">
<img src="https://img.shields.io/badge/JSON-000000.svg?style=flat&logo=JSON&logoColor=white" alt="JSON">
<img src="https://img.shields.io/badge/Markdown-000000.svg?style=flat&logo=Markdown&logoColor=white" alt="Markdown">
<img src="https://img.shields.io/badge/npm-CB3837.svg?style=flat&logo=npm&logoColor=white" alt="npm">
<img src="https://img.shields.io/badge/Jupyter-F37626.svg?style=flat&logo=Jupyter&logoColor=white" alt="Jupyter">
<img src="https://img.shields.io/badge/scikitlearn-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white" alt="scikitlearn">
<img src="https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=flat&logo=JavaScript&logoColor=black" alt="JavaScript">
<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white" alt="FastAPI">
<br>
<img src="https://img.shields.io/badge/React-61DAFB.svg?style=flat&logo=React&logoColor=black" alt="React">
<img src="https://img.shields.io/badge/NumPy-013243.svg?style=flat&logo=NumPy&logoColor=white" alt="NumPy">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Vite-646CFF.svg?style=flat&logo=Vite&logoColor=white" alt="Vite">
<img src="https://img.shields.io/badge/ESLint-4B32C3.svg?style=flat&logo=ESLint&logoColor=white" alt="ESLint">
<img src="https://img.shields.io/badge/pandas-150458.svg?style=flat&logo=pandas&logoColor=white" alt="pandas">
<img src="https://img.shields.io/badge/Pydantic-E92063.svg?style=flat&logo=Pydantic&logoColor=white" alt="Pydantic">

</div>
<br>

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [License](#license)

---

## Overview

CougarPark is pullman campus real-time parking occupancy predictions and enforcement insights, leveraging machine learning and comprehensive data integration. Its modular architecture includes APIs, data processing pipelines, and user interfaces, enabling scalable and maintainable smart parking solutions.

**Why CougarPark?**

This project aims to streamline users to find parking through predictive analytics and data-driven decision-making. 

## Features

| Component            | Details                                                                                     |
| :------------------- | :------------------------------------------------------------------------------------------ |
| **Architecture**     | <ul><li>Microservices architecture with FastAPI backend</li><li>Separation of concerns between API, models, and frontend</li></ul> |
| **Code Quality**     | <ul><li>Uses Pydantic for data validation</li><li>Structured project layout with src/ directory</li></ul> |
| **Documentation**    | <ul><li>Basic README with project overview</li><li>Includes API documentation via FastAPI's automatic docs</li><li>Contains dependency lists and setup instructions</li></ul> |
| **Integrations**     | <ul><li>Backend API built with **FastAPI** and **Flask** </li><li>Frontend uses **React** with **Vite** and **ESLint**</li><li>Supports **scikit-learn**, **XGBoost**, **LightGBM** for ML models</li><li>Uses **requests** for HTTP calls</li></ul> |
| **Modularity**       | <ul><li>Separate modules for occupancy and enforcement models</li><li>Models stored as JSON metadata files</li><li>Frontend and backend code separated</li></ul> |
| **Testing**          | <ul><li>Includes Jupyter notebooks for exploratory testing</li></ul> |
| **Performance**      | <ul><li>Uses **uvicorn** for ASGI server hosting FastAPI</li><li>Leverages optimized ML libraries like **XGBoost** and **LightGBM**</li></ul> |
| **Security**         | <ul><li>Uses **fastapi** with **pydantic** for input validation</li><li>Cross-Origin Resource Sharing (CORS) support via **flask-cors**</li></ul> |
| **Dependencies**     | <ul><li>Python dependencies via **requirements.txt** and **src/requirements.txt**</li><li>JavaScript dependencies via **package.json**</li><li>Includes ML libraries (**scikit-learn**, **xgboost**, **lightgbm**), visualization (**matplotlib**, **seaborn**), and web frameworks</li></ul> |

---

## Project Structure

```sh
└── CougarPark/
    ├── LICENSE
    ├── README.md
    ├── config.json
    ├── cougarpark
    │   ├── .gitignore
    │   ├── eslint.config.js
    │   ├── index.html
    │   ├── package-lock.json
    │   ├── package.json
    │   ├── public
    │   ├── src
    │   └── vite.config.js
    ├── models
    │   ├── enforcement_model_metadata.json
    │   └── occupancy_model_metadata.json
    ├── notebooks
    │   ├── enforcement
    │   ├── occupancy
    │   └── shared
    ├── requirements.txt
    └── src
        ├── feature_engineering.py
        ├── parking_api.py
        └── requirements.txt
```

---

### Project Index

<details open>
	<summary><b><code>COUGARPARK/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/config.json'>config.json</a></b></td>
					<td style='padding: 8px;'>- Defines configuration settings for the parking management system, specifying active predictive models, API server parameters, and feature toggles<br>- It orchestrates the integration of occupancy and enforcement risk prediction models, ensuring the system operates with the correct environment setup and feature availability, thereby supporting efficient parking occupancy forecasting and enforcement decision-making within the overall architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/LICENSE'>LICENSE</a></b></td>
					<td style='padding: 8px;'>- Provides the licensing information for the project, establishing legal permissions and restrictions<br>- It ensures users understand their rights to use, modify, and distribute the software while clarifying liability limitations<br>- This file underpins the projects open-source distribution, supporting its integration and collaboration within the broader codebase architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/README.md'>README.md</a></b></td>
					<td style='padding: 8px;'>- Provides core functionalities for predicting parking availability across WSU campus lots by leveraging machine learning models and processed data<br>- Facilitates real-time, granular parking forecasts, enabling users to locate parking efficiently, reduce search time, and improve campus traffic flow<br>- Serves as a foundational component within the broader system architecture, supporting data analysis, model deployment, and user-facing prediction features.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Defines project dependencies essential for data analysis, machine learning, and API development<br>- Ensures consistent environment setup for data processing with pandas and numpy, model training with scikit-learn and xgboost, visualization via matplotlib and seaborn, and deployment through FastAPI and Uvicorn<br>- Facilitates seamless integration of data workflows and scalable API services within the overall architecture.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- src Submodule -->
	<details>
		<summary><b>src</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ src</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/src/parking_api.py'>parking_api.py</a></b></td>
					<td style='padding: 8px;'>- Src/parking_api.pyThis file defines the core API for the CougarPark Smart Parking Prediction System<br>- It serves as the primary interface for interacting with the parking occupancy prediction model, enabling clients to request real-time parking occupancy forecasts<br>- The API orchestrates data processing, feature engineering, and model inference to deliver accurate predictions, integrating seamlessly within the overall system architecture to support intelligent parking management and decision-making.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/src/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Defines project dependencies essential for the CougarPark API, ensuring the environment supports web server functionality, data processing, and machine learning tasks<br>- It facilitates consistent setup across development and deployment environments, enabling reliable execution of API endpoints that leverage machine learning models for data analysis and predictions within the overall architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/src/feature_engineering.py'>feature_engineering.py</a></b></td>
					<td style='padding: 8px;'>- Provides feature engineering capabilities for parking occupancy prediction by generating relevant temporal, event, weather, enforcement, and historical lag features<br>- Integrates diverse data sources to produce comprehensive feature vectors, enabling accurate modeling of parking occupancy patterns and enforcement impacts within the broader prediction architecture.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- cougarpark Submodule -->
	<details>
		<summary><b>cougarpark</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ cougarpark</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/eslint.config.js'>eslint.config.js</a></b></td>
					<td style='padding: 8px;'>- Defines ESLint configuration to enforce coding standards and best practices across JavaScript and JSX files within the project<br>- It integrates recommended rules for JavaScript, React hooks, and React refresh, ensuring code quality, consistency, and compatibility with modern JavaScript features throughout the codebase.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/package.json'>package.json</a></b></td>
					<td style='padding: 8px;'>- Defines the core configuration for the cougarpark-dashboard, a React-based web application designed for interactive data visualization and user engagement<br>- It orchestrates development, build, and preview workflows, ensuring a streamlined process for creating and maintaining a modern, responsive dashboard interface within the overall project architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/vite.config.js'>vite.config.js</a></b></td>
					<td style='padding: 8px;'>- Configures the development environment for a React application using Vite, streamlining the build process and enabling fast, efficient development<br>- It integrates React-specific tooling to optimize module handling and hot-reloading, ensuring a smooth developer experience within the overall project architecture<br>- This setup supports rapid iteration and reliable deployment of the frontend interface.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/index.html'>index.html</a></b></td>
					<td style='padding: 8px;'>- Establishes the foundational HTML structure for the CougarPark Smart Parking web application, serving as the entry point that loads the React-based user interface<br>- It sets up the environment for dynamic parking management features, enabling users to access real-time parking information and interact with the system seamlessly within the WSU campus ecosystem.</td>
				</tr>
			</table>
			<!-- src Submodule -->
			<details>
				<summary><b>src</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ cougarpark.src</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/src/main.jsx'>main.jsx</a></b></td>
							<td style='padding: 8px;'>- Initialize the React application by rendering the main App component within a strict mode environment, ensuring adherence to best practices and enabling development checks<br>- This setup serves as the entry point for the project’s user interface, orchestrating the mounting of the core component into the DOM and establishing the foundation for the entire codebase’s frontend architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/src/App.jsx'>App.jsx</a></b></td>
							<td style='padding: 8px;'>- Provides the main interface for CougarPark, enabling users to select parking zones and times, fetch parking occupancy predictions, and view recommendations<br>- Integrates user inputs with backend ML models to deliver real-time parking insights, while managing state and orchestrating data flow across components to support smart parking decisions on the WSU campus.</td>
						</tr>
					</table>
					<!-- components Submodule -->
					<details>
						<summary><b>components</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ cougarpark.src.components</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/src/components/ZoneSelector.jsx'>ZoneSelector.jsx</a></b></td>
									<td style='padding: 8px;'>- Provides an interactive interface for selecting parking zones by fetching and filtering available lots from the backend<br>- Facilitates user search and selection, updating the applications state accordingly<br>- Integrates seamlessly within the overall architecture to enhance user experience in navigating parking options and managing zone-specific data.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/src/components/TimeSelector.jsx'>TimeSelector.jsx</a></b></td>
									<td style='padding: 8px;'>- Provides an interactive date and time selection component with integrated parking duration input<br>- Facilitates users in choosing precise reservation times, setting durations between 1 to 12 hours, and quickly updating to the current time<br>- Enhances user experience by combining date-time picking and duration management within a cohesive interface, supporting scheduling functionalities across the application.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/src/components/PredictionDisplay.jsx'>PredictionDisplay.jsx</a></b></td>
									<td style='padding: 8px;'>- Provides a user interface component for displaying parking predictions, including occupancy levels, enforcement risks, and tailored recommendations based on real-time data<br>- It visualizes model outputs, communicates uncertainty, and guides users on optimal parking decisions within the broader parking management architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/src/components/FeedbackForm.jsx'>FeedbackForm.jsx</a></b></td>
									<td style='padding: 8px;'>- Facilitates user feedback collection on parking prediction accuracy and availability within the application<br>- Enables users to confirm if parking was found and specify search duration, contributing real-time data to improve predictive models<br>- Integrates seamlessly into the overall architecture by providing a user-friendly interface for gathering actionable insights to enhance parking occupancy forecasts.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/src/components/FindParkingNow.jsx'>FindParkingNow.jsx</a></b></td>
									<td style='padding: 8px;'>- Provides an interactive component enabling users to quickly find optimal parking options in real-time<br>- It integrates seamlessly within the broader parking discovery platform, facilitating instant recommendations and enhancing user experience by streamlining the parking search process<br>- This component supports the applications goal of delivering efficient, user-friendly parking solutions.</td>
								</tr>
							</table>
						</blockquote>
					</details>
					<!-- services Submodule -->
					<details>
						<summary><b>services</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ cougarpark.src.services</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/cougarpark/src/services/apiService.js'>apiService.js</a></b></td>
									<td style='padding: 8px;'>- Provides an interface for interacting with backend APIs related to parking zone management, occupancy prediction, enforcement risk assessment, and user feedback<br>- Facilitates seamless data retrieval and submission to support real-time parking insights, enforcement strategies, and user engagement within the overall system architecture<br>- Acts as a crucial bridge connecting frontend components with backend services to enable dynamic, data-driven decision-making.</td>
								</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- models Submodule -->
	<details>
		<summary><b>models</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ models</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/models/enforcement_model_metadata.json'>enforcement_model_metadata.json</a></b></td>
					<td style='padding: 8px;'>- Defines the metadata for an XGBoost model predicting enforcement risk, incorporating lag and temporal features<br>- It summarizes model performance, hyperparameters, feature composition, and risk thresholds, serving as a reference for model evaluation, deployment, and interpretability within the broader enforcement risk prediction architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/models/occupancy_model_metadata.json'>occupancy_model_metadata.json</a></b></td>
					<td style='padding: 8px;'>- Defines metadata for the occupancy prediction model, capturing its type, training performance, feature composition, and data scope<br>- Serves as a reference for model evaluation and reproducibility within the overall architecture, ensuring clarity on the model’s purpose, data usage, and performance metrics across different training periods.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- notebooks Submodule -->
	<details>
		<summary><b>notebooks</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ notebooks</b></code>
			<!-- occupancy Submodule -->
			<details>
				<summary><b>occupancy</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ notebooks.occupancy</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/occupancy/02_occupancy_prediction_models.ipynb'>02_occupancy_prediction_models.ipynb</a></b></td>
							<td style='padding: 8px;'>- The <code>02_occupancy_prediction_models.ipynb</code> notebook is a key component of the project’s architecture focused on developing predictive models for parking occupancy<br>- It serves to analyze historical parking data and generate machine learning models that forecast parking availability, enabling proactive management of parking resources<br>- This notebook integrates with the broader system by providing accurate occupancy predictions, which can be utilized for real-time decision-making, optimizing parking lot operations, and enhancing user experience across the platform.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/occupancy/01_occupancy_data_transformation.ipynb'>01_occupancy_data_transformation.ipynb</a></b></td>
							<td style='padding: 8px;'>- Occupancy Data TransformationThis code file is a core component of the data processing pipeline that converts raw parking session data into actionable hourly occupancy insights<br>- It shifts the analytical focus from individual session durations to aggregated occupancy metrics, enabling more reliable and directly interpretable predictions of parking lot utilization<br>- This transformation supports the broader system by providing accurate, hourly occupancy rates per zone, facilitating better operational decision-making and resource planning within the parking management architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/occupancy/fix_paths.py'>fix_paths.py</a></b></td>
							<td style='padding: 8px;'>- Ensures consistent data path references within the occupancy data transformation notebook by updating relative directory paths<br>- This adjustment facilitates seamless access to data resources across different project directory levels, supporting reliable data processing workflows within the overall architecture<br>- The script enhances maintainability and reduces path-related errors during the data transformation process.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- shared Submodule -->
			<details>
				<summary><b>shared</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ notebooks.shared</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/04_lpr_calendar_enrichment.ipynb'>04_lpr_calendar_enrichment.ipynb</a></b></td>
							<td style='padding: 8px;'>- SummaryThe <code>04_lpr_calendar_enrichment.ipynb</code> notebook serves as a key component in the data pipeline, responsible for enhancing and enriching calendar-related data within the project<br>- It integrates and aligns calendar information with license plate recognition (LPR) data, enabling more accurate temporal and contextual analysis<br>- This enrichment process supports the broader architecture by providing refined, context-aware datasets that facilitate improved insights and decision-making across the system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/10_create_amp_zone_mapping.ipynb'>10_create_amp_zone_mapping.ipynb</a></b></td>
							<td style='padding: 8px;'>- Creates an enhanced mapping table linking detailed AMP zone names to standardized lot numbers and zone identifiers<br>- Facilitates consistent lot identification across datasets by translating diverse zone naming conventions into a unified format, supporting accurate data integration and analysis within the overall parking and lot management architecture<br>- The output CSV enables seamless referencing of zone aliases throughout the system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/09_model_validation_strategy.ipynb'>09_model_validation_strategy.ipynb</a></b></td>
							<td style='padding: 8px;'>- Model Validation Strategy-Avoiding Over/UnderfittingThis notebook outlines the approach for validating machine learning models within the project, focusing on strategies to prevent overfitting and underfitting<br>- It provides a systematic framework for assessing model performance, ensuring that the models generalize well to unseen data<br>- By establishing robust validation techniques, this component plays a critical role in maintaining the overall integrity and reliability of the predictive systems across the codebase.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/01_data_exploration.ipynb'>01_data_exploration.ipynb</a></b></td>
							<td style='padding: 8px;'>- Data Exploration NotebookThis notebook serves as the foundational step in the data pipeline, focusing on the initial examination of raw parking data received from the WSU Transportation Department<br>- Its primary purpose is to understand the structure, quality, and coverage of the dataset, including identifying missing values, discrepancies, and key patterns related to parking lot distribution and temporal coverage<br>- The insights gained here inform subsequent data preprocessing and modeling efforts, ensuring data integrity and relevance for the overall project architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/07_weather_enrichment.ipynb'>07_weather_enrichment.ipynb</a></b></td>
							<td style='padding: 8px;'>- The <code>07_weather_enrichment.ipynb</code> notebook serves as a key component in the data pipeline, responsible for integrating weather data into the broader dataset<br>- Its primary purpose is to enhance existing data with relevant weather information, enabling more comprehensive analysis and modeling<br>- This step is crucial for ensuring that weather-related factors are incorporated into the overall architecture, supporting downstream insights and decision-making processes across the project.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/03_calendar_enrichment.ipynb'>03_calendar_enrichment.ipynb</a></b></td>
							<td style='padding: 8px;'>- Summary of <code>notebooks/shared/03_calendar_enrichment.ipynb</code>This notebook serves as a key component in the data pipeline, responsible for enriching calendar-related data within the broader project architecture<br>- Its primary purpose is to enhance raw calendar datasets with additional contextual information, enabling more insightful analysis and downstream processing<br>- By integrating this enrichment step, the project ensures that calendar data is more comprehensive and aligned with the overall data architecture, supporting accurate time-based insights and decision-making across the system.---</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/06_fetch_weather_data.ipynb'>06_fetch_weather_data.ipynb</a></b></td>
							<td style='padding: 8px;'>- Fetch_weather_data.ipynbThis notebook is dedicated to retrieving and compiling historical weather data for the WSU Pullman campus, covering the period from January 1, 2020, to October 31, 2025<br>- It leverages the Open-Meteo Historical Weather API to gather key weather variables such as temperature, precipitation, snow depth, wind speed, and weather conditions<br>- This data serves as a foundational component for analyses related to environmental trends, campus planning, or climate impact assessments within the broader project architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/08_exploratory_data_analysis.ipynb'>08_exploratory_data_analysis.ipynb</a></b></td>
							<td style='padding: 8px;'>- Exploratory Data Analysis NotebookThis notebook serves as a foundational component of the project’s data pipeline, providing an in-depth exploration and understanding of the dataset<br>- It facilitates initial insights into data distributions, relationships, and quality, which are crucial for informing subsequent modeling and analysis steps within the overall architecture<br>- By systematically examining the data, this notebook helps ensure data integrity and guides feature engineering efforts, ultimately supporting the development of robust, data-driven solutions across the project.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/11_data_cleaning_validation.ipynb'>11_data_cleaning_validation.ipynb</a></b></td>
							<td style='padding: 8px;'>- This code file, <code>11_data_cleaning_validation.ipynb</code>, is dedicated to refining and validating parking lot data within the broader data processing pipeline<br>- Its primary purpose is to ensure the accuracy and relevance of parking data by removing obsolete or irrelevant lots, handling special zones such as event-specific or test areas, and confirming parking type classifications<br>- This step is crucial for maintaining data integrity, which underpins reliable analysis and decision-making related to parking management and transportation planning across the entire project architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/shared/02_data_preprocessing.ipynb'>02_data_preprocessing.ipynb</a></b></td>
							<td style='padding: 8px;'>- Data Preprocessing and CleaningThis notebook serves as a critical component in the data pipeline, responsible for preparing raw data for analysis and modeling<br>- It offers two preprocessing strategies—one that integrates License Plate Recognition (LPR) data with AMP data, and another that relies solely on AMP data with embedded zone information<br>- The notebook consolidates data from multiple sources, performs feature engineering focused on temporal aspects, and applies filtering and quality checks to ensure data integrity<br>- Overall, it standardizes and cleans the data, enabling reliable downstream analytics and machine learning tasks within the broader system architecture.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- enforcement Submodule -->
			<details>
				<summary><b>enforcement</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ notebooks.enforcement</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/07_lot_level_enforcement.ipynb'>07_lot_level_enforcement.ipynb</a></b></td>
							<td style='padding: 8px;'>- This code file focuses on transforming enforcement data from a zone-level aggregation to a more granular lot-level perspective<br>- By doing so, it enables precise enforcement predictions tailored to individual parking lots, such as garages and rec centers, recognizing that each lot exhibits unique enforcement patterns<br>- This enhancement supports more accurate, lot-specific enforcement strategies within the broader parking management system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/04_identify_fixed_cameras.ipynb'>04_identify_fixed_cameras.ipynb</a></b></td>
							<td style='padding: 8px;'>- SummaryThis notebook is dedicated to identifying fixed cameras within the surveillance system<br>- It processes and analyzes video data to distinguish stationary cameras from mobile or transient ones<br>- By accurately pinpointing fixed cameras, the code supports the broader systems goal of reliable camera management and monitoring, ensuring that subsequent analyses and operations are based on correctly classified camera sources<br>- This step is essential for maintaining the integrity of the surveillance infrastructure and enabling precise, automated enforcement workflows across the entire project architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/09_add_lot_names_to_enforcement.ipynb'>09_add_lot_names_to_enforcement.ipynb</a></b></td>
							<td style='padding: 8px;'>- Enhances enforcement data by integrating lot names for improved lookup and analysis<br>- It merges supplementary lot information into existing enforcement records, filling gaps with zone names where specific lot descriptions are missing<br>- This process facilitates more intuitive data interpretation and supports subsequent spatial or operational analyses within the broader project architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/10_create_zone_level_from_lots.ipynb'>10_create_zone_level_from_lots.ipynb</a></b></td>
							<td style='padding: 8px;'>- Aggregates enforcement data from individual lots to zone-level summaries, enabling analysis of enforcement activity and occupancy patterns across different zones<br>- Facilitates high-level insights into enforcement rates, environmental conditions, and temporal trends, supporting strategic decision-making and resource allocation within the broader enforcement and occupancy prediction architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/08_create_lot_level_enforcement.ipynb'>08_create_lot_level_enforcement.ipynb</a></b></td>
							<td style='padding: 8px;'>- SummaryThis notebook is designed to generate lot-level enforcement data by aggregating predictions at the individual lot level rather than by broader zones<br>- Its primary purpose is to enable more granular enforcement analysis, allowing each lot (such as CUE Garage, Library Garage, etc.) to have distinct enforcement predictions<br>- This enhances the precision of enforcement strategies within the overall system architecture, supporting targeted decision-making and resource allocation at the lot level.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/01_ticket_analysis.ipynb'>01_ticket_analysis.ipynb</a></b></td>
							<td style='padding: 8px;'>- Ticket Analysis & Enforcement NotebookThis notebook serves as the core component for analyzing support tickets and enforcing operational policies within the broader system architecture<br>- It processes ticket data to identify patterns, trends, and anomalies, enabling data-driven decision-making and policy enforcement<br>- By integrating insights from ticket analysis, the project aims to improve issue resolution efficiency, monitor compliance, and support proactive management across the platform.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/05_enforcement_risk_models.ipynb'>05_enforcement_risk_models.ipynb</a></b></td>
							<td style='padding: 8px;'>- Enforcement Risk Prediction ModelsThis notebook focuses on developing and evaluating machine learning models to assess enforcement risk<br>- It aims to identify and quantify potential enforcement actions likelihood, supporting proactive decision-making within the broader compliance and enforcement architecture<br>- By leveraging historical data and predictive analytics, this code contributes to the overall system's ability to prioritize enforcement efforts effectively and efficiently.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/06_extend_enforcement_to_oct2025.ipynb'>06_extend_enforcement_to_oct2025.ipynb</a></b></td>
							<td style='padding: 8px;'>- This code file extends enforcement data coverage through October 2025 by leveraging historical License Plate Recognition (LPR) patterns<br>- It integrates actual enforcement records up to late 2025 with estimated LPR data for the upcoming months, enabling comprehensive analysis of enforcement activities beyond the current data horizon<br>- This extension supports ongoing monitoring and evaluation of enforcement strategies within the broader data architecture, ensuring continuity and accuracy in enforcement metrics over an extended timeframe.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/03_enforcement_patterns_analysis.ipynb'>03_enforcement_patterns_analysis.ipynb</a></b></td>
							<td style='padding: 8px;'>- SummaryThe <code>03_enforcement_patterns_analysis.ipynb</code> notebook serves as a key analytical component within the enforcement module of the project<br>- Its primary purpose is to examine and identify common enforcement patterns, providing insights that inform the development and refinement of enforcement strategies across the system<br>- This analysis supports the overall architecture by enabling data-driven decision-making and ensuring enforcement mechanisms are both effective and aligned with project goals.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/gudino27/CougarPark/blob/master/notebooks/enforcement/02_enforcement_prediction.ipynb'>02_enforcement_prediction.ipynb</a></b></td>
							<td style='padding: 8px;'>- The <code>02_enforcement_prediction.ipynb</code> notebook serves as a core component for generating enforcement outcome predictions within the project<br>- It leverages the projects data pipeline and modeling framework to analyze enforcement-related data, producing predictive insights that support decision-making and enforcement strategies<br>- This notebook integrates with the broader architecture by utilizing data processed in earlier stages and contributing to the systems overall goal of enhancing enforcement efficiency through data-driven predictions.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** JupyterNotebook
- **Package Manager:** Pip, Npm

### Installation

Build CougarPark from the source and install dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/gudino27/CougarPark
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd CougarPark
    ```

3. **Install the dependencies:**

**Using [pip](https://pypi.org/project/pip/):**

```sh
❯ pip install -r requirements.txt, src/requirements.txt
```
**Using [npm](https://www.npmjs.com/):**

```sh
❯ npm install
```

### Usage

Run the project with:

**Using [pip](https://pypi.org/project/pip/):**

```sh
python {src/parking_api.py}
```
**Using [npm](https://www.npmjs.com/):**

```sh
npm run dev
```

### Testing

Cougarpark uses the {__test_framework__} test framework. Run the test suite with:

**Using [pip](https://pypi.org/project/pip/):**

```sh
pytest
```
**Using [npm](https://www.npmjs.com/):**

```sh
npm test
```

---

## License

Cougarpark is protected under the [MIT License](https://choosealicense.com/licenses) License. For more details, refer to the [MIT License](https://choosealicense.com/licenses/) file.

---

<div align="left"><a href="#top">⬆ Return</a></div>

---
