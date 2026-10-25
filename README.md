# MHGU Tail Slam Fix (Hellblade Glavenus)

Monster Hunter Generations Ultimate 1.4.0

- Build ID: `FB08F1D20FD1204FE7070672777F869B`
- Title ID: `0100770008DD8000`

## 问题

60fps / 120fps 下，烬灭刃斩龙（Hellblade Glavenus）的**尾砸**判定窗口过短，容易漏判。

原因不是 hitbox 持续时间被简单减半，而是 30fps 的 **tick 量化**：

- 尾砸 hit 数据里 `+0x5c` 初始值为 `1.0`
- 30fps：`dt=2.0`，`1.0 / 2.0` 只够 **1 tick = 33ms**
- 60fps：`dt=1.0`，`1.0` 只有 **1 帧 = 16.7ms**
- 120fps：`dt=0.5`，`1.0` 只有 **2 帧 = 16.7ms**

所以 30fps 下判定窗口反而更宽，60/120fps 更容易漏。

## 修复

怪物攻击 hit 数据表里，尾砸记录：

```text
原：01 00 14 00 ...   ; +0x5c = 1.0, +0x60 = 20.0
改：02 00 14 00 ...   ; +0x5c = 2.0, +0x60 = 20.0
```

- 文件偏移：`0x17336BC`
- 原字节：`01 00`
- 改为：`02 00`
- 效果：`MhHitAtk + 0x5c` 初始值 `1.0 -> 2.0`
- 60/120fps 下判定窗口恢复到约 **33ms**，与 30fps 一致

## 安装

把补丁放到对应模拟器的 load 目录：

```text
exefs/FB08F1D20FD1204FE7070672777F869B.ips
```

Eden：

```text
<eden>/load/0100770008DD8000/TailSlamFix/exefs/FB08F1D20FD1204FE7070672777F869B.ips
```

Yuzu：

```text
<yuzu>/user/load/0100770008DD8000/TailSlamFix/exefs/FB08F1D20FD1204FE7070672777F869B.ips
```

然后**完全重启模拟器**。exefs 补丁只在启动时应用。

## 关闭

把 `TailSlamFix` 文件夹移出 load 目录，重启模拟器。

只删文件但不重启，补丁仍然留在当前运行的进程里。

## 格式

这是 **IPS32** 补丁：

```text
IPS32
offset 0x017336BC
size   0x0002
data   0x0002
EEOF
```

因为地址 `0x17336BC` 超过普通 IPS 的 16MB（3 字节偏移）上限，所以必须用 IPS32。

## 注意

- 只改了 `1 / 20` 这一条尾砸 hit 记录。如果其他难度或变种使用不同的 hit 数据记录，需要另外定位。
- 30fps 下 `2.0` 仍然只跑 1 tick（33ms），所以对 30fps 基本无副作用。
- 补丁不依赖 Forge，纯 exefs 数据修改。

## 工具

`tools/make_ips.py` 可以重新生成补丁，并校验 `main.bin` 的原始字节：

```bash
python tools/make_ips.py --main main.bin --out exefs/FB08F1D20FD1204FE7070672777F869B.ips
```
