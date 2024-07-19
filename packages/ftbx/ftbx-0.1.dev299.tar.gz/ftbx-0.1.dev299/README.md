# FTBX - FLEX TOOLBOX

Just trying to make flex operations faster for all teams.

## Table of Contents

  - [Requirements](#requirements)  
  - [Installation](#installation)  
    - [Windows](#1-windows)  
    - [Linux](#2-linux)  
    - [macOS](#3-macos)
  - [Usage](#commandssetup)
    - [ftbx update](#update)
    - [ftbx connect](#connect)  
    - [ftbx setup](#setup-optional)
    - [ftbx query](#raw-queries)  
    - [ftbx list](#list-items)  
    - [ftbx pull](#pull-items)  
    - [ftbx create](#create-items)
    - [ftbx push](#push-items)  
    - [ftbx restore](#restore-items)  
    - [ftbx compare](#compare-items)  
    - [ftbx retry](#retry-items)  
    - [ftbx launch](#launch-instances--custom-scripts)  
    - [ftbx workflowDesigner](#workflow-designer)
    - [ftbx metadataDesigner](#metadata-designer)
  - [Errors & fixes](#errors--fixes)  
    - [SSLCertVerificationError](#self-signed-certificates)  
  - [Contact](#contacts)  

## __Bug/Feature Bounty Hunters__

| Bounty Hunter          | Bugs found | Features suggested | PR merged | Bounties |
|------------------------|------------|--------------------|-----------|----------|
| **Elouan GOUINGUENET** | 1          | 5                  | 1         | 7        |
| **Guillaume GAY**      | 1          | 2                  | 0         | 3        |
| **Gustavo BONASSO**    | 2          | 0                  | 1         | 3        |
| **Hugo TALBOT**        | 0          | 1                  | 1         | 2        |
| **Bowen ZHANG**        | 1          | 0                  | 0         | 1        |
| **Julius SANTUA**      | 0          | 1                  | 0         | 1        |
| **Rémi MARCHAND**      | 1          | 0                  | 0         | 1        |
| **TOTAL**              | **6**      | **9**              | **3**     | **18**   |

> See HUNT.md for full history

# __REQUIREMENTS__

#### [Git (click here to download)](https://git-scm.com/downloads)

#### [Python 3.10 (click here to download)](https://www.python.org/downloads/release/python-31011/)

***

# __INSTALLATION__

## Install python

#### Windows

* link above

#### Linux

```shell
sudo apt install python3-pip
```

#### macOS

```shell
brew install python
```

## Install FTBX

```shell
pip install ftbx
ftbx init
```

## Update FTBX

```shell
ftbx update
```

# __USAGE__

You can use the flag `--help` with any command to show the command arguments (see below).  

```shell
ftbx --help

# output
                        Tools
init                Initialize Flex ToolBox (multi-OS)
update              Fetches the newest version of the toolbox
connect             Connect to a Flex env (url, username, pwd)
env                 Show available environments and default environment
setup               Download the documentation and SDK for a given Flex version
query               Query (GET, POST, PUT) an environment with or without payload (file or command line arguments)
list                List (to CSV & JSON) config items from an environment, with filters and post-filters
pull                Pull (files & folders) config items from an environment, with filters and post-filters
create              Create a config item within an environment if no item with same name already exist
push                Push (create or update) config items to an environment
restore             Restore config items to a previous point in time
compare             Compare config items against several environments
retry               Retry or bulk retry config item instances within an environment
launch              Launch a config item instance within an environment
workflowDesigner    Opens a browser window with the given workflow designer
metadataDesigner    Opens a browser window with the given metadata designer
```

```shell
ftbx retry --help

# output
usage: ftbx.py retry [-h] [--from FROM_] [--filters [FILTERS ...]] [--file FILE] {jobs,workflows}

positional arguments:
  {jobs,workflows}      Config item

optional arguments:
  -h, --help            show this help message and exit
  --from FROM_          Environment to retry from
  --filters [FILTERS ...]
                        Filters to apply
  --file FILE           File containing items to retry

```

# __Update__

```shell
ftbx update
```

This command fetches the latest version of the toolbox.

# __Connect__

```shell
ftbx connect <env_url_or_alias> <username> --alias <env_alias>  
```

> options:  
> --alias [String]: alias to set for the environment (ex: wb-stg for warner brother STG)  

This command does 4 things:  
   
- input you to enter password in hidden characters  
- check connection against the env with url, username and password  
- add environment credentials to your environmentsif successful (encrypted)
- set the environment as your default environment if successful

If you're looking for how to connect to self-signed environments, see [here](#4-connect-to-self-signed-environments).

---

#### 1. Connect to a new environment

```shell
# connect without showing password (will prompt you to input password and hide characters)
ftbx connect "https://devstaging.flex.daletdemos.com" "username" --alias "devstaging"

# connect with plain password
ftbx connect "https://devstaging.flex.daletdemos.com" "username" "my_password" --alias "devstaging"
```

```shell
# OUTPUT

STATUS: Connection successful (0.267 seconds)

DEFAULT ENVIRONMENT: https://master.cs-sandbox.flex.cs.dalet.cloud [cs-sandbox-ovh-flex-config] as masteruser
```

---

#### 2. Connect to a known environment (must be in `environments`)

```shell
# Full URL
ftbx connect "https://devstaging.flex.daletdemos.com"

# Alias
ftbx connect "devstaging"
```

```shell
# OUTPUT

STATUS: Connection successful (0.267 seconds)

DEFAULT ENVIRONMENT: https://master.cs-sandbox.flex.cs.dalet.cloud [cs-sandbox-ovh-flex-config] as masteruser
```

---

#### 3. Display available default environments

```shell
ftbx env
```

```shell
# OUTPUT

DEFAULT             ALIAS                                   URL                       USERNAME  
   X        cs-sandbox-ovh-flex-config https://master.cs-sandbox.flex.cs.dalet.cloud masteruser  
        devstaging.flex.daletdemos.com        https://devstaging.flex.daletdemos.com    dnaisse  
                                wb-dev     https://portal.dev.archive.warnerbros.com    dnaisse  
                                wb-stg      https://vault.stg.archive.warnerbros.com    dnaisse  
                               wb-prod          https://vault.archive.warnerbros.com    dnaisse  
          master.firstmedia.ooflex.net          https://master.firstmedia.ooflex.net masteruser  
```

#### 4. Connect to self-signed environments

Environments deployed with a self-signed certificate are not trusted by default. In order to trust this certification authority, set the environment variable `REQUESTS_CA_BUNDLE` to the path to the certificate of the root certification authority. Like:

```shell
# POSIX
export REQUESTS_CA_BUNDLE=/path/to/cert

# Windows - PowerShell
Set-Item Env:REQUESTS_CA_BUNDLE "path\to\cert"
```

#### Download Flex root certificate authority certificate

This can be done with most web browser. But here is a command for POSIX system.

```shell
echo quit | openssl s_client -showcerts -servername "devstaging.flex.daletdemos.com" -connect devstaging.flex.daletdemos.com:443 > cacert.pem
```

# __Setup__ (optional)

```shell
ftbx setup <flex_version>
```

This command will download the API documentation and the SDK for the specific Flex version.
   
- API documentation will go in `docs/`  
- SDK (.jar) will go in `sdks/`

Once the SDK is downloaded, you simply have to add it to your modules in your favorite IDE.

> Note: you have to be connected to the `dlt-fw-uk-UDP4-1120-full-config` VPN to be able to retrieve the SDK.

---

#### 1. Setup

```shell
ftbx setup "2022.5.7"
```

```shell
# OUTPUT

Version: 2022.5.7 (2022.5.x)

DOCUMENTATION: 2022.5.7.yml has been downloaded to docs/2022.5.7.yml

# if you are not connected to the VPN
/!\ Failed to download the sdk. Please connect to the dlt-fw-uk-UDP4-1120-full-config VPN /!\ 
# if you are connected to the VPN
SDK: flex-sdk-external-5.2.10.9.jar has been downloaded to sdks/flex-sdk-external-5.2.10.9.jar.
```

# __Raw Queries__

```shell
ftbx query <method> <long_or_short_query>
```

> options:  
> --from [String] environment to query if not default environment  
> --payload [String] path to payload (JSON) file or payload arguments
> --stdout [Boolean - default:False] print the query response in the terminal (does not disable writing to query.json)

This command queries any env (without the need of setting up headers etc...) and stores the result in a query.json file.  

---

#### 1. Query absolutely everything

```shell
# GET (commands below are the same)

# Default env
ftbx query GET "actions/410"
# Full url
ftbx query GET "https://master.cs-sandbox.flex.cs.dalet.cloud/api/actions/410"
# Env alias
ftbx query GET "actions/410" --from "cs-sbx"
# Print query response to terminal
ftbx query GET "actions/410" --stdout

# POST/PUT (same args as above, plus --payload)
ftbx query PUT "actions/410/configuration" --payload "payload.json"

# Cancel a failed job with command line arguments
ftbx query POST "jobs/1213/actions" --payload "action=cancel"
```

```shell
# OUTPUT

Performing [GET] https://master.cs-sandbox.flex.cs.dalet.cloud/api/actions;limit=10...  
  
Result of the query has been saved in query.json for your best convenience.  
```

# __List items__

```shell
ftbx list <config_item>
```

> options:  
> --from [String]: environment to query if not default environment  
> --filters [String(s)]: filters to apply, that are used directly within the query (see available filters [here](https://help.dalet.com/daletflex/admin/developer_guide/apis/apis.html))  
> --post-filters [String(s)]: post retrieval filters, that are applied after query (operators: '!=', '!~', '>=', '<=', '~', '=', '<', '>')  
> --name [String]: filename of the output file

This command queries any env and displays the main info of the requested items, as well as the requested post_filters
values. A folder and two files will then be created:  

- `lists/`  
  - `<timestamp>_<env_alias>_<config_item>_<filters>_<post-filters>.json`  
  - `<timestamp>_<env_alias>_<config_item>_<filters>_<post-filters>.csv`  

---

#### 1. List anything

  ```shell
  # List all actions 
  ftbx list actions

  # List all assets with fql
  ftbx list assets --filters "fql=(mimetype~mp4)" --name "mp4Assets"
  
  # List 5 jobs in a failed status 
  ftbx list jobs --filters "status=Failed" "limit=5" --name "failedJobs"
  
  # List scripts that contains "createJob"
  ftbx list actions --filters "type=script" --post-filters "configuration.instance[text]~createJob"
  
  # List jobs for which the last (-1) history message is an error message containing "getName()" in its stackTrace
  ftbx list jobs --filters "name=basic-long-running-action" --post-filters "history.events[-1].stackTrace~getName()"
  
  # List all actions with concurrency > 0 from default env
  ftbx list actions --post-filters "concurrencyJobsLimit>0" --name "jobsWithConcurrencyLimit"

  # List workflows that completed, and get some metadata fields from the asset the workflow was on
  ftbx list workflows --filters "name=my_workflow" "status=Completed" --post-filters "asset.metadata.instance.general-info.sha1!=None" "asset.fileInformation.currentLocation!=None"
  
  # List all workflows in a corrupted state
  ftbx list workflows --filters "status=Running" --post-filters "jobs.jobs[-1].status!=Running"

  # List events of type 'Login Failed' from April 1, 2024 to May 14, 2024
  ftbx list events --filters "eventType=Login Failed" "from=01 Apr 2024" "to=14 May 2024"
  ```
  
> Note: FQL search has a max number of results of 10 000, so if you need any more than that, you will have to split your FQL search in multiples other ones.

  ```shell
  # OUTPUT
  
  Performing [GET] https://portal.dev.archive.warnerbros.com/api/actions;type=script;limit=10...

  Retrieving actions: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.46it/s]
  Retrieving actions []: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<?, ?it/s]

                     name                   id    type.name                       pluginClass
  1          action-modified-test-script  1874308   script   tv.nativ.mio.plugins.actions.script.GroovyScriptCommand
  2    create-placeholder-sequence-group  1856453   script   tv.nativ.mio.plugins.actions.script.GroovyScriptCommand
  3   delete-asset-from-bm-event-handler  1856600   script   tv.nativ.mio.plugins.actions.script.GroovyScriptCommand
  4                   prepare-delete-udo  2026696   script    tv.nativ.mio.plugins.actions.jef.JEFActionProxyCommand
  5                 sc-create-collection  1863345   script    tv.nativ.mio.plugins.actions.jef.JEFActionProxyCommand
  6                sc-sharing-collection  1863346   script    tv.nativ.mio.plugins.actions.jef.JEFActionProxyCommand
  7                                 test  2338482   script   tv.nativ.mio.plugins.actions.script.GroovyScriptCommand
  8                update-gatorsky-to-in  1856601   script   tv.nativ.mio.plugins.actions.script.GroovyScriptCommand
  9                   wamo-purge-trigger  1917236   script   tv.nativ.mio.plugins.actions.script.GroovyScriptCommand
  10                 wamo-query-aws-sign  1837898   script   tv.nativ.mio.plugins.actions.script.GroovyScriptCommand

  Results of the query have been saved as list.json for your best convenience.
  ```

# __Pull items__

```shell
ftbx pull <config_item>
```

> options:  
> --from [String(s)]: environments to pull from if not default environment  
> --filters [String(s)]: filters to apply, that are used directly within the query (see available filters [here](https://help.dalet.com/daletflex/admin/developer_guide/apis/apis.html))  
> --with-dependencies [Boolean - default:False]: whether to retrieve all the items dependencies (ex: workflows of launch actions etc..)  
> --post-filters [String(s)]: post retrieval filters, that are applied after query (operators: '!=', '>=', '<=', '~', '=', '<', '>')  


This command queries any env and locally creates folders/files for the requested items. Structure will be in the following format:  

- `<config_item>/`  
    - `<item_name>/`  
        - `_object.json`: main config of the item  
        - `<item_property>.json`: item properties (ex: configuration, variables, status..)  
        - `script.groovy`: groovy file with code if any (actions etc...)  
        - `body.html`: html file with html code if any (message templates etc...)  

---

#### 1. Pull anything

```shell
# Pull **ALL** actions
ftbx pull actions # default env
ftbx pull actions --from "wb-stg"

# Pull actions matching filters
ftbx pull actions --filters "name=set-asset-metadata" --from "wb-stg"
ftbx pull actions --filters "id=309" # default env
ftbx pull actions --filters "enabled=true" # default env
ftbx pull actions --filters "type=script" --from "wb-stg"
ftbx pull actions --filters "type=script" "enabled=true" # default env

# Pull **ALL**
ftbx pull all
ftbx pull all --from "wb-stg"

# Pull env actions with dependencies
ftbx pull actions --with-dependencies # default env

# Pull all actions where script contains "context.asset.id"
ftbx pull actions --post-filters "configuration.instance[text]~context.asset.id"

# Pull workflow definitions with dependencies
ftbx pull workflowDefinitions --filters "name=ingest-workflow" --with-dependencies

# Pull actions from several envs at the same time
ftbx pull actions --from "wb-dev" "wb-stg" "wb-prod" --filters "name=set-asset-metadata"
```

# __Create items__

```shell
ftbx create <config_item> <plugin> <item_name>
```

> options:  
> --in [String] environment to create the item in  

This command creates templated items in the destination environments.

---

#### 1. Create items

```shell
# Create a script action in default environment
ftbx create actions script "set-asset-metadata"

# Create a script action in a specific environment
ftbx create actions script "set-asset-metadata" --in "wb-stg"

# Create a decision action 
ftbx create actions decision "check-asset-status" --in "wb-stg"

# Create a launchWorkflow wizard
ftbx create wizards launchWorkflow "launch-my-workflow"
```

# __Push items__

```shell
ftbx push <config_item> <item_name>
```

> options:  
> --from [String] environment to push from if not default environment  
> --to [String(s)] environments (yes, several at the same time is possible) to push to if not default environment  
> --push-to-failed-jobs [Boolean or String - default:False] whether to update and restart failed jobs if item is an action. If a string is provided, it must be the path to either a .CSV or .JSON (see examples in 1.)  
> --with-dependencies [Boolean or String - default: False] whether to also push the item dependencies  
> --include-resources [Boolean or String - default: False] /!\ whether to also push resource configurations, this will overwrite the corresponding destination environment resource configurations /!\  
> --retry [Boolean or String - default: False] whether to retry the item you are pushing (jobs, workflows...)  
> --listen [Boolean or String - default: False] whether to listen to the item you are pushing (jobs)

This command pushes local items to the destination environments. Process is as shown below:  

1. check if item exists locally  
   - yes: continue  
   - no: stop  
2. check if item exists in the destination environment  
   - yes: pull to `<item_name>/backup/` in case you break something  
   - no: create it in destination environment  
3. push updated item properties (ex: configuration.json, script.groovy etc..)
4. [OPTIONAL] push item dependencies if --with-dependencies was given
5. pull updated items from the destination environment for verification purposes  
6. [OPTIONAL] retry given failed jobs with new configuration if --retry  
7. [OPTIONAL] listen to a retried job and have the logs in your terminal    

- CSV (same as .csv file resulting from `ftbx list`)   

CSV file must contain at least the "id" column, the number/name/order of the other columns doesn't matter.  

| id  | other column name | other column status |
|-----|-------------------|---------------------|
| 238 | job1              | Failed              |
| 239 | job2              | Failed              |
| 240 | job3              | Failed              |

- JSON (same as .json file resulting from `ftbx list`)    

JSON file must contain a dict with an "id" key for each instance, the number/name/order of the other keys doesn't matter.  

```json
{
  "failed_job_1": {"id": 238, "other_key_1": "..."},
  "failed_job_2": {"id": 239, "other_key_1": "..."},
  "failed_job_3": {"id": 240, "other_key_1": "..."},
  ...
}
```

---

#### 1. Push anything

```shell
# Push action to an env
ftbx push actions check-end-node-wf # from default env to default env

# Push job and retry it (yes, you can pull jobs directly and tweak their code in your IDE)
ftbx push jobs 294036 --retry

# Push job, retry it but also LISTEN to it (logs will appear in your terminal)
ftbx push jobs 294036 --retry --listen

# Push updated action to **ALL** corresponding failed jobs and retry them
ftbx push actions "check-end-node-wf" --push-to-failed-jobs

# Push updated action to failed jobs contained in .CSV or .JSON and retry them
ftbx push actions "check-end-node-wf" --push-to-failed-jobs "failed_jobs.csv"
ftbx push actions "check-end-node-wf" --push-to-failed-jobs "failed_jobs.json"

# LIST + PUSH with RETRY flow: push & retry failed jobs created after given date
ftbx list jobs --filters "name=check-end-node-wf" "createdFrom=20 Dec 2023"
ftbx push actions "check-end-node-wf" --push-to-failed-jobs "list.json"
ftbx push actions "check-end-node-wf" --push-to-failed-jobs "list.csv"

# Push (create, or update) action from wb-dev to wb-stg AND wb-prod (yes)
ftbx push actions "set-asset-metadata" --from "wb-dev" --to "wb-stg" "wb-prod"  

# Push/update workflow definition WITHOUT updating the resources configuration
ftbx push workflowDefinitions "Get Or Compute Asset Checksum" --from "templates" --to "cs-sandbox-ovh-flex-config" --with-dependencies

# Push workflow definition with ALL its dependencies (actions, resources...)
ftbx push workflowDefinitions "Get Or Compute Asset Checksum" --from "templates" --to "cs-sandbox-ovh-flex-config" --with-dependencies --include-resources
```

# __Restore items__

```shell
ftbx restore <config_item> <item_name> <timestamp_or_backup_name>
```

This command restores an item from a backup (every push generates a backup) in case you break something.  

---

#### 1. Restore backup (in config_item/item_name/backup)

```shell
ftbx restore actions set-tech-metadata-dpx "2023-10-10 15h53m43s"
```
  
# __Compare items__

```shell
ftbx compare <config_item> <list_of_envs>
```

> options:  
> --filters [String(s)]: filters to apply, that are used directly within the query (see available filters [here](https://help.dalet.com/daletflex/admin/developer_guide/apis/apis.html))  

This command compares items from different environments. The first environment provided in the list is always the reference environment. The list of differences will then be saved in a `compare_<env1>_<env2>_.../` folder with a TSV file for each item (no file if no differences).  

---

#### 1. Compare items

```shell
# Compare action "check-end-node-wf" between wb-dev, wb-stg and wb-prod
ftbx compare actions "wb-dev" "wb-stg" "wb-prod" --filters "name=check-end-node-wf"

# Compare **ALL** actions between wb-dev, wb-stg and wb-prod
ftbx compare actions "wb-dev" "wb-stg" "wb-prod"
```

```shell
# OUTPUT
Performing [GET] https://vault.stg.archive.warnerbros.com/api/metadataDefinitions;name=Asset;limit=1...

Retrieving 1 metadataDefinitions: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.83it/s]
Retrieving metadataDefinitions ['definition']: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.53it/s]

Performing [GET] https://vault.archive.warnerbros.com/api/metadataDefinitions;name=Asset;limit=1...

Retrieving 5 metadataDefinitions: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.51it/s]
Retrieving metadataDefinitions ['definition']: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  4.51it/s]

Comparing items between ['wb-stg', 'wb-prod']: 100%|████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 139.47it/s]

Result of the comparison (if there are any differences) have been saved in compare_wb-stg_wb-prod/metadataDefinitions/<item_name>.tsv for your best convenience. 
```

# Retry items

```shell
ftbx retry <config_item> <options>
```

> options:  
> --filters [String(s)]: filters to apply, that are used directly within the query (see available filters [here](https://help.dalet.com/daletflex/admin/developer_guide/apis/apis.html))  
> --from [String]: environment alias if not default  
> --file [String]: JSON or CSV file to take as input  

This command bulk retries job/workflow instances within a Flex environment, either from a query or from JSON/CSV files (see formats below).    

- CSV (same as .csv file resulting from `ftbx list`)    

CSV file must contain at least the "id" column, the number/name/order of the other columns doesn't matter.    

| id  | other_column_name | other_column_status |
|-----|-------------------|---------------------|
| 238 | job1              | Failed              |
| 239 | job2              | Failed              |
| 240 | job3              | Failed              |

- JSON (same as .json file resulting from `ftbx list`)    

JSON file must contain a dict with an "id" key for each instance, the number/name/order of the other keys doesn't matter.    

```json
{
  "failed_job_1": {"id": 238, "other_key_1": "..."},
  "failed_job_2": {"id": 239, "other_key_1": "..."},
  "failed_job_3": {"id": 240, "other_key_1": "..."},
  ...
}
```

---

### 1. Retry instances

```shell
# "status=Failed" is applied by the command by default 

# retry 5 failed "untar-frames" jobs with query
ftbx retry jobs --filters "name=untar-frames" "limit=5"

# retry all failed "untar-frames" jobs
ftbx retry jobs --filters "name=untar-frames"

# retry **ALL** failed jobs/workflows
ftbx retry jobs
ftbx retry workflows

# retry all failed jobs from a CSV file (CSV file must contain the "id" column)
ftbx retry jobs --file "failed_jobs.csv"

# retry all failed workflows from a JSON file (JSON file must be made of a dict for each instance, with a "id" key within each dict)
ftbx retry workflows --file "failed_workflows.json"

# LIST + RETRY flow
ftbx list jobs --filters "status=Failed" "name=untar-frames" --name "list" # this will create a JSON and CSV file with the failed items 
ftbx retry jobs --file "lists/list.json" # same as below
ftbx retry jobs --file "lists/list.csv" # same as above
```

# Launch instances & custom scripts

```shell
ftbx launch <config_item> <item_name> <options>
```

> options:  
> --in [String]: environment alias if not default  
> --params [String(s)]: params to use for the launched instance (see available parameters [here](https://help.dalet.com/daletflex/admin/developer_guide/apis/apis.html))  
> --from-file [String]: JSON file to take as input (contained values will replace --params)  
> --use-local [Boolean - default: False]: whether to push the local config before launching the instance  
> --listen [Boolean or String - default: False] whether to listen to the item you launched (jobs)

This command allows you to launch config instances (jobs, workflows) with custom parameters, including scripts with or without asset in context.  

To be able to run any custom local script within an environment, please create a script in the destination environment with a unique name first (ex: `ftbx-script-dnaisse-wb-dev`). The flow will be explained in 2.  

---

### 1. Launch instances

```shell
# launch a check-end-node-wf job
ftbx launch jobs "check-end-node-wf"

# launch a check-end-node-wf job in wb-dev
ftbx launch jobs "check-end-node-wf" --in "wb-dev"

# launch and listen to a check-end-node-wf in wb-dev
ftbx launch jobs "check-end-node-wf" --in "wb-dev" --listen

# launch a check-end-node-wf on asset id 809, in workspace id 303
ftbx launch jobs "check-end-node-wf" --params "assetId=809" "workspaceId=303"

# launch a check-end-node-wf on asset id 809 from file launch_config.json
# launch_config.json:
# {
#   "assetId"=809,
#   "workspaceId"=303
# } 
ftbx launch jobs "check-end-node-wf" --from-file "launch_config.json"

# launch a check-end-node-wf with your local configuration on asset id 809
ftbx launch jobs "check-end-node-wf" --params "assetId=809" --use-local
```

---

### 2. Launch custom local scripts

To be able to run any custom local script within an environment, please create a script in the destination environment with a unique name first (ex: `ftbx-script-dnaisse-wb-dev`). This script will be used as an ultra-configurable, multi-purpose action.  

#### 2.1. Same action, different code, different assets

```shell
# Example: I want to set some metadata on asset id 809  
# 1. I update the code of my local ftbx-script-dnaisse-wb-dev to do what I want

# wb-dev/actions/ftbx-script-dnaisse-wb-dev/script.groovy:

# import com.ooyala.flex.plugins.PluginCommand
# 
# class Script extends PluginCommand {
#   def execute() {
#     assetId = context.asset.id
#     flexSdkClient.assetService.setAssetMetadata(assetId, <someMetadata>)
#   }
# }

# 2. I launch my local script on the asset, here the --use-local is the key 
ftbx launch jobs "ftbx-script-dnaisse-wb-dev" --params "assetId=809" --use-local

# 3. I now want to do something else on asset 1320, I update my local action again

# wb-dev/actions/ftbx-script-dnaisse-wb-dev/script.groovy:

# import com.ooyala.flex.plugins.PluginCommand
# 
# class Script extends PluginCommand {
#   def execute() {
#     <do something else>
#   }
# }

# 4. I launch my local script again, on a different asset
ftbx launch jobs "ftbx-script-dnaisse-wb-dev" --params "assetId=1320" --use-local
```

#### 2.2. Run a script on an asset and retry it until you get it right

```shell
# Example: I want to set some metadata on asset id 809  
# 1. I update the code of my local ftbx-script-dnaisse-wb-dev to do what I want

# wb-dev/actions/ftbx-script-dnaisse-wb-dev/script.groovy:

# import com.ooyala.flex.plugins.PluginCommand
# 
# class Script extends PluginCommand {
#   def execute() {
#     assetId = context.asset.id
#     flexSdkClient.assetService.setAssetMetadata(assetId, <someMetadata>)
#     assert <myMetadataUpdateWorkedCorrectly>
#   }
# }

# 2. I launch my local script on the asset
ftbx launch jobs "ftbx-script-dnaisse-wb-dev" --params "assetId=809" --use-local
# However, let's say my script fails because my code is incorrect

# 3. Then, I update and push the code until it succeeds
ftbx push jobs 308 --retry --listen # fails too, I update and push the code again 
ftbx push jobs 308 --retry --listen # fails too, I update and push the code again 
ftbx push jobs 308 --retry --listen # finally works!

# 4. I can now copy the script to a new action since I know my code works
```

# Workflow Designer

```shell
ftbx workflowDesigner <workflow_name> <options>
```

> options:  
> --in [String]: environment alias if not default  

This command launches the workflow designer for the corresponding workflow in a new browser window.

---

### 1. Open workflow designer

```shell
# open workflow designer in default environment
ftbx workflowDesigner "Get or compute asset checksum"

# open workflow designer in wb-stg environment
ftbx workflowDesigner "Get or compute asset checksum" --in "wb-stg"
```

# Metadata Designer

```shell
ftbx metadataDesigner <options>
```

> options:  
> --in [String]: environment alias if not default  

This command launches the metadata designer in a new browser window.

---

### 1. Open metadata designer

```shell
# open metadata designer in default environment
ftbx metadataDesigner

# open metadata designer in wb-stg environment
ftbx workflowDesigner --in "wb-stg"
```

# ERRORS & FIXES

### Self-signed certificates
```shell
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1006)
```
Fix: see [4. Connect to self-signed environments](#4-connect-to-self-signed-environments)

---

# CONTACTS

David NAISSE - [dnaisse@dalet.com](dnaisse@dalet.com)
