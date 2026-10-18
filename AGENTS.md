本项目（homecad）主要记录个人 3D 参数化建模，供 FDM 打印的源代码。

项目偏好：
- 简单单文件
  - 默认不 check-in 测试文件
    - 如果用户显式要求 check-in 测试，首选 doctest，不用单独文件
  - 默认不 check-in 图片文件
    - 如果用户显式要求 check-in 某图片，用 optipng / webp 优化压缩
  - 说明简要放到 docstring，不用单独文件
    - 如果说明信息引用到 repo 外信息（比如 3D 扫描文件，参考图片），偏好将这些信息写在 commit message 而不是 docstring
    - 无需说明如何使用 b4dcad
  - 合理的时候，仍可 `import` 其他模型，比如我有时候会 `import` 为 3M Command Strip 设计的挂墙用薄板
  - 注释和文档可用中文
  - 不要修改 repo root 的 README.md
- 默认使用 b4dcad 建模
  - 见 ~/src/b4dcad/README.md
    - 若不存在，则让用户先准备好这个文件
  - 复杂部分仍可使用 cadquery
  - 旧代码仍使用 cadquery 和 cqutils，已不再是首选实践
- 3D 打印建模提醒
  - 如果壁太薄（比如 <0.5mm)，会被切片软件忽略，注意薄壁。
  - 如果有需要适配松紧，不确定具体参数的情况，可考虑使用省材料的 test fit rings 来测试。
