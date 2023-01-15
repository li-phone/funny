Deploy
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

On the other platform:
```
link -s deploy-x.x.x-Linux deploy
```

Usage
-----
* Use ```deploy -h``` to call for the help.

```
usage: deploy [-h] [--env ENV] [--module MODULE] [--cfg CFG]
                                [--run] [--demo]

optional arguments:
  -h, --help            show this help message and exit
  --env ENV, -e ENV     environment name, e.g. 'KF'
  --module MODULE, -m MODULE
                        module name, e.g. 'app'
  --cfg CFG, -c CFG     config file
  --run, -r             whether run or not
  --demo, -d            generate demo config file
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
  "APP_CONFIG": {
    "jar": [ //delete me: jar应用需要替换的文件和文件夹路径
      "lib",
      "*.jar"
    ],
    "war": [ //delete me: war应用需要替换的文件和文件夹路径
      "WEB-INF/lib",
      "WEB-INF/classes/com"
    ]
  },
  "APP": [
    {
      "user": "user", //delete me: 用户名
      "host": "host1,host2", //delete me: 连接地址，逗号分隔
      "name": "app name", //delete me: 应用名称
      "root": "~/app/app_root", //delete me: 远程应用的根目录
      "start": "cd ~/app/app_root/ && nohup sh start.sh &", //delete me: 应用启动命令，如需每次都查看一遍，请去掉nohup和&
      "dst": "~/app/app_root", //delete me: 远程应用的运行目录
      "target": "app/app_root/target" //delete me: 本地编译的目标目录
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
