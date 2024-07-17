# theca-sdk-python



### Usage 1: Set environment variables
```bash
export DEVNULL_EMAIL="_your_registered_email"
export DEVNULL_ACCESS_KEY="_your_access_key_"
export DEVNULL_SECRET_KEY="_your_access_key_"

python3 -c 'from theca import create_cert; create_cert()'
ls -lt  $HOME/.devnull/certs/
```

### Usage 2: Serve a credential file
```bash
cat ~/.devnull/credentials
[default]
email = ca-by-devnull@outlook.com
accesskey = _your_access_key_
secretkey = _your_secret_key_

python3 -c 'from theca import create_cert; create_cert()'
ls -lt  $HOME/.devnull/certs/
```

## Trust your private CA -- todo
```bash
theca_add_ca --orgid 0c74e79c1014
theca_add_ca --email ca-by-devnull@outlook.com
```



