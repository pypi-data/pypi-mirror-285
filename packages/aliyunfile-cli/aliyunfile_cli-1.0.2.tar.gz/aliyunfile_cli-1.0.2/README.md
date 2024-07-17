# aliyunfile-cli(alyf)

Usage:

```
alyf upload [-h] --file_path FILE_PATH --folder_id FOLDER_ID --group_id GROUP_ID --account_id ACCOUNT_ID --token TOKEN

options:
  -h, --help            show this help message and exit
  --file_path FILE_PATH
                        Path of local file to upload
  --folder_id FOLDER_ID
                        Target folder id, find after group from the url in browser address bar
  --group_id GROUP_ID   Target group id, find after group id from the url in browser address bar, or can be root
  --account_id ACCOUNT_ID
                        Account id, find sub domain from the aliyunfile url
  --token TOKEN         Token to access aliyunfile, find access token from token in the local storage
```