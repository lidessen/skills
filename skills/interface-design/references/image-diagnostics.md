# 元素色块抽象

用真实几何削弱内容语义，观察布局、留白、大小与疏密。主要输出是在干净画布上重建的元素色块，不是截图描边、模糊或减色。先看原图提出疑问，再看抽象图，最后回到真实界面核对；不输出自动审美分数。

## 采集实际边界

`scripts/collect_regions.js` 提供只读浏览器函数 `collectRegions()`。通过当前环境支持的浏览器 evaluate API 执行函数并保存返回 JSON；它不改变 DOM、样式或交互状态，也不导出文字内容。使用浏览器工具允许的执行方式，不以脚本绕过工具权限。

- 普通文字使用每段文字的实际 Range 行框，保留宽高，不改成固定长度的占位条。
- 按钮、输入框、选择器等控件作为完整色块，内部文字不重复绘制。
- 图片、SVG、视频、canvas 和 iframe 作为媒体块；不猜测其内部结构。
- 不透明背景作为色面，保留颜色；隐藏元素排除，普通 overflow 裁切按可见边界处理。
- 输出只包含当前 viewport。坐标及 `image_size` 单位为 CSS px，生成图采用一 CSS px 对应一图像像素。

先打开目标页面并等待字体、内容稳定，再连续采集 JSON 和原始截图。嵌入式预览最好打开独立画布页面，避免混入工具栏或搞错 iframe 坐标。对比原图时将截图缩放到同一 CSS 视口大小；不要直接把高倍率截图坐标当作 CSS px。

采集器不重建伪元素、复杂裁切、遮挡层级、Shadow DOM 内部或旋转轮廓，返回 `warnings` 说明部分限制。遇到这些对象，先核对可见区域再修正 JSON，不把采集缺失当作设计问题。`aria-hidden` 装饰内容被省略。控件完整替换意味着文字视图不包含控件标签。

## 生成分类视图

脚本依赖 Python 3 和 Pillow。缺失依赖时创建独立环境，无需修改被评项目：

```sh
python3 -m venv /tmp/interface-design-env
/tmp/interface-design-env/bin/python -m pip install Pillow
/tmp/interface-design-env/bin/python scripts/render_blocks.py regions.json /tmp/ui-blocks
```

路径相对本 skill。输出目录必须不存在；脚本不读取、修改或覆盖原图。

| 输出         | 观察内容                         |
| ------------ | -------------------------------- |
| overview.png | 色面、控件、媒体和文字的整体构成 |
| text.png     | 普通文字行的宽度、对齐和阅读节奏 |
| controls.png | 控件大小、位置和分布             |
| surfaces.png | 容器背景和媒体占位的空间分配     |

控件、文字、媒体使用各自固定的中性色，容器保留采集到的背景色。颜色是分类辅助，不代表重要性；不能据此判断原界面的真实明暗、对比度或注意力。所有块保留原位置和矩形尺寸；圆角、阴影、图标细节被有意省略。图层按色面、控件/媒体、文字排列，因此不是浏览器渲染器的完整替代。

## 只有截图时

先人工识别并核对区域，再用同一格式生成抽象图；不宣称自动识别。`box` 是 x、y、width、height。按截图像素标注时，`image_size` 应为该截图尺寸：

```json
{
  "image_size": [1200, 800],
  "background": "#ffffff",
  "regions": [
    { "kind": "surface", "box": [20, 20, 300, 180], "fill": "#eeeeee" },
    { "kind": "text", "box": [36, 36, 100, 18] },
    { "kind": "control", "box": [36, 120, 80, 28] },
    { "kind": "media", "box": [350, 20, 180, 180] }
  ]
}
```

文字按可见行标注，不能用父容器大矩形填掉行间空白。容器先父后子。需要只改原图中的指定区域时，可另用 `replace_regions.py page.png regions.json new.png --kind text`；它是局部替换工具，不是整体抽象的默认输出。

## 验证与解读

至少核对代表性文字、控件、容器与原图的位置和边界，实际打开生成图。保持相同内容、视口、状态和采集方法比较两版。把“观察到的分布”与“为何不合适”分开；例如一侧色块密集是观察，是否需要调整取决于它承担的工作，不能机械追求左右平衡。

脚本测试：`python scripts/test_render_blocks.py`。采集器集成测试需要环境提供 Playwright：`bun scripts/test_collect_regions.mjs`；可追加已启动的本地页面 URL 和新的输出目录，保存真实页面的 regions.json 与 original.png。这是开发验证入口，不要求日常使用安装另一个浏览器控制环境。skill-creator 的 `quick_validate.py` 另需 PyYAML。
