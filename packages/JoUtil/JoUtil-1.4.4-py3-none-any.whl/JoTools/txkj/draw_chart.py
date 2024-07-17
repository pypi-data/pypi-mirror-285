# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import random
import numpy as np
import matplotlib.pyplot as plt

def draw_pr_chart(chart_path, save_path="", show=False):

    plt.style.use("ggplot")
    plt.figure()
    plt.title('Precision-Recall Curve')

    with open(chart_path, "r") as chart_file:
        line = chart_file.readline()
        while(line):

            random_color = [random.random(), random.random(), random.random()]
            model_name = line.strip()

            line_p = chart_file.readline()
            p = line_p.strip().split(",")[1:]
            p = [float(x) for x in p]

            line_r = chart_file.readline()
            r = line_r.strip().split(",")[1:]
            r = [float(x) for x in r]

            plt.plot(r, p, color=random_color, marker='o', label=str(model_name))
            plt.legend(loc=0, ncol=2)

            line = chart_file.readline()


    if(save_path):
        plt.savefig(plt_pic_name)

    if show:
        plt.show()



if __name__ == "__main__":

    draw_pr_chart(r"C:\Users\14271\Desktop\chart.txt", "", True)