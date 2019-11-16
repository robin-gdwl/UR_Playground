## [SVG 简介](http://www.w3school.com.cn/svg/svg_intro.asp)
在 Sketch（草图）研究中，我们经常会遇到 SVG 格式的图像文件。和 PNG 不同，SVG是一种矢量图，它可以保存草图绘图过程中每个笔画的坐标信息。所以，理解 SVG 对于研究草图是很有意义的。

PNG 实际上是像素点，是一个矩阵，比如 RGB 三通道的 224 * 224 像素的一张 PNG 图片，就是一个 224 * 224 * 3 的实数矩阵。但是 **SVG 则是一门编程语言，是使用 XML 来描述二维图形和绘图程序的语言**。也就是说，SVG文件实际上就是一些 XML 代码，所以我们要理解 svg ，就是要理解这些 XML 代码。

SVG 中包含了矩形，圆形，路径等多种组成元素，分别对应 <rect> <circle> <path> 等标签，每个标签都有自己的一些属性，比如 <circle> 中 cx 和 cy 属性定义圆点的 x 和 y 坐，r 属性定义圆的半径。但是对于 Sketch，我们并主要理解 <path> 就够了，因为草图的笔画都是通过 <path> 来存储的。path 元素的形状通过属性 d 来定义，属性 d 的值是一个 “命令+参数” 的序列。下面将介绍 [<path d=""> 的一些命令](https://segmentfault.com/a/1190000005053782)：

### 直线命令
- M = moveto
【Move to】需要两个参数，分别是需要移动到的点的x轴和y轴的坐标。类似于移动画笔的位置。一般 M 会表示一个笔画的开始。
```
M x y //绝对位置
m dx dy //相对位置。后续提到其他命令雷同，故省略不再赘述。
```
- L = lineto
【Line to】需要两个参数，分别是一个点的x轴和y轴坐标，L命令将会在当前位置和新位置（L前面画笔所在的点）之间画一条线段。

- H = horizontal lineto
H 【绘制平行线】

- V = vertical lineto
V【绘制垂直线】
这两个命令都只带一个参数，标明在x轴或y轴移动到的位置，因为它们都只在坐标轴的一个方向上移动

- Z = closepath
Z 【闭合路径】
Z命令会从当前点画一条直线到路径的起点。不区分大小写

### 曲线命令
- C = curveto
三次贝塞尔曲线。(x,y)表示的是曲线的终点，(x1,y1)是起点的控制点，(x2,y2)是终点的控制点。
控制点描述的是曲线起始点的斜率，曲线上各个点的斜率，是从起点斜率到终点斜率的渐变过程。 
```
C x1 y1, x2 y2, x y
```

下面还有一些其他命令就不再贴解释了，有兴趣的可以在 [svg之<path>详解](ttps://segmentfault.com/a/1190000005053782) 中去了解。
- S = smooth curveto
- Q = quadratic Belzier curve
- T = smooth quadratic Belzier curveto
- A = elliptical Arc

在 Sketch 中，一般只有 M 和 C 两种命令。所以只需要理解这两种命令应该就够了。

pip install svgwrite
pip install svgpathtools


