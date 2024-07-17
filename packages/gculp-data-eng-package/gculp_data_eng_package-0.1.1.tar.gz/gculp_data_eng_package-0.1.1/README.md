## Strava Modern Data Stack
This is a project used to analyze my strava data using the modern data stack

## Project Inspiration
Please check out the other amazing projects that inspired me and this project
- https://github.com/matsonj/nba-monte-carlo
- https://github.com/dagster-io/mdsfest-opensource-mds

## Run Locally
- Set `PYTHONPATH` environment variable

## Renovate
https://developer.mend.io/github/culpgrant/strava_mds

# TODO:
- look into package called dbt-coverage
- A unit test to make sure every function is added in the __all__ in the __init__ file (Why again?)

- still need to finalize Dagster working via docker locally
- DBT add a test that all yml files in the DBT project start with `_`
- Run the CI Pipeline as apart of the Release Pipeline
- And Update the CI Pipline to have python as an environment variable

- For the release pipeline how can I get the description like Polars has (Performance Improvements, Features, Bugs, Documentation, Misc) and then list the PR in those areas
