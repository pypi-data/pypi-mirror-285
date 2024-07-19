## Get Or Compute Asset Checksum

> Description:  
> 1. Check if the context asset on s3 has a sha1 tag  
> 2. if TRUE, set this tag value to asset metadata  
> 3. if FALSE, send asset to FFP for checksum compute, then set new tag from filesHashInfo wfvar (output of compute-asset-sha1)  

![](graph.png)

- type: workflowDefinitions
- runtime permissions [bitbucket pull request](https://bitbucket.org/ooyalaflex/wb-stg/pull-requests/69)
- dependencies:
  - actions:
    - `check-asset-sha1-s3-tag-exists`:
      - vars to edit:
        - AWS_KEY
        - AWS_SECRET
        - AWS_TAGS
    - `compute-asset-sha1`
    - `set-asset-sha1-from-asset-tag`:
      - vars to edit:
        - AWS_KEY
        - AWS_SECRET
        - AWS_TAGS
    - `set-asset-sha1-from-filesHashInfo`
  - resources:
    - `FFP`:
      - vars to edit:
        - datacenter