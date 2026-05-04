# 生图 AI 完整风格库 V1

> 说明：这是面向生图 AI 提示词使用的风格库，不是严格设计史目录。整理标准是：AI 是否容易识别、是否能稳定控制画面、是否适合作为 prompt 风格标签。

---

## 使用逻辑

写提示词时，不要只写一个风格词。更稳定的结构是：

```text
主体 + 设计/艺术风格 + 表现技法 + 媒介/材质 + 构图 + 光影/摄影 + 质量要求
```

例如：

```text
一张运动鞋广告海报，扁平化波普艺术风格，赛璐璐上色，粗黑描边，半调网点，爆炸框构图，丝网印刷质感，高饱和色彩
```

对应结构是：

```text
主体：运动鞋广告海报
设计风格：扁平化波普艺术
表现技法：赛璐璐上色
视觉元素：粗黑描边、半调网点
构图：爆炸框构图
媒介质感：丝网印刷
色彩：高饱和
```

---

# 一、基础设计 / 艺术流派

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 极简主义 | minimalist design, minimalism | 品牌、海报、UI、产品、室内 |
| 极繁主义 | maximalism | 时尚、包装、装饰性海报 |
| 现代主义 | modernism, modernist design | 建筑、家具、平面、产品 |
| 后现代主义 | postmodern design | 拼贴、反常规、幽默混搭 |
| 功能主义 | functionalism | 产品、工业设计、建筑 |
| 国际主义风格 | International Style | 建筑、品牌、平面系统 |
| 包豪斯风格 | Bauhaus | 几何海报、家具、建筑、排版 |
| 瑞士国际主义平面风 | Swiss Style, International Typographic Style | 海报、品牌、字体排版 |
| 装饰艺术风格 | Art Deco | 奢华、几何、珠宝、建筑、包装 |
| 新艺术运动风格 | Art Nouveau | 花卉曲线、女性形象、装饰海报 |
| 工艺美术运动 | Arts and Crafts | 手工感、自然纹样、复古包装 |
| 构成主义风格 | Constructivism | 政治海报、红黑白几何构图 |
| 风格派 | De Stijl | 红黄蓝、黑白灰、垂直水平构成 |
| 未来主义 | Futurism | 速度、机器、城市、动态感 |
| 达达主义 | Dadaism | 拼贴、荒诞、反设计 |
| 超现实主义 | Surrealism | 梦境、异空间、概念视觉 |
| 欧普艺术 | Op Art | 视错觉、黑白几何、强视觉冲击 |
| 波普艺术 | Pop Art | 漫画、广告、高饱和、消费符号 |
| 迷幻艺术 | Psychedelic Art | 60 年代音乐海报、迷幻色彩 |
| 孟菲斯风格 | Memphis Design | 彩色几何、波点、反功能主义 |
| 意大利激进设计 | Italian Radical Design | 实验家具、反主流产品 |
| 新浪潮平面设计 | New Wave Graphic Design | 实验排版、80 年代平面视觉 |
| 反设计 | Anti-design | 故意粗糙、反商业、反规范 |
| 激进设计 | Radical Design | 概念家具、批判性产品设计 |
| 粗野主义 | Brutalism | 建筑、网页、海报、强体块感 |
| 解构主义 | Deconstructivism | 破碎、扭曲、非线性结构 |
| 有机现代主义 | Organic Modernism | 自然曲线、家具、建筑、室内 |
| 生物形态设计 | Biomorphic Design | 有机曲线、仿生产品、空间 |
| 参数化设计 | Parametric Design | 算法曲面、建筑、产品、室内 |
| 可持续设计 | Sustainable Design, Eco Design | 环保包装、绿色建筑、生态品牌 |
| 包容性设计 | Inclusive Design | 公益、教育、医疗、无障碍视觉 |
| 服务设计视觉 | Service Design Visuals | 用户旅程图、流程图、系统说明 |
| 设计系统风格 | Design System Style | UI 组件库、品牌规范、SaaS |

---

# 二、历史 / 古典 / 装饰风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 古埃及风格 | Ancient Egyptian style | 神庙、壁画、金色符号、法老视觉 |
| 两河流域风格 | Mesopotamian style | 古文明、楔形文字、神话视觉 |
| 古希腊风格 | Ancient Greek style | 柱式、雕塑、比例、古典秩序 |
| 古罗马风格 | Ancient Roman style | 拱券、穹顶、帝国建筑、雕塑 |
| 拜占庭风格 | Byzantine style | 金色马赛克、宗教图像、圣像感 |
| 罗曼式风格 | Romanesque style | 厚重建筑、半圆拱、宗教空间 |
| 哥特式风格 | Gothic style | 尖拱、玫瑰窗、教堂、暗黑装饰 |
| 伊斯兰几何风格 | Islamic geometric design | 几何纹样、花砖、清真寺 |
| 文艺复兴风格 | Renaissance style | 透视、古典比例、人文主义 |
| 巴洛克风格 | Baroque style | 戏剧性、金色、强装饰、动态光影 |
| 洛可可风格 | Rococo style | 柔美曲线、粉色、宫廷装饰 |
| 新古典主义 | Neoclassicism | 对称、庄重、古希腊罗马秩序 |
| 维多利亚风格 | Victorian style | 繁复装饰、复古字体、华丽室内 |
| 爱德华时期风格 | Edwardian style | 轻盈古典、优雅室内、复古服饰 |
| 折衷主义 | Eclecticism | 多风格混搭、历史元素拼接 |
| 浪漫主义风格 | Romanticism | 情绪化、自然、史诗感、戏剧画面 |
| 新哥特风格 | Gothic Revival | 哥特复兴建筑、暗黑古典装饰 |
| 殖民风格 | Colonial style | 复古住宅、木质空间、历史感 |
| 地中海风格 | Mediterranean style | 白墙、蓝色、拱门、海边感 |
| 摩洛哥风格 | Moroccan style | 花砖、拱门、浓烈色彩 |
| 俄式构成主义 | Russian Constructivism | 红黑白、政治海报、强几何 |

---

