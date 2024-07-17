# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import subprocess




class ExternalCommandUtil(object):

    @staticmethod
    def test(command):
        return_list = []
        res = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        for line in res.stdout.readlines():
            return_list.append(line.strip().decode('utf-8'))
        return return_list



if __name__ == "__main__":


    # command = "nvidia-smi --query-gpu=uuid --format=csv"
    command = "echo hhe"

    a = ExternalCommandUtil.test(command)
    print(a)

