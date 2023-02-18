import glob
import os.path
import os.path as osp
import subprocess

__VERSION__ = '2.0.0'

ENV, DEFAULT_ENV, APP, IDENTITY_FILE = None, None, None, None
ENV_STR = 'source /etc/profile; source ~/.profile; source ~/.bashrc;'


def dec_cmd(cmd):
    if not IDENTITY_FILE:
        return f'{cmd} '
    return f'{cmd} -i "{IDENTITY_FILE}" '


def glob_path(root, path):
    targets = glob.glob(path, recursive=True)
    if not targets:
        targets = glob.glob(osp.join(root, path), recursive=True)
    if targets:
        return targets
    return None


def prepare_environment(user, host):
    def run(cmd):
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        r = p.stdout.read().decode('utf-8')
        if r is not None:
            r = r.rstrip()
        return r

    kill2 = 'kill2'
    kill2_cmd = r'''
# kill process by process name
kill2() {
    echo \"[INFO] kill before:\"&&ps -ef|grep \$1&&echo&&ps -ef|grep \$1|awk '{print \$2}'|xargs kill -9 2> /dev/null||echo \"[INFO] kill after:\"||ps -ef|grep \$1;
}
    '''
    prefix = dec_cmd('ssh') + f'{user}@{host} '
    ret = run(f'{prefix} "command -v {kill2}"')
    if ret != kill2:
        ret = run(f'{prefix} "echo \\"{kill2_cmd}\\" >> ~/.bashrc"')
        ret = run(f'{prefix} "{ENV_STR}"')


def build_deploy(user, host, app):
    """
    Core Steps:
        1. kill remote running process (Only Debug, Not Production)
        2. replace remote files or folders (Not Distinguish Application Category)
        3. restart remote process
    """

    pid = osp.basename(app['name'])
    command = [dec_cmd('ssh') + f'{user}@{host} "kill2 {pid}"']

    for replace in app['replace']:
        if 'source' not in replace or 'destination' not in replace:
            continue
        src_paths = glob_path(app['local_root'], replace['source'])
        if not src_paths:
            continue
        for src in src_paths:
            src = src.replace('\\', '/')
            head_path = os.path.join(app['local_root'], replace['destination'])
            tail_path = src[len(head_path):]
            if tail_path:
                dst = osp.join(app['remote_root'], replace['destination'], tail_path).replace('\\', '/')
            else:
                dst = osp.join(app['remote_root'], replace['destination']).replace('\\', '/')
            command.append(dec_cmd('ssh') + f'{user}@{host} "rm -r {dst}"')
            if osp.isdir(src):
                command.append(dec_cmd('ssh') + f'{user}@{host} "mkdir -p {dst}"')
                dst = osp.dirname(dst)
            else:
                dst = osp.dirname(dst)
                command.append(dec_cmd('ssh') + f'{user}@{host} "mkdir -p {dst}"')
            command.append(dec_cmd('scp') + f'-r {src} {user}@{host}:{dst}')

    cmd = f"{ENV_STR} {app['start']}"
    command.append(dec_cmd('ssh') + f'{user}@{host} "{cmd}"')

    return command


def run_deploy(command, app):
    for cmd in command:
        # os.system(cmd)
        # p = os.popen(cmd)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # if app['start'] in cmd:
        #     time.sleep(1)
        print(cmd)
        if not (app['start'] in cmd):
            ret = p.stdout.read().decode('utf-8')
        #     print(ret)


def deploy(env=None, module=None, run=None):
    commands = []
    env = ENV[env] if env in ENV else env
    for app in APP:
        if module and str(module).strip() and module not in app['name']:
            continue
        user, hosts = app['user'], app['host'].strip().split(',')
        for host in hosts:
            if host not in env:
                continue
            prepare_environment(user, host)
            command = build_deploy(user, host, app)
            commands.extend(command)
            if run:
                run_deploy(command, app)
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
    parser.add_argument("--cfg", "-c", default="deploy-config-2.json", help="config file")
    parser.add_argument("--run", "-r", action="store_true", help="whether run or not")
    parser.add_argument("--demo", "-d", action="store_true", help="generate demo config file")
    parser.add_argument("--version", "-v", action="store_true", help="show deploy version")
    args = parser.parse_args()

    if args.version:
        print(f'deploy version: {__VERSION__}')
        return

    if args.demo:
        generate_demo()
        print('[*] ' + '-' * 16 + ' generate demo OK!')
        return

    cfg = read_cfg(args.cfg)
    global ENV, DEFAULT_ENV, APP, IDENTITY_FILE
    ENV, DEFAULT_ENV, APP = cfg['ENV'], cfg['DEFAULT_ENV'], cfg['APP']
    IDENTITY_FILE = IDENTITY_FILE if 'IDENTITY_FILE' not in cfg else cfg['IDENTITY_FILE']
    args.env = args.env if args.env else DEFAULT_ENV
    deploy(args.env, args.module, args.run)
    print('[*] ' + '-' * 16 + ' process OK!')


if __name__ == '__main__':
    main()