# 三、平面设计 / 海报 / 排版风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 瑞士网格风 | Swiss grid layout | 海报、杂志、品牌系统 |
| 文字主导设计 | typography-driven design | 海报、封面、社交图 |
| 大字报风格 | bold typography poster | 强口号、宣传海报 |
| 实验排版 | experimental typography | 艺术海报、音乐视觉、展览视觉 |
| 编辑设计风 | editorial design | 杂志、画册、品牌内容 |
| 杂志封面风 | magazine cover design | 人像、时尚、文化封面 |
| 画册设计风 | art book layout, catalog design | 展览、摄影集、品牌画册 |
| 拼贴风 | collage design | 海报、封面、实验视觉 |
| 达达拼贴风 | Dada collage | 荒诞、碎片化、复古印刷 |
| 剪贴簿风 | scrapbook aesthetic | 手账、青春、复古生活方式 |
| 丝网印刷风 | screen print poster | 音乐海报、街头视觉 |
| Risograph 印刷风 | risograph print style | 独立出版、颗粒插画 |
| 凸版印刷风 | letterpress style | 复古字体、手工感包装 |
| 胶版印刷风 | offset print style | 杂志、报纸、复古海报 |
| 报纸印刷风 | newspaper print style | 旧报纸、纪实、拼贴 |
| 复古海报风 | vintage poster design | 广告、旅行、电影、活动海报 |
| 复古旅游海报风 | vintage travel poster | 城市、景点、航空、铁路 |
| 政治宣传海报风 | propaganda poster style | 口号、英雄人物、强构图 |
| 广告海报风 | advertising poster design | 产品、商业、活动视觉 |
| 波普海报风 | pop art poster | 漫画、消费符号、高饱和 |
| 朋克杂志风 | punk zine aesthetic | 剪贴、粗糙字体、反叛感 |
| 垃圾摇滚风 | grunge design | 破损纹理、脏污图层、90 年代感 |
| 涂鸦风格 | graffiti style | 街头、潮牌、音乐、青年文化 |
| 新丑风 | new ugly design | 故意怪异、反精致、错位排版 |
| 数字粗野主义 | digital brutalism | 原始网页感、硬边字体、强对比 |
| 粗野主义海报 | brutalist poster design | 大字、强对比、压迫感构图 |
| 艺术展览视觉 | art exhibition identity | 美术馆、画廊、文化品牌 |
| 品牌手册风 | brand guideline style | 品牌规范、色彩、字体、Logo 展示 |
| 信息图风格 | infographic style | 科普、商业、教育、数据说明 |
| 图标系统风 | icon system design | UI、品牌、说明图 |
| 图案平铺风 | seamless pattern design | 包装、纺织、背景图 |
| 贴纸拼贴风 | sticker collage layout | 潮流、Y2K、社交媒体图 |

---

# 四、UI / 数字产品 / 网页风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 扁平化设计 | flat design, flat UI | App、图标、网页、信息图 |
| 拟物化设计 | skeuomorphic UI | 真实按钮、皮革、金属、老式 App |
| 新拟物风 | neumorphism UI | 柔和浮雕、浅色界面、按钮 |
| 玻璃拟态 | glassmorphism UI | 毛玻璃、透明卡片、科技界面 |
| 液态玻璃风 | liquid glass UI | 折射、透明、流体高光、未来界面 |
| 黏土拟态 | claymorphism | 柔软 3D、圆润图标、儿童化产品 |
| Material Design 风格 | Material Design UI | 卡片、层级、阴影、移动端界面 |
| 暗黑模式 UI | dark mode UI | 黑底、霓虹点缀、科技产品 |
| 科幻界面 | sci-fi interface, FUI | 飞船、控制台、未来 HUD |
| 游戏 HUD 风格 | game HUD interface | 血条、地图、任务面板 |
| 仪表盘 UI | dashboard UI design | 数据面板、后台、商业系统 |
| 企业级后台风 | enterprise dashboard UI | SaaS、CRM、数据平台 |
| SaaS 官网风 | SaaS landing page design | 科技公司官网、产品展示 |
| 苹果式极简 UI | Apple-inspired UI | 留白、玻璃感、产品导向 |
| Web3 风格 | Web3 interface design | 渐变、3D 图形、科技金融 |
| AI 产品风 | AI product interface design | 蓝紫渐变、抽象光效、智能感 |
| 全息 UI | holographic UI | 透明蓝光、悬浮界面、科幻感 |
| 赛博 UI | cyber UI, cyberpunk UI | 霓虹、黑底、网格、未来城市 |
| 响应式网页风 | responsive web design | 多屏幕展示、现代网页视觉 |
| 组件库风格 | component library UI | 按钮、卡片、表格、设计系统 |
| 旧互联网风 | old web aesthetic | 早期网页、像素按钮、低保真 |
| Windows 95 风格 | Windows 95 UI aesthetic | 复古电脑、灰色窗口、像素按钮 |
| Frutiger Aero UI | Frutiger Aero UI | 玻璃、水滴、蓝绿、2000s 科技 |
| Frutiger Metro | Frutiger Metro | 彩色几何、早期系统 UI、都市科技 |
| 网页粗野主义 | web brutalism | 原始 HTML 感、强字体、反模板 |
| 液态渐变 UI | liquid gradient UI | 背景渐变、柔和光晕、现代科技 |
| Aurora 渐变 | aurora gradient | 蓝紫绿光晕、SaaS、AI 产品 |
| Mesh 渐变 | gradient mesh design | 品牌背景、网页视觉、科技产品 |

---

# 五、插画 / 图像表现风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 平面插画 | flat illustration | 品牌插画、网页、海报 |
| 矢量插画 | vector illustration | 图标、商业插画、信息图 |
| 等距插画 | isometric illustration | 城市、办公、科技场景 |
| 线稿风 | line art illustration | 包装、说明图、艺术插画 |
| 粗线条插画 | bold outline illustration | 儿童、潮流、社交媒体 |
| 几何插画 | geometric illustration | 抽象人物、品牌图形、海报 |
| 儿童书插画 | children’s book illustration | 温和、故事性、柔软画面 |
| 社论插画 | editorial illustration | 杂志、新闻、观点表达 |
| 概念艺术 | concept art | 游戏、电影、世界观设计 |
| 角色设定图 | character design sheet | 游戏、动画、IP 设计 |
| 漫画风 | comic book style | 分镜、角色、动作场景 |
| 美漫风 | American comic style | 英雄、动作、强线条 |
| 欧漫风 | European comic style | 冒险、复古、线条感 |
| 法漫风 | bande dessinée style | 精致线稿、欧洲绘本感 |
| 日漫风 | anime style | 动漫人物、场景、情绪表达 |
| 复古日漫风 | retro anime style, 80s anime | 怀旧动画、科幻、青春感 |
| 黑白漫画风 | black and white manga style | 分镜、故事感、线稿 |
| 网点漫画风 | screentone manga style | 黑白漫画、复古印刷 |
| 少年漫画风 | shonen manga style | 热血、动作、角色 |
| 少女漫画风 | shojo manga style | 柔美、浪漫、闪光效果 |
| Q版风格 | chibi style | 头像、贴纸、可爱角色 |
| 吉祥物风格 | mascot design | 品牌形象、IP 角色 |
| 贴纸风格 | sticker illustration | 表情包、周边、社交图 |
| 动画截图感 | animation still look | 场景图、故事画面 |
| 视觉小说风 | visual novel style | 角色立绘、恋爱游戏 |
| 乙女游戏风 | otome game style | 精致人物、柔和光影 |
| 复古科幻插画 | retro sci-fi illustration | 太空、机器人、旧时代科幻 |
| 企业孟菲斯插画 | Corporate Memphis | 科技公司官网、职场人物 |
| 阿莱格里亚插画 | Alegria illustration | 大手大脚人物、SaaS 品牌 |
| 低保真手绘风 | lo-fi hand-drawn illustration | 随性、亲切、手账、草图感 |
| 幼稚艺术风 | Naive Art | 天真、原始、非学院派绘画 |
| 原生艺术 / 局外人艺术 | Art Brut, Outsider Art | 粗粝、直觉化、非规范视觉 |

