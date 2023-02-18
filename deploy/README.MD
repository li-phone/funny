DEPLOY
===========
> An automatic deployment tool for deploying your applications on the remote hosts.

Install
-------
Just run `build.sh` script that OK.

```
> sh build.sh
```

Make a link to the deployment program and add to the environment path.

On Windows:

```
mklink deploy deploy-x.x.x-win_x64.exe
```

On Linux:

```
link -s deploy-x.x.x-Linux deploy
```

Usage
-----

* **Allow accessing to the remote hosts by your identity file (SSH private key)**.
* **Only yourself own the SSH private key**.
    * On Linux:
        ```
        > chmod 700 ~/.ssh/id_rsa
        ```
    * On Windows:
      > Delete the SYSTEM and the Administrators roles and only keep yourself.
* Use ```deploy -h``` to call for the help.

```
usage: deploy [-h] [--env ENV] [--module MODULE] [--cfg CFG]
                                [--run] [--demo] [--version]

optional arguments:
  -h, --help            show this help message and exit
  --env ENV, -e ENV     environment name, e.g. 'KF'
  --module MODULE, -m MODULE
                        module name, e.g. 'app'
  --cfg CFG, -c CFG     config file
  --run, -r             whether run or not
  --demo, -d            generate demo config file
  --version, -v         show deploy version
```

* Generate the demo config file.

```
> deploy -d or deply --demo
```

* Modify the configurations as required.

```
{
  "ENV": {
    "KF": "host1,host2,host3" //delete me: 环境名称的全部连接地址，逗号分隔
  },
  "DEFAULT_ENV": "KF", //delete me: 默认环境名称
  "IDENTITY_FILE": "", //delete me: 私钥文件，默认为~/.ssh/id_rsa
  "APP": [
    {
      "user": "user", //delete me: 用户名
      "host": "host1,host2", //delete me: 连接地址，逗号分隔
      "name": "app name", //delete me: 应用名称
      "local_root": "~/app/local_root", //delete me: 本地根目录
      "remote_root": "~/app/remote_root", //delete me: 远端根目录
      "start": "cd ~/app/remote_root/ && nohup sh start.sh &", //delete me: 应用启动命令，如需每次都查看一遍，请去掉nohup和&
      "replace": [
        {
          "source": "config/app.cfg", // delete me: 源文件路径
          "destination": "config/" // delete me: 目的路径，为目录时需与源文件路径保持一致的"/"符号，此处有"/"
        },
        {
          "source": "lib", // delete me: 源文件路径
          "destination": "lib" // delete me: 目的路径，为目录时需与源文件路径保持一致的"/"符号，此处无"/"
        },
        {
          "source": "app.jar", // delete me: 源文件路径
          "destination": "app.jar" // delete me: 目的路径
        }
      ]
    }
  ]
}
```

* Use the follow commands to deploying your applications

```
# The default configurations:
# -e default 'DEFAULT_ENV'
# -m default all applications
# -c default 'deploy-config.json'
> deploy -e [your environment] -m [your applications] -c [your config file] [-r]
```

* Automatically generate deployment script for additional supplement.

```
> sh deploy-auto.sh
```

Release logs
------------

#### V1.0.0 at 2022/08/28

* With the additional deployment script.
* With the help for running and configuration.
* Support prefix abbreviations for the module parameter.

#### V2.0.0 at 2023/02/18

* Not distinguish application type.
