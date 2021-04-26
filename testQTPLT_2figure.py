import sys
import time
import matplotlib
import networkx as nx
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
# 使用 matplotlib中的FigureCanvas (在使用 Qt5 Backends中 FigureCanvas继承自QtWidgets.QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon

class App(QWidget):
    
    all_nodes = ['room_1','room_2','room_3','room_4','room_5','room_6','room_7','room_8','pump_1','pump_2','heatpump_1','communication_node']
    all_nodeslabel=['r-1','r-2','r-3','r-4','r-5','r-6','r-7','r-8','p-1','p-2','hp','com']
    all_coordinates = [[9, 2], [7, 2], [5, 2], [9, 3], [7, 3], [5, 3], [3, 3], [1, 3], [3, 2],[1, 2], [2, 1.6], [2, 3.4]]
    all_npos = dict(zip(all_nodes, all_coordinates))  # 节点与坐标之间的映射关系
    all_nlabels = dict(zip(all_nodes, all_nodeslabel))  # 节点与标签之间的映射关系

    full_nodes = all_nodes
    full_edges=[
        ['room_1','room_2'],
        ['room_1','room_4'],
        ['room_2','room_3'],
        ['room_2','room_5'],
        ['room_3','room_6'],
        ['room_3','pump_1'],
        ['room_4','room_5'],
        ['room_5','room_6'],
        ['room_6','room_7'],
        ['room_7','room_8'],
        ['room_7','pump_1'],
        ['room_7','communication_node'],
        ['room_8','pump_2'],
        ['room_8','communication_node'],
        ['pump_1','pump_2'],
        ['pump_1','heatpump_1'],
        ['pump_2','heatpump_1']
    ]
    iter_edges = 1
    def __init__(self, parent=None):
        # 父类初始化方法
        super(App, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('动态演示')
        self.setFixedSize(1200, 700)
        self.setMinimumSize(1200, 700)
        self.setMaximumSize(1200, 700)
        # 几个QWidgets
  
        self.startBtn = QPushButton('开始')
        self.endBtn = QPushButton('结束')
        self.startBtn.clicked.connect(self.startTimer)
        self.endBtn.clicked.connect(self.endTimer)
        # 时间模块
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        #图像模块
        self.figure = plt.figure("node")
        self.canvas = FigureCanvas(self.figure)

        #垂直布局

        layout=QVBoxLayout()
        layout.addWidget(self.startBtn)
        layout.addWidget(self.endBtn)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        # 数组初始化
        self.x=[]

    def showTime(self):
        # figure1
        self.figure.clear()
        self.ax1 = self.figure.add_subplot(121)
        self.ax1.set_title("当前节点图")
        exist_nodes = self.full_nodes
        node_color = []
        npos = dict.fromkeys(exist_nodes, '')
        nlabels = dict.fromkeys(exist_nodes, '')
        for ele in npos:
            npos[ele] = self.all_npos[ele]
            nlabels[ele] = self.all_nlabels[ele]
            if ele[0] == 'p' or ele[0] == 'h':
                node_color.append("#66FF66")
            elif ele[0] == 'c':
                node_color.append("#FF0000")
            else:
                node_color.append("#6CB6FF")
        G=nx.Graph()
        G.add_nodes_from(exist_nodes) 
        nx.draw_networkx_nodes(G, npos, node_size=400, node_color=node_color)  # 绘制节点
        nx.draw_networkx_labels(G, npos, nlabels)  # 标签

        # figure2
        self.ax2 = self.figure.add_subplot(122)
        self.ax2.set_title("当前拓扑图")
        nodes = self.full_nodes
        edges = self.full_edges
        G=nx.Graph()
        node_color = []
        npos = dict.fromkeys(nodes, '')
        nlabels = dict.fromkeys(nodes, '')
        for ele in npos:
            npos[ele] = self.all_npos[ele]
            nlabels[ele] = self.all_nlabels[ele]
            if ele[0] == 'p' or ele[0] == 'h':
                node_color.append("#66FF66")
            elif ele[0] == 'c':
                node_color.append("#FF0000")
            else:
                node_color.append("#6CB6FF")
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.draw_networkx_nodes(G, npos, node_size=400, node_color=node_color)  # 绘制节点
        nx.draw_networkx_edges(G, npos, edges)  # 绘制边
        nx.draw_networkx_labels(G, npos, nlabels)  # 标签

        self.canvas.draw()
        self.iter_edges = self.iter_edges + 1
    # 启动函数
    def startTimer(self):
        # 设置计时间隔并启动
        self.timer.start(1000)#每隔一秒执行一次绘图函数 showTime
        self.startBtn.setEnabled(False)#开始按钮变为禁用
        self.endBtn.setEnabled(True)#结束按钮变为可用

    def endTimer(self):
        self.timer.stop()#计时停止
        self.startBtn.setEnabled(True)#开始按钮变为可用
        self.endBtn.setEnabled(False)#结束按钮变为可用
        self.iter_edges = 1

# 运行程序
if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    main_window = App()
    main_window.show()
    app.exec()