---

# 六、渲染 / 上色 / 表现技法风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 赛璐璐风格 | cel-shaded style, cel animation style | 动漫、游戏、角色、插画 |
| 日漫赛璐璐风 | anime cel shading | 动漫人物、清晰上色 |
| 传统动画赛璐璐质感 | traditional cel animation look | 动画截图、复古动画 |
| 卡通渲染 | toon shading, cartoon rendering | 角色、游戏、儿童视觉 |
| 非真实感渲染 | non-photorealistic rendering, NPR | 风格化 3D、技术插画 |
| 手绘渲染 | hand-drawn rendering | 插画、建筑草图、概念图 |
| 平涂风格 | flat color illustration | 商业插画、角色、海报 |
| 厚涂风格 | painterly rendering, thick painting style | 概念艺术、角色、幻想场景 |
| 半厚涂风格 | semi-painterly style | 游戏角色、卡牌、概念设定 |
| 水彩渲染 | watercolor rendering | 儿童书、旅行插画、柔和画面 |
| 油画渲染 | oil painting style | 人像、古典场景、艺术化图像 |
| 丙烯画风 | acrylic painting style | 装饰画、现代插画 |
| 粉彩画风 | pastel illustration | 柔和人物、儿童、生活方式 |
| 墨水插画 | ink illustration | 线稿、黑白图、漫画感 |
| 炭笔素描 | charcoal drawing | 肖像、人体、戏剧光影 |
| 铅笔素描 | pencil sketch | 概念草图、产品草图、人物 |
| 马克笔渲染 | marker rendering | 工业设计、汽车、产品草图 |
| 建筑手绘渲染 | architectural hand rendering | 建筑、室内、空间概念 |
| 蓝图风格 | blueprint style | 机械、建筑、科幻设定 |
| 技术插图风 | technical illustration | 产品结构、说明图、机械图 |
| 剖面图风格 | cutaway illustration | 建筑、机械、科普图 |
| 爆炸图风格 | exploded view illustration | 产品结构、机械装配、说明书 |
| 线稿上色风 | line art with flat colors | 插画、角色、漫画 |
| 硬边阴影风 | hard-edged shadows | 赛璐璐、漫画、海报 |
| 柔和渐变风 | soft gradient shading | UI、商业插画、3D 图标 |
| 高对比明暗风 | high contrast lighting | 戏剧场景、电影感、人像 |
| 半调网点风 | halftone dots | 波普、漫画、印刷质感 |
| 漫画网点风 | manga screentone | 黑白漫画、日漫分镜 |
| 喷枪渲染 | airbrush rendering | 复古广告、汽车、科幻封面 |

---

# 七、3D / 游戏 / 玩具 / 虚拟资产风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 低多边形风 | low poly style | 游戏、图标、场景 |
| 体素风格 | voxel art | 方块场景、游戏资产 |
| 像素艺术 | pixel art | 复古游戏、8-bit / 16-bit |
| 黏土 3D 风 | clay 3D style, claymorphism | 图标、儿童、品牌插画 |
| 玩具渲染风 | toy-like rendering | 产品、角色、潮玩 |
| 手办渲染风 | collectible figure render | IP、角色、潮玩 |
| 盲盒风格 | designer toy blind box style | 可爱角色、潮玩产品 |
| 潮玩风格 | designer toy style | IP、公仔、品牌角色 |
| 皮克斯式 3D | stylized 3D animation style | 家庭向角色、电影感 |
| 风格化 3D | stylized 3D | 商业插画、角色、场景 |
| 等距 3D 风 | isometric 3D | 科技、数据中心、办公场景 |
| 3D 图标风 | 3D icon design | App、功能图、SaaS |
| 游戏概念图风 | game concept art | 场景、角色、世界观 |
| 游戏原画风 | game key art | 宣传图、角色、场景 |
| 卡牌插画风 | trading card illustration | 奇幻、角色、战斗 |
| 等距游戏风 | isometric game art | 城市、房间、策略游戏 |
| 低保真游戏风 | lo-fi game aesthetic | 像素、复古、独立游戏 |
| PS1 低模风 | PS1 low-poly style | 复古恐怖、低清游戏 |
| 任天堂式可爱风 | cozy stylized game art | 温暖、可爱、休闲游戏 |
| 暗黑游戏美术 | dark fantasy game art | 怪物、地下城、奇幻 |
| 科幻游戏 HUD | sci-fi game HUD | 界面、机甲、飞船 |
| 开放世界概念图 | open world concept art | 大场景、地图、环境设定 |
| 机甲设定风 | mecha design | 机器人、战斗机甲、科幻装备 |
| 武器设定风 | weapon concept design | 游戏武器、科幻装备 |
| 道具设定风 | prop design | 游戏、动画、电影道具 |
| 环境设定风 | environment concept art | 游戏、电影、世界观场景 |

---

# 八、摄影 / 影像 / 镜头风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 电影感 | cinematic style | 人像、场景、广告 |
| 剧照风格 | film still | 人物、故事画面 |
| 纪录片摄影风 | documentary photography | 真实人物、街景、社会题材 |
| 时尚摄影风 | fashion editorial photography | 模特、服装、杂志 |
| 产品摄影风 | product photography | 包装、商品、商业图 |
| 棚拍广告风 | studio advertising photography | 高级产品图 |
| 胶片摄影风 | film photography | 复古、人像、生活方式 |
| 宝丽来风 | Polaroid photo style | 青春、旅行、日常 |
| VHS 录像风 | VHS aesthetic | 复古影像、恐怖、90s |
| 监控录像风 | CCTV footage style | 悬疑、纪实、低清 |
| 手持摄影风 | handheld camera look | 真实、紧张、纪录感 |
| 鱼眼镜头风 | fisheye lens style | 街头、滑板、Y2K |
| 微距摄影风 | macro photography | 产品、昆虫、细节 |
| 移轴摄影风 | tilt-shift photography | 城市、模型感 |
| 高速摄影风 | high-speed photography | 液体、爆炸、运动 |
| 长曝光风 | long exposure photography | 夜景、灯轨、梦幻 |
| 黑白摄影风 | black and white photography | 纪实、人像、建筑 |
| 黑色电影摄影 | film noir lighting | 强阴影、悬疑、复古 |
| 黄金时刻摄影 | golden hour photography | 人像、旅行、自然场景 |
| 蓝调时刻摄影 | blue hour photography | 城市、夜景、电影感 |
| 闪光灯直拍风 | direct flash photography | 时尚、派对、街拍 |
| 低保真摄影 | lo-fi photography | 青春、复古、独立杂志 |
| 街头摄影风 | street photography | 城市、人物、纪实 |
| 建筑摄影风 | architectural photography | 建筑、空间、室内 |
| 食品摄影风 | food photography | 餐饮、包装、菜单 |
| 奢侈品广告摄影 | luxury advertising photography | 香水、珠宝、腕表 |
| 运动摄影风 | sports photography | 动态、速度、能量 |

