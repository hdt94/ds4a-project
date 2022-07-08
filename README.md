# DS4A Capstone Project - Team 60

## Up and running

The services and web app have been developed applying best practices from cloud-native approach for flexibility regarding computing environment, that is, customizing environment configuration through variables and running containerized processes. These can then be run in local machine, cloud virtual machine instances, cloud PaaS services, or even Kubernetes clusters.

### Prework

Following analytics prework is required:
- Cleaning and saving raw datasets into `data/clean` directory. Use `core_ds4a_project.datasets.read_joining_datasets()` function to save CARTERA, CLIENTES, and COLOCACION datasets. Refer to Jupyter Notebooks in `analytics/cleaning` for detaily explanations.
- Building analytics models for recommendations and save them into `services/recommendations/models/` directory. This also includes dictionary `dict-defaulting-variable-category-code.json` for mapping input data to category coded data. Refer to Jupyter Notebooks in `analytics/exploring` for detaily explanations.

### Production

Build container images and lift up containers:
```bash
docker-compose \
    -f docker-compose.common.yaml \
    -f docker-compose.prod.yaml \
    up --build
```
