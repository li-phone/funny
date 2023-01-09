import glob
import os.path
import os.path as osp
import subprocess

ENV, DEFAULT_ENV, APP_CONFIG, APP, IDENTITY_FILE = None, None, None, None, None


class AppConfig(object):
    JAR = 'jar'
    WAR = 'war'
    ENV_STR = 'source /etc/profile; source ~/.profile; source ~/.bashrc;'

    @staticmethod
    def get_type(path):
        def is_type(t):
            for s in t:
                p = glob.glob(osp.join(path, s))
                if len(p) == 0:
                    return False
            return True

        for k, v in APP_CONFIG.items():
            if is_type(v):
                return k, v
        return None


def dec_cmd(cmd):
    if not IDENTITY_FILE:
        return f'{cmd} '
    return f'{cmd} -i "{IDENTITY_FILE}" '


def check_params(module, app):
    if module and str(module).strip() and module not in app['name']:
        return None
    target_path = app['target'] if 'target' in app and app['target'] else f"**/{app['name']}/target"
    targets = glob.glob(target_path, recursive=True)
    if not targets:
        return None
    target = targets[0]
    app_type, app_def = AppConfig.get_type(target)
    if not app_type:
        return None
    return dict(target=target, app_type=app_type, app_def=app_def)


def prepare_environment(user, host):
    def run(cmd):
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        r = p.stdout.read().decode('utf-8')
        if r is not None:
            r = r.rstrip()
        return r

    kill2 = 'kill2'
    kill2_cmd = r'''
# 0x0001  根据名称杀死进程
kill2() {
    echo \"[INFO] kill before:\"&&ps -ef|grep \$1&&echo&&ps -ef|grep \$1|awk '{print \$2}'|xargs kill -9 2> /dev/null||echo \"[INFO] kill after:\"||ps -ef|grep \$1;
}
    '''
    prefix = dec_cmd('ssh') + f'{user}@{host} '
    ret = run(f'{prefix} "command -v {kill2}"')
    if ret != kill2:
        ret = run(f'{prefix} "echo \\"{kill2_cmd}\\" >> ~/.bashrc"')
        ret = run(f'{prefix} "{AppConfig.ENV_STR}"')


def build_deploy(user, host, app, app_params):
    """
        1. 杀死服务
        2. 删除文件
        3. 上传文件
        4. 重启服务
    """
    target, app_type, app_def = app_params['target'], app_params['app_type'], app_params['app_def']
    pid = osp.basename(app['root']) + '.jar' if app_type == AppConfig.JAR else osp.basename(app['root'])
    command = [dec_cmd('ssh') + f'{user}@{host} "kill2 {pid}"']
    for path in app_def:
        p = glob.glob(osp.join(target, path))
        if not p:
            continue
        full_path = p[0].replace(osp.join(target, ''), '')
        src = osp.join(target, full_path).replace('\\', '/')
        if app_type == AppConfig.WAR:
            full_path = path.replace('*/', '')
        dst = osp.join(app['dst'], full_path).replace('\\', '/')
        command.append(dec_cmd('ssh') + f'{user}@{host} "rm -r {dst}"')
        if osp.isdir(src):
            command.append(dec_cmd('ssh') + f'{user}@{host} "mkdir -p {dst}"')
            dst = osp.dirname(dst)
        command.append(dec_cmd('scp') + f'-r {src} {user}@{host}:{dst}')
    cmd = f"{AppConfig.ENV_STR} {app['start']}"
    command.append(dec_cmd('ssh') + f'{user}@{host} "{cmd}"')
    return command


def run_deploy(command, app, app_params):
    for cmd in command:
        # os.system(cmd)
        # p = os.popen(cmd)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # if app['start'] in cmd:
        #     time.sleep(1)
        print(cmd)
        if not (app['start'] in cmd and app_params['app_type'] in (AppConfig.WAR,)):
            ret = p.stdout.read().decode('utf-8')
        #     print(ret)


def deploy(env=None, module=None, run=None):
    commands = []
    env = ENV[env] if env in ENV else env
    for app in APP:
        app_params = check_params(module, app)
        if not app_params:
            continue
        user, hosts = app['user'], app['host'].strip().split(',')
        for host in hosts:
            if host not in env:
                continue
            prepare_environment(user, host)
            command = build_deploy(user, host, app, app_params)
            commands.extend(command)
            if run:
                run_deploy(command, app, app_params)
    with open(f'{osp.basename(__file__)[:-3]}-auto.sh', 'w') as fp:
        fp.writelines('\n'.join(commands))


def read_cfg(file_path):
    import json
    with open(file_path) as fp:
        return json.load(fp)


def generate_demo():
    demo = '''{
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
    '''
    if os.path.exists('deploy-demo.json'):
        return
    with open('deploy-demo.json', 'w') as fp:
        fp.write(demo)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", "-e", help="environment name, e.g. 'KF'")
    parser.add_argument("--module", "-m", help="module name, e.g. 'app'")
    parser.add_argument("--cfg", "-c", default="deploy-config.json", help="config file")
    parser.add_argument("--run", "-r", action="store_true", help="whether run or not")
    parser.add_argument("--demo", "-d", action="store_true", help="generate demo config file")
    args = parser.parse_args()

    if args.demo:
        generate_demo()
        print('[*] ' + '.' * 16 + ' generate demo OK!')
        return
    cfg = read_cfg(args.cfg)
    global ENV, DEFAULT_ENV, APP_CONFIG, APP, IDENTITY_FILE
    ENV, DEFAULT_ENV, APP_CONFIG, APP = cfg['ENV'], cfg['DEFAULT_ENV'], cfg['APP_CONFIG'], cfg['APP']
    IDENTITY_FILE = IDENTITY_FILE if 'IDENTITY_FILE' not in cfg else cfg['IDENTITY_FILE']
    args.env = args.env if args.env else DEFAULT_ENV
    deploy(args.env, args.module, args.run)
    print('[*] ' + '.' * 16 + ' process OK!')


if __name__ == '__main__':
    main()