---

# 九、媒介 / 印刷 / 手工工艺风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 木刻版画风 | woodcut print style | 民艺、复古、黑白图 |
| 浮世绘版画风 | ukiyo-e print style | 日式海浪、人物、风景 |
| 铜版画风 | engraving style | 古典科学图、地图、动物 |
| 蚀刻版画风 | etching style | 复古插图、建筑、肖像 |
| 丝网印刷风 | screen print style | 海报、音乐、街头 |
| Risograph 风 | risograph print style | 独立出版、颗粒插画 |
| 胶版印刷风 | offset print style | 复古杂志、海报 |
| 报纸印刷风 | newspaper print style | 旧报纸、拼贴、纪实 |
| 旧书插图风 | vintage book illustration | 科普、植物、动物 |
| 科学插图风 | scientific illustration | 动植物、医学、机械 |
| 植物图谱风 | botanical illustration | 花卉、草药、包装 |
| 动物图谱风 | zoological illustration | 自然历史、科普图 |
| 医学插图风 | medical illustration | 解剖、医学科普、器官结构 |
| 地图插画风 | illustrated map | 旅行、城市、游戏地图 |
| 纸雕风格 | paper cutout, paper craft | 立体插画、儿童、广告 |
| 剪纸风格 | paper cutting style | 民俗、节庆、装饰 |
| 拼贴画风 | collage art | 海报、杂志、实验视觉 |
| 撕纸拼贴风 | torn paper collage | 独立杂志、手工感 |
| 刺绣风格 | embroidery style | 手工、服装、民艺 |
| 编织风格 | knitted texture style | 温暖、手作、家居 |
| 陶瓷釉面风 | ceramic glaze style | 器皿、产品、手工感 |
| 马赛克风格 | mosaic style | 壁画、宗教、装饰图案 |
| 彩色玻璃风 | stained glass style | 教堂、装饰窗、神秘感 |
| 珐琅工艺风 | enamel style | 珠宝、徽章、复古工艺 |
| 漆器风格 | lacquerware style | 东方器物、奢华工艺 |
| 金箔风格 | gold leaf style | 宗教、奢华、装饰画 |
| 纺织图案风 | textile pattern design | 布料、家居、包装 |
| 陶土手作风 | handmade clay craft | 器皿、手工、生活方式 |

---

# 十、材质 / 表面质感风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 铬金属风 | chrome aesthetic | Y2K、产品、字体 |
| 液态金属风 | liquid metal aesthetic | 科技、奢侈、未来感 |
| 全息镭射风 | holographic aesthetic | 包装、科技、时尚 |
| 虹彩风格 | iridescent material | 香水、科技、饰品 |
| 透明塑料风 | transparent plastic aesthetic | Y2K、电子产品、玩具 |
| 磨砂玻璃风 | frosted glass effect | UI、包装、空间 |
| 毛玻璃风 | glassmorphism | UI、科技、卡片界面 |
| 果冻质感 | jelly texture | 可爱、食品、3D 图标 |
| 橡胶质感 | rubber material style | 产品、玩具、潮流 |
| 充气塑料风 | inflatable design | 家具、潮玩、活动视觉 |
| 泡泡质感 | bubble texture | 儿童、可爱、未来感 |
| 粘液质感 | slime texture | 怪核、Y2K、实验视觉 |
| 粗颗粒质感 | grainy texture | 复古、胶片、印刷 |
| 做旧质感 | distressed texture | 朋克、复古、海报 |
| 破损纹理 | grunge texture | 摇滚、街头、反设计 |
| 纸张纹理 | paper texture | 包装、书籍、海报 |
| 布料纹理 | fabric texture | 服装、家居、手工 |
| 大理石质感 | marble texture | 奢侈、室内、包装 |
| 混凝土质感 | concrete texture | 粗野主义、建筑、工业风 |
| 木纹质感 | wood grain texture | 北欧、自然、家具 |
| 皮革质感 | leather texture | 奢侈品、复古、包装 |
| 金箔质感 | gold foil texture | 高端包装、海报、邀请函 |
| 珠光质感 | pearlescent material | 美妆、香水、奢侈品 |
| 陶瓷质感 | ceramic material | 器皿、产品、手作 |
| 釉面质感 | glazed material | 陶瓷、包装、装饰 |
| 磨砂金属 | matte metal | 科技产品、工业设计 |
| 拉丝金属 | brushed metal | 家电、腕表、科技产品 |
| 碳纤维质感 | carbon fiber texture | 汽车、运动、科技装备 |
| 水晶质感 | crystal material | 珠宝、奢侈、奇幻 |
| 冰晶质感 | ice crystal texture | 冬季、珠宝、科幻 |
| 烟雾质感 | smoky texture | 香水、电影感、暗黑视觉 |
| 液体质感 | liquid texture | 美妆、饮料、抽象视觉 |

---

# 十一、产品 / 家具 / 工业设计风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 德国工业设计 | German industrial design | 家电、工具、理性产品 |
| 包豪斯家具风 | Bauhaus furniture design | 椅子、灯具、几何家具 |
| 中世纪现代家具 | Mid-century modern furniture | 沙发、椅子、室内场景 |
| 北欧家具风 | Scandinavian furniture design | 木材、布艺、温暖极简 |
| 意大利现代家具 | Italian modern furniture | 高级、流线、雕塑感家具 |
| 孟菲斯产品设计 | Memphis product design | 彩色家具、灯具、装饰产品 |
| 太空时代设计 | Space Age design | 圆润塑料、白色舱体、未来复古 |
| 流线型现代风 | Streamline Moderne | 汽车、家电、交通工具 |
| 复古电子产品风 | retro electronics design | 收音机、电视、游戏机 |
| 透明科技产品风 | transparent tech product design | 透明外壳、内部结构 |
| 苹果式产品设计 | Apple-inspired product design | 极简、铝合金、白色背景 |
| 模块化产品设计 | modular product design | 可拆卸、组合系统 |
| 生物形态产品设计 | biomorphic product design | 曲线、有机外形、自然仿生 |
| 软体家具风 | soft organic furniture | 圆润、柔软、云朵感 |
| 奢侈品产品设计 | luxury product design | 高端材质、商业摄影 |
| 可持续产品设计 | sustainable product design | 再生材料、环保结构 |
| 参数化产品设计 | parametric product design | 算法曲面、复杂孔洞 |
| 医疗产品设计 | medical product design | 干净、精密、可信赖 |
| 户外装备设计 | outdoor gear design | 功能性、耐用、运动感 |
| 运动装备设计 | sports equipment design | 动态、速度、性能感 |
| 汽车概念设计 | automotive concept design | 未来汽车、交通工具 |
| 家电设计风 | home appliance design | 现代厨房、智能家居 |
| 智能硬件设计 | smart hardware design | AI 设备、穿戴设备、科技产品 |
| 潮玩产品设计 | designer toy product design | 公仔、盲盒、收藏玩具 |

