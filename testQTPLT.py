import sys
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
    
    all_nodes=['1-1','1-2','1-3','2-1','2-2','2-3','3-1','3-2','3-3','device-1','device-2','device-3','device-4','device-5']
    all_nodeslabel=['1-1','1-2','1-3','2-1','2-2','2-3','3-1','3-2','3-3','d-1','d-2','d-3','d-4','d-5']
    all_coordinates = [[1, 3], [3, 3], [5, 3], [1, 5], [3, 5], [5, 5], [1, 7], [3, 7],[5, 7],[1, 1], [2, 1], [3, 1],[4, 1], [5, 1]]
    all_npos = dict(zip(all_nodes, all_coordinates))  # 节点与坐标之间的映射关系
    all_nlabels = dict(zip(all_nodes, all_nodeslabel))  # 节点与标签之间的映射关系

    full_nodes=['1-1','1-2','1-3','2-1','2-2','2-3','3-1','3-2','3-3','device-1','device-2','device-3','device-4','device-5']
    full_edges=[
        ['1-1','1-2'],
        ['1-2','1-3'],
        ['1-1','2-1'],
        ['2-1','2-2'],
        ['2-2','2-3'],
        ['2-1','3-1'],
        ['3-1','3-2'],
        ['3-2','3-3'],
        ['device-1','1-1'],
        ['device-1','device-2'],
        ['device-2','device-3'],
        ['device-3','device-4'],
        ['device-4','device-5']
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
        layout.addWidget( self.canvas )
        self.setLayout(layout)
        # 数组初始化
        self.x=[]

    def showTime(self):
        self.figure.clear()
        nodes = self.full_nodes[0:self.iter_edges+1]
        edges = self.full_edges[0:self.iter_edges]
        G=nx.Graph()
        node_color = []
        npos = dict.fromkeys(nodes, '')
        nlabels = dict.fromkeys(nodes, '')
        for ele in npos:
            npos[ele] = self.all_npos[ele]
            nlabels[ele] = self.all_nlabels[ele]
            if ele[0] == 'd':
                node_color.append("#66FF66")
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