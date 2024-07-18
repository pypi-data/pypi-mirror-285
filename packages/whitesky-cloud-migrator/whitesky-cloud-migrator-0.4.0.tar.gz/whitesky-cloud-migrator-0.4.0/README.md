# wscm

## usage

```
wscm --help
Usage: wscm [OPTIONS]

Options:
  --ws-portal TEXT             Url to the cloud portal, E.g.
                               https://portal.whitesky.cloud  [required]
  --target-ws-portal TEXT      Url to the target cloud portal, E.g.
                               https://portal.whitesky.cloud. When omitted,
                               the target portal is the same as the source
  --migrate-portal TEXT        Url to the cloud portal, E.g.
                               https://migrate.whitesky.cloud  [required]
  --customer-id TEXT           whitesky customer ID  [required]
  --target_customer-id TEXT    Target whitesky customer ID. When omitted, the
                               target_customer is the same as the source
  --source-cloudspace TEXT     ID of the source cloudspace  [required]
  --target-cloudspace TEXT     ID of the target cloudspace  [required]
  --source-vm-id INTEGER       ID of the virtual machine to create units and
                               targets for. Add this option for every virtual
                               machine you want to migrate or ommit the option
                               to create migration options for all the VMs in
                               the source cloudspace.
  --jwt TEXT                   JWT authentication token  [required]
  --target_jwt TEXT            JWT authentication token. When omitted, the
                               target_jwt is the same as the source
  --migrate-login TEXT         Login on the migration portal  [required]
  --migrate-passwd TEXT        Password for the migration portal  [required]
  --vault TEXT                 ID of the Vault to use for the units. Should be
                               SSH-KEY based
  --vault-pub-key TEXT         Pub ssh key corresponding to the vault used.
  --ignore-target-subnet       Set this flag when the target subnet is
                               different from the source
  --skip-target-storage-match  When matching for target VMs in the target
                               cloudspace, skip the match on storage
  --help                       Show this message and exit.
  ```

  ## installation

  ```
  pip install wscm
  ```