---

# 十二、建筑 / 室内 / 空间风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 现代建筑 | modern architecture | 住宅、办公楼、公共空间 |
| 极简建筑 | minimalist architecture | 白墙、体块、留白 |
| 国际主义建筑 | International Style architecture | 玻璃、钢、混凝土、盒子体量 |
| 粗野主义建筑 | brutalist architecture | 裸露混凝土、大体量 |
| 解构主义建筑 | deconstructivist architecture | 扭曲、破碎、非正交结构 |
| 参数化建筑 | parametric architecture | 曲面、网格、算法造型 |
| 未来主义建筑 | futuristic architecture | 智能城市、科幻空间 |
| 高技派建筑 | high-tech architecture | 外露结构、管线、金属构件 |
| 有机建筑 | organic architecture | 自然融合、曲线、木石材料 |
| 生物仿生建筑 | biomorphic architecture | 细胞、骨骼、植物形态 |
| 包豪斯建筑 | Bauhaus architecture | 几何、白墙、功能主义 |
| 北欧室内 | Scandinavian interior design | 木材、白色、温暖、实用 |
| 日式现代室内 | Japanese modern interior | 木格栅、榻榻米、自然光 |
| 侘寂风室内 | wabi-sabi interior | 粗糙墙面、旧木、低饱和 |
| 工业风室内 | industrial interior design | 水泥、金属、管线、裸砖 |
| 法式复古室内 | French vintage interior | 石膏线、壁炉、古典家具 |
| 意式现代室内 | Italian modern interior | 高级材质、雕塑感家具 |
| 轻奢风室内 | modern luxury interior | 大理石、金属、柔和灯光 |
| 奶油风室内 | creamy minimalist interior | 米白、圆润、柔软 |
| 地中海室内 | Mediterranean interior | 白墙、蓝色、拱门 |
| 摩洛哥室内 | Moroccan interior design | 花砖、拱门、浓烈色彩 |
| 太空舱风 | space capsule interior | 白色、圆角、舱体 |
| 赛博朋克空间 | cyberpunk interior | 霓虹、雨夜、未来城市 |
| 有机未来主义空间 | organic futuristic interior | 生物曲线、未来自然感 |
| 生态未来主义空间 | eco futuristic architecture | 绿色能源、植物建筑 |
| 展览空间设计 | exhibition space design | 美术馆、品牌展、装置 |
| 零售空间设计 | retail interior design | 门店、橱窗、商业空间 |
| 酒店空间设计 | boutique hotel interior | 高级、舒适、品牌化 |
| 咖啡馆空间设计 | specialty coffee interior | 生活方式、品牌空间 |
| 办公空间设计 | modern office interior | 科技公司、开放办公 |
| 未来城市设计 | futuristic city design | 智慧城市、科幻建筑群 |
| 反乌托邦城市 | dystopian cityscape | 黑暗、拥挤、未来压迫感 |

---

# 十三、包装 / 品牌 / 商业视觉风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 高端奢侈品牌风 | luxury brand design | 香水、珠宝、时装、精品包装 |
| 极简品牌风 | minimalist branding | 科技、护肤、家居 |
| 现代科技品牌风 | modern tech branding | AI、SaaS、硬件、创业公司 |
| 精品咖啡品牌风 | specialty coffee branding | 咖啡包装、门店、菜单 |
| 手工品牌风 | artisanal brand design | 烘焙、香薰、手作 |
| 有机食品包装风 | organic food packaging | 食品、饮品、农产品 |
| 环保包装风 | eco-friendly packaging | 可持续材料、再生纸 |
| 日式包装风 | Japanese packaging design | 和纸、留白、精致小物 |
| 北欧包装风 | Scandinavian packaging design | 简洁、温和、自然材料 |
| 复古食品包装风 | retro food packaging | 罐头、汽水、零食 |
| 复古药房包装风 | vintage apothecary packaging | 药瓶、草本、老字号 |
| 美妆包装风 | cosmetic packaging design | 护肤、彩妆、香氛 |
| 香水包装风 | luxury perfume packaging | 玻璃、金属、柔光 |
| DTC 品牌风 | DTC brand design | 年轻消费品牌、电商视觉 |
| 潮牌视觉 | streetwear brand identity | 服装、街头文化、字体标识 |
| 运动品牌风 | sports brand identity | 动感、速度、能量 |
| 艺术品牌风 | art brand identity | 展览、画廊、文化商品 |
| 生活方式品牌风 | lifestyle branding | 家居、香薰、杂货 |
| 医疗健康品牌风 | healthcare branding | 干净、可信、柔和 |
| 儿童品牌风 | children’s brand design | 圆润、可爱、明亮 |
| 食品饮料品牌风 | food and beverage branding | 包装、菜单、广告 |
| 音乐节视觉 | music festival identity | 海报、舞台、宣传物料 |
| 电影海报风 | movie poster design | 宣传海报、角色视觉 |
| 展会视觉系统 | event visual identity | 主视觉、导视、宣传图 |

---

# 十四、年代 / 复古 / 时代风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 1920 年代装饰艺术风 | 1920s Art Deco | 爵士、奢华、金色、几何 |
| 1930 年代流线型现代风 | 1930s Streamline Moderne | 汽车、列车、速度、铬金属 |
| 1950 年代复古风 | 1950s retro design | 广告、厨房、家电、粉彩 |
| 1960 年代迷幻风 | 1960s psychedelic design | 音乐海报、嬉皮、彩色曲线 |
| 1970 年代复古风 | 1970s retro aesthetic | 暖色、颗粒、复古字体 |
| 1980 年代霓虹风 | 1980s neon aesthetic | 街机、霓虹网格、跑车 |
| 1990 年代杂志风 | 1990s editorial design | 青年文化、时尚、粗糙排版 |
| 1990 年代垃圾摇滚风 | 1990s grunge aesthetic | 破损、脏污、乐队海报 |
| Y2K 风格 | Y2K aesthetic | 银色、透明塑料、早期互联网 |
| 千禧辣妹风 | McBling aesthetic | 粉色、亮片、金属、时尚杂志 |
| 复古未来主义 | retrofuturism | 旧时代对未来的想象 |
| 太空时代风 | Space Age design | 白色塑料、圆形舱体、宇航元素 |
| 弗鲁蒂格水色美学 | Frutiger Aero | 蓝绿、玻璃、水滴、气泡 |
| 弗鲁蒂格都会风 | Frutiger Metro | 彩色几何、系统 UI、城市科技 |
| 旧互联网风 | old internet aesthetic | 早期网页、按钮、像素、低保真 |
| VHS 录像带风 | VHS aesthetic | 噪点、扫描线、复古影像 |
| 胶片摄影风 | film photography | 颗粒、暖色、自然曝光 |
| 宝丽来风 | Polaroid aesthetic | 即时成像、白边、生活记录 |
| 早期数码相机风 | digicam aesthetic | 闪光灯、低清、2000s 日常 |
| 街机游戏风 | arcade aesthetic | 霓虹、像素、游戏厅 |
| 复古电脑风 | retro computer aesthetic | CRT、像素、老系统界面 |
| 模拟电视风 | analog TV aesthetic | 扫描线、失真、怀旧影像 |

