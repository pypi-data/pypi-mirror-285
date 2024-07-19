# BUG/FEATURE HUNT

Welcome to the Hunt! Found bugs or suggested features are shown below.

(checkmarks indicate whether the bug/feature is fixed/implemented or not)

- 2024-06:
  - [x] **Gustavo BONASSO** (BUG) - `ftbx push` not working for old groovy scripted-wait actions
  - [x] **Bowen ZHANG** (BUG) - `ftbx push --with-dependencies` not working for workflows with wait-for-signal actions
- 2024-05:
  - [x] **Sergey MOROZOV** (BUG) - `ftbx init` to work with uppercase folder names
  - [x] **Sergey MOROZOV** (BUG) - incorrect readme documentation for MacOS/Linux (python3 instead of python)
  - [] **Julius SANTUA** (FEATURE) - `ftbx list` to support user defined objects
- 2024-04:
  - [x] **Gustavo BONASSO** (PR) - `ftbx connect` to hide password
  - [x] **Elouan GOUINGUENET** (PR) - Failures from Flex API displaying flex.request.id for newer Flex versions.
- 2024-03:  
  - [x] **Gustavo BONASSO** (BUG) - `ftbx init` not working as expected for first installation because of env var dependency in new feature
  - [x] **Hugo TALBOT** (PR) - Installation instructions for macOS  
  - [x] **Guillaume GAY** (BUG) - `ftbx push` with `--with-dependencies` failing to update workflow summary when pushing for the second time, as workflow is enabled  
  - [x] **Guillaume GAY** (FEATURE) - `ftbx push` to have a `--ignore-resources` flag to allow to push dependencies from env to env without touching the resources  
  - [x] **Rémi MARCHAND** (BUG) - `ftbx list/pull` with FQL returning the same objects multiple times  
  - [x] **Elouan GOUINGUENET** (FEATURE) - `ftbx launch` to automatically pull the corresponding launched item  
  - [ ] **Elouan GOUINGUENET** (FEATURE) - `ftbx clear` command to automatically wipe local folders of instances (jobs, workflows..)  
  - [ ] **Elouan GOUINGUENET** (FEATURE) - `ftbx push` to work with jobs of timed actions  
- 2024-02:  
  - [x] **Elouan GOUINGUENET** (FEATURE) - `ftbx push` to have a `--retry` flag to allow for **optional** retry when pushing jobs  
  - [x] **Elouan GOUINGUENET** (FEATURE) - `ftbx query` to log JSON result in the terminal  
  - [x] **Guillaume GAY** (FEATURE) - `ftbx compare` to work with nested items (ex: metadata definitions)  
- 2024-01:  
  - [ ] **Elouan GOUINGUENET** (BUG) - `ftbx push` not working as expected when initial pull was done before a script was created for a given action  