---

# 十五、亚文化 / 氛围 / 审美标签

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 赛博朋克 | cyberpunk | 霓虹、雨夜、未来城市、黑客 |
| 蒸汽朋克 | steampunk | 黄铜、齿轮、蒸汽机械 |
| 柴油朋克 | dieselpunk | 战间期机械、军工、复古未来 |
| 原子朋克 | atompunk | 冷战、核能、50 年代未来想象 |
| 太阳朋克 | solarpunk | 绿色能源、乐观未来、生态城市 |
| 蒸汽波 | vaporwave | 粉紫渐变、古典雕塑、复古电脑 |
| 合成波 | synthwave | 80 年代霓虹、网格、跑车、夕阳 |
| 梦核 | dreamcore | 梦境、模糊、熟悉但不真实 |
| 怪核 | weirdcore | 异常、荒诞、不安的超现实 |
| 阈限空间 | liminal space aesthetic | 空荡商场、走廊、泳池 |
| 暗黑学院风 | dark academia | 旧书、学院、深色、古典知识感 |
| 轻学院风 | light academia | 米色、文具、校园、柔和复古 |
| 哥特风 | gothic aesthetic | 黑色、尖拱、暗黑浪漫 |
| 黑色电影风 | film noir aesthetic | 高反差、侦探、烟雾 |
| 朋克风 | punk aesthetic | 反叛、拼贴、铆钉、粗糙字体 |
| 滑板文化风 | skate culture graphic design | 街头、贴纸、涂鸦 |
| 街头潮流风 | streetwear aesthetic | 潮牌、喷绘、城市背景 |
| 可爱风 | kawaii aesthetic | 圆润、粉色、卡通、亲和 |
| 暗黑奇幻风 | dark fantasy style | 怪物、古堡、阴影、魔法 |
| 高级灰审美 | muted luxury aesthetic | 低饱和、克制、时尚 |
| 多巴胺风格 | dopamine design | 高饱和、多彩、快乐 |
| 哥布林核 | goblincore | 苔藓、蘑菇、自然怪趣 |
| 乡村核 | cottagecore | 田园、花草、手作、慢生活 |
| 仙女核 | fairycore | 森林、闪光、柔和幻想 |
| 海妖核 | mermaidcore | 珍珠、贝壳、水色、梦幻 |
| 天使核 | angelcore | 白色、羽毛、柔光、神圣感 |
| 恐怖可爱风 | creepy cute | 可爱 + 诡异 |
| 迷雾氛围 | foggy atmospheric aesthetic | 悬疑、梦境、电影感 |
| 反乌托邦风 | dystopian aesthetic | 压迫、灰暗、未来城市 |
| 乌托邦未来风 | utopian futuristic aesthetic | 明亮、科技、理想城市 |

---

# 十六、东方 / 地域文化风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 日式极简 | Japanese minimalism | 留白、自然材质、安静秩序 |
| 日式禅意 | Zen aesthetic | 石庭、木材、低饱和、冥想感 |
| 侘寂美学 | wabi-sabi | 不完美、旧化、自然痕迹 |
| 浮世绘风格 | ukiyo-e | 日式版画、浪、艺伎、强线条 |
| 和风包装 | Japanese packaging design | 和纸、印章、留白 |
| 韩式极简 | Korean minimalist aesthetic | 柔和、干净、生活方式 |
| 新中式 | modern Chinese style | 传统元素 + 现代空间 / 品牌 |
| 国潮风 | guochao design | 中国符号、潮流配色、年轻化 |
| 中国水墨风 | Chinese ink painting aesthetic | 留白、墨色、山水、写意 |
| 工笔画风 | gongbi painting style | 精细线条、花鸟、传统人物 |
| 东方未来主义 | oriental futurism | 东方符号 + 未来科技 |
| 唐风美学 | Tang dynasty aesthetic | 华丽、金色、宫廷、盛唐服饰 |
| 宋风美学 | Song dynasty aesthetic | 雅致、留白、低饱和、文人审美 |
| 明式家具风 | Ming furniture style | 木材、比例、线条、东方理性 |
| 敦煌风格 | Dunhuang mural style | 壁画、飞天、矿物色 |
| 藏式装饰风 | Tibetan decorative style | 强色彩、宗教图案、金色纹样 |
| 印度装饰风 | Indian decorative style | 曼荼罗、浓烈色彩、纺织纹样 |
| 东南亚热带风 | Southeast Asian tropical style | 藤编、木材、热带植物 |
| 摩洛哥装饰风 | Moroccan decorative style | 花砖、拱门、几何图案 |
| 波斯细密画风 | Persian miniature style | 精细人物、装饰图案、古典叙事 |
| 非洲部落图案风 | African tribal pattern style | 几何纹样、强对比、手工感 |
| 拉丁美洲民艺风 | Latin American folk art | 鲜艳色彩、民俗图案、装饰性 |
| 墨西哥亡灵节风 | Day of the Dead style | 骷髅、花朵、浓烈色彩 |

---

# 十七、构图 / 版式 / 视觉语言风格

| 中文风格 | 英文关键词 | 适合用途 |
|---|---|---|
| 网格系统构图 | grid-based layout | 瑞士风、海报、品牌 |
| 中心构图 | centered composition | 产品、海报、图标 |
| 对称构图 | symmetrical composition | 建筑、奢侈、仪式感 |
| 不对称构图 | asymmetrical layout | 现代海报、编辑设计 |
| 放射状构图 | radial composition | 波普、宣传海报、爆炸感 |
| 对角线构图 | diagonal composition | 动态、运动、战斗 |
| 大留白构图 | negative space composition | 极简、奢侈、日式 |
| 满版构图 | full-bleed layout | 杂志、广告、海报 |
| 海报式构图 | poster composition | 商业图、电影图、活动图 |
| 杂志版式 | magazine layout | 编辑设计、时尚 |
| 信息图构图 | infographic layout | 科普、商业、教育 |
| 分屏构图 | split screen layout | 海报、对比图、广告 |
| 分镜构图 | storyboard layout | 动画、漫画、广告脚本 |
| 爆炸框构图 | comic burst composition | 波普、漫画、广告 |
| 贴纸拼贴构图 | sticker collage layout | 潮流、社交媒体、Y2K |
| 层叠卡片构图 | layered card layout | UI、SaaS、演示页 |
| 轴测构图 | axonometric composition | 建筑、产品、技术图 |
| 等距构图 | isometric composition | 科技、城市、办公 |
| 鸟瞰构图 | bird’s-eye view | 城市、建筑、游戏地图 |
| 仰视构图 | low-angle composition | 英雄感、建筑、权力感 |
| 俯视构图 | top-down composition | 产品、食物、地图 |
| 近景特写 | close-up composition | 产品、人像、细节 |
| 极端特写 | extreme close-up | 美妆、珠宝、食物 |
| 宽银幕构图 | cinematic widescreen composition | 电影感、场景、故事图 |
| 留白海报构图 | minimalist poster composition | 高级品牌、艺术海报 |
| 中轴对称海报 | axial symmetry poster | 奢侈、建筑、仪式感 |

---

# 十八、常用混合风格

| 中文混合风格 | 英文关键词 | 组合逻辑 |
|---|---|---|
| 扁平化波普艺术 | flat pop art style | 扁平矢量 + 波普艺术 |
| 极简赛博朋克 | minimalist cyberpunk | 极简构图 + 霓虹科技 |
| 瑞士波普海报 | Swiss pop poster style | 网格排版 + 高饱和波普色 |
| 包豪斯波普海报 | Bauhaus poster with pop colors | 几何构成 + 明亮流行色 |
| 新艺术奢侈包装 | Art Nouveau luxury packaging | 花卉曲线 + 高端包装 |
| 日式侘寂极简 | Japanese wabi-sabi minimalism | 日式留白 + 自然旧化 |
| 北欧极简 | Scandinavian minimalism | 北欧自然材料 + 极简秩序 |
| 粗野主义奢侈品牌 | brutalist luxury branding | 强硬体块 + 高端克制品牌 |
| 赛博粗野主义 | cyber brutalism | 数字粗野主义 + 赛博视觉 |
| 复古未来产品设计 | retro futuristic product design | 旧时代外壳 + 未来科技 |
| Y2K 铬金属风 | Y2K chrome aesthetic | 千禧年视觉 + 高反射金属 |
| 液态金属 Y2K | liquid metal Y2K | 流体铬金属 + 2000s 数码感 |
| 玻璃拟态科技 UI | glassmorphism tech UI | 毛玻璃 + 科技界面 |
| 黏土拟态 3D 图标 | claymorphism 3D icon style | 柔软黏土 + 圆润功能图标 |
| 编辑拼贴风 | editorial collage design | 杂志排版 + 拼贴图像 |
| 朋克粗野主义海报 | punk brutalist poster | 朋克拼贴 + 粗野排版 |
| 迷幻波普艺术 | psychedelic pop art | 迷幻色彩 + 波普符号 |
| 超现实极简海报 | surreal minimalist poster | 极简构图 + 超现实概念 |
| 有机未来主义建筑 | organic futuristic architecture | 生物曲线 + 未来建筑 |
| 参数化奢华室内 | parametric luxury interior | 参数化曲面 + 高端材质 |
| 生态未来主义设计 | eco futuristic design | 可持续理念 + 未来科技 |
| 极简奢侈品牌风 | minimalist luxury branding | 留白 + 高级材质 |
| 高端科技极简 | premium minimalist tech design | 科技产品 + 留白 + 冷静灯光 |
| 手绘极简 | hand-drawn minimalism | 简化造型 + 手绘线条 |
| 儿童书极简 | minimalist children’s book illustration | 温和配色 + 简单形状 |
| 拼贴波普 | pop art collage | 剪贴拼贴 + 波普漫画感 |
| 孟菲斯极简 | minimalist Memphis design | 孟菲斯几何 + 降低装饰密度 |
| 东方未来主义 | oriental futurism | 东方元素 + 科幻视觉 |
| 国潮赛博风 | cyber guochao style | 中国符号 + 霓虹未来 |
| 水墨未来主义 | ink futurism | 水墨留白 + 科技结构 |
| 奶油极简风 | creamy minimalism | 米白色调 + 柔软圆润 |
| 赛璐璐赛博朋克 | cel-shaded cyberpunk | 动画上色 + 霓虹未来城市 |
| 赛璐璐波普艺术 | cel-shaded pop art | 硬边动画上色 + 波普符号 |
| 复古日漫赛博 | retro anime cyberpunk | 80s 日漫 + 赛博朋克 |
| 水彩新艺术 | watercolor Art Nouveau | 水彩质感 + 花卉曲线 |
| 铬金属奢侈风 | chrome luxury aesthetic | 铬金属 + 高级商业摄影 |
| 粗野主义 UI | brutalist UI design | 强字体 + 原始网页结构 |
| 液态玻璃 AI 产品风 | liquid glass AI product UI | 液态玻璃 + AI 科技视觉 |
| 低多边形生态未来 | low poly solarpunk | 低模几何 + 绿色未来城市 |
| 像素赛博朋克 | pixel cyberpunk | 像素艺术 + 霓虹未来 |
| 玩具化奢侈品 | toy-like luxury product | 玩具渲染 + 高端产品陈列 |

---

# 十九、最终可复制核心候选库

如果要让 AI 在生成前“确认风格”，可以把下面这段作为候选风格库：

```text
极简主义、极繁主义、现代主义、后现代主义、功能主义、国际主义风格、包豪斯风格、瑞士国际主义平面风、装饰艺术风格、新艺术运动风格、工艺美术运动、构成主义风格、风格派、未来主义、达达主义、超现实主义、欧普艺术、波普艺术、迷幻艺术、孟菲斯风格、意大利激进设计、新浪潮平面设计、反设计、激进设计、粗野主义、解构主义、有机现代主义、生物形态设计、参数化设计、可持续设计、包容性设计、服务设计视觉、设计系统风格、古埃及风格、古希腊风格、古罗马风格、拜占庭风格、罗曼式风格、哥特式风格、伊斯兰几何风格、文艺复兴风格、巴洛克风格、洛可可风格、新古典主义、维多利亚风格、折衷主义、浪漫主义风格、瑞士网格风、文字主导设计、大字报风格、实验排版、编辑设计风、杂志封面风、拼贴风、达达拼贴风、剪贴簿风、丝网印刷风、Risograph 印刷风、凸版印刷风、复古海报风、复古旅游海报风、政治宣传海报风、波普海报风、朋克杂志风、垃圾摇滚风、涂鸦风格、新丑风、数字粗野主义、粗野主义海报、艺术展览视觉、品牌手册风、扁平化设计、拟物化设计、新拟物风、玻璃拟态、液态玻璃风、黏土拟态、Material Design 风格、暗黑模式 UI、科幻界面、游戏 HUD 风格、仪表盘 UI、企业级后台风、SaaS 官网风、苹果式极简 UI、Web3 风格、AI 产品风、全息 UI、赛博 UI、旧互联网风、Frutiger Aero UI、Frutiger Metro、网页粗野主义、Aurora 渐变、Mesh 渐变、平面插画、矢量插画、等距插画、线稿风、粗线条插画、几何插画、儿童书插画、社论插画、概念艺术、角色设定图、漫画风、美漫风、欧漫风、法漫风、日漫风、复古日漫风、黑白漫画风、网点漫画风、少年漫画风、少女漫画风、Q版风格、吉祥物风格、贴纸风格、动画截图感、视觉小说风、企业孟菲斯插画、阿莱格里亚插画、赛璐璐风格、日漫赛璐璐风、传统动画赛璐璐质感、卡通渲染、非真实感渲染、手绘渲染、平涂风格、厚涂风格、半厚涂风格、水彩渲染、油画渲染、丙烯画风、粉彩画风、墨水插画、炭笔素描、铅笔素描、马克笔渲染、建筑手绘渲染、蓝图风格、技术插图风、剖面图风格、爆炸图风格、半调网点风、喷枪渲染、低多边形风、体素风格、像素艺术、黏土 3D 风、玩具渲染风、手办渲染风、盲盒风格、潮玩风格、风格化 3D、等距 3D 风、3D 图标风、游戏概念图风、游戏原画风、卡牌插画风、等距游戏风、PS1 低模风、暗黑游戏美术、机甲设定风、环境设定风、电影感、剧照风格、纪录片摄影风、时尚摄影风、产品摄影风、棚拍广告风、胶片摄影风、宝丽来风、VHS 录像风、监控录像风、手持摄影风、鱼眼镜头风、微距摄影风、移轴摄影风、高速摄影风、长曝光风、黑白摄影风、黑色电影摄影、黄金时刻摄影、街头摄影风、建筑摄影风、奢侈品广告摄影、木刻版画风、浮世绘版画风、铜版画风、蚀刻版画风、旧书插图风、科学插图风、植物图谱风、动物图谱风、医学插图风、地图插画风、纸雕风格、剪纸风格、撕纸拼贴风、刺绣风格、编织风格、陶瓷釉面风、马赛克风格、彩色玻璃风、珐琅工艺风、漆器风格、金箔风格、铬金属风、液态金属风、全息镭射风、虹彩风格、透明塑料风、磨砂玻璃风、果冻质感、橡胶质感、充气塑料风、泡泡质感、粘液质感、粗颗粒质感、做旧质感、破损纹理、纸张纹理、布料纹理、大理石质感、混凝土质感、木纹质感、皮革质感、金箔质感、珠光质感、陶瓷质感、磨砂金属、拉丝金属、碳纤维质感、德式工业设计、包豪斯家具风、中世纪现代家具、北欧家具风、意大利现代家具、孟菲斯产品设计、太空时代设计、流线型现代风、复古电子产品风、透明科技产品风、苹果式产品设计、模块化产品设计、生物形态产品设计、软体家具风、奢侈品产品设计、可持续产品设计、现代建筑、极简建筑、国际主义建筑、粗野主义建筑、解构主义建筑、参数化建筑、未来主义建筑、高技派建筑、有机建筑、生物仿生建筑、北欧室内、日式现代室内、侘寂风室内、工业风室内、法式复古室内、意式现代室内、轻奢风室内、奶油风室内、地中海室内、摩洛哥室内、太空舱风、赛博朋克空间、有机未来主义空间、生态未来主义空间、高端奢侈品牌风、极简品牌风、现代科技品牌风、精品咖啡品牌风、手工品牌风、有机食品包装风、环保包装风、日式包装风、北欧包装风、复古食品包装风、复古药房包装风、美妆包装风、香水包装风、DTC 品牌风、潮牌视觉、运动品牌风、艺术品牌风、生活方式品牌风、1920 年代装饰艺术风、1930 年代流线型现代风、1950 年代复古风、1960 年代迷幻风、1970 年代复古风、1980 年代霓虹风、1990 年代杂志风、Y2K 风格、千禧辣妹风、复古未来主义、弗鲁蒂格水色美学、弗鲁蒂格都会风、赛博朋克、蒸汽朋克、柴油朋克、原子朋克、太阳朋克、蒸汽波、合成波、梦核、怪核、阈限空间、暗黑学院风、轻学院风、哥特风、黑色电影风、朋克风、滑板文化风、街头潮流风、可爱风、暗黑奇幻风、高级灰审美、多巴胺风格、乡村核、仙女核、恐怖可爱风、反乌托邦风、日式极简、日式禅意、侘寂美学、浮世绘风格、韩式极简、新中式、国潮风、中国水墨风、工笔画风、东方未来主义、唐风美学、宋风美学、明式家具风、敦煌风格、藏式装饰风、印度装饰风、摩洛哥装饰风、网格系统构图、中心构图、对称构图、不对称构图、放射状构图、对角线构图、大留白构图、满版构图、海报式构图、杂志版式、信息图构图、分屏构图、分镜构图、爆炸框构图、等距构图、鸟瞰构图、仰视构图、俯视构图、宽银幕构图、扁平化波普艺术、极简赛博朋克、瑞士波普海报、包豪斯波普海报、新艺术奢侈包装、日式侘寂极简、北欧极简、粗野主义奢侈品牌、赛博粗野主义、复古未来产品设计、Y2K 铬金属风、液态金属 Y2K、玻璃拟态科技 UI、黏土拟态 3D 图标、编辑拼贴风、朋克粗野主义海报、迷幻波普艺术、超现实极简海报、有机未来主义建筑、参数化奢华室内、生态未来主义设计、极简奢侈品牌风、高端科技极简、手绘极简、儿童书极简、拼贴波普、孟菲斯极简、国潮赛博风、水墨未来主义、奶油极简风、赛璐璐赛博朋克、赛璐璐波普艺术、复古日漫赛博、水彩新艺术、铬金属奢侈风、粗野主义 UI、液态玻璃 AI 产品风、低多边形生态未来、像素赛博朋克、玩具化奢侈品
```

---

# 二十、推荐的风格确认提示词模板

可以直接放到生图流程里：

```text
在生成图片前，请先从以下风格库中选择最适合的 1 个主风格、1 个表现技法、1 个媒介/材质风格、1 个构图方式，并说明选择理由。确认后再生成图片。

主风格可以来自：极简主义、波普艺术、包豪斯、瑞士国际主义平面风、装饰艺术、新艺术运动、赛博朋克、复古未来主义、Y2K、国潮风、日式极简、侘寂美学、粗野主义、孟菲斯风格等。

表现技法可以来自：赛璐璐风格、平涂风格、厚涂风格、水彩渲染、马克笔渲染、卡通渲染、非真实感渲染等。

媒介/材质可以来自：丝网印刷、Risograph、半调网点、铬金属、液态金属、玻璃拟态、纸张纹理、胶片颗粒等。

构图可以来自：网格系统构图、大留白构图、放射状构图、分镜构图、爆炸框构图、满版构图、对称构图等。
```

最实用的组合公式是：

```text
主风格 + 表现技法 + 材质/媒介 + 构图 + 色彩 + 光影
```

例如：

```text
波普艺术 + 赛璐璐风格 + 半调网点 + 爆炸框构图 + 高饱和红黄蓝 + 丝网印刷质感
```

---

## 后续拆分建议

这个库后续可以按用途拆成不同版本：

- 头像风格库
- 产品图风格库
- 海报风格库
- UI 风格库
- 包装风格库
- 建筑室内风格库
- 游戏角色风格库
- 摄影影像风格